#!/usr/bin/env python3
"""Build a neutral HyperFrames timing skeleton from a creative or production manifest."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from validate_story_manifest import validate_manifest


ASPECT_SIZES = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080), "4:5": (1080, 1350)}


def fmt(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def hf_id(value: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", value.lower()).strip("-")


def replace_tokens(source: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        source = source.replace(f"__{key}__", value)
    return source


def validate_creative_manifest(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest: expected an object"]
    if not isinstance(data.get("project"), str) or not data["project"].strip():
        errors.append("project: provide a non-empty project id")
    if data.get("aspect", "16:9") not in ASPECT_SIZES:
        errors.append(f"aspect: expected one of {sorted(ASPECT_SIZES)}")
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("scenes: provide at least one scene")
        return errors
    seen: set[str] = set()
    for index, scene in enumerate(scenes):
        base = f"scenes[{index}]"
        if not isinstance(scene, dict):
            errors.append(f"{base}: expected an object")
            continue
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not scene_id.strip():
            errors.append(f"{base}.id: provide a non-empty id")
        elif scene_id in seen:
            errors.append(f"{base}.id: duplicate id {scene_id!r}")
        else:
            seen.add(scene_id)
        duration = scene.get("duration")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
            errors.append(f"{base}.duration: provide a positive number")
        responsibility = scene.get("responsibility") or scene.get("narrative_goal")
        if not isinstance(responsibility, str) or not responsibility.strip():
            errors.append(f"{base}.responsibility: state the scene's changed story state")
    return errors


def build(manifest_path: Path, project: Path, *, creative: bool = False) -> dict[str, float | int | str]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    findings = [] if creative else validate_manifest(data)
    errors = validate_creative_manifest(data) if creative else [
        f"{item['path']}: {item['message']}" for item in findings if item["severity"] == "error"
    ]
    if errors:
        message = "\n".join(errors)
        raise SystemExit(f"Manifest has blocking errors:\n{message}")

    skill_root = Path(__file__).resolve().parent.parent
    template_root = skill_root / "assets" / "project-template"
    index_template = (template_root / "index.html").read_text(encoding="utf-8")
    scene_template = (template_root / "compositions" / "scene-template.html").read_text(encoding="utf-8")
    width, height = ASPECT_SIZES[data.get("aspect", "16:9")]
    project.mkdir(parents=True, exist_ok=True)
    compositions = project / "compositions"
    compositions.mkdir(parents=True, exist_ok=True)

    hosts: list[str] = []
    captions: list[str] = []
    audio_tracks: list[str] = []
    timeline_lines: list[str] = []
    global_start = 0.0
    scene_starts: dict[str, float] = {}
    subtitle_mode = data.get("subtitle_mode", "zh")
    caption_size = max(28, round(width * 0.018))
    caption_en_size = max(18, round(caption_size * 0.68))

    for index, scene in enumerate(data["scenes"]):
        scene_id = hf_id(scene["id"])
        duration = float(scene["duration"])
        scene_starts[scene_id] = global_start
        title = scene.get("title") or scene_id.replace("-", " ").title()
        events = scene.get("events") if isinstance(scene.get("events"), list) else []
        first_event = events[0] if events and isinstance(events[0], dict) else {
            "start": min(1.0, duration * 0.2),
            "action": scene.get("action", "Block the decisive action"),
            "result": scene.get("result", "Show the changed story state"),
        }
        event_at = float(first_event.get("start", min(1.0, duration * 0.2)))
        event_at = min(max(event_at, 0.2), max(0.2, duration - 0.5))
        event_text = f"{first_event['action']} → {first_event['result']}"
        scene_html = replace_tokens(
            scene_template,
            {
                "SCENE_ID": scene_id,
                "WIDTH": str(width),
                "HEIGHT": str(height),
                "DURATION": fmt(duration),
                "SCENE_TITLE": html.escape(str(title)),
                "SCENE_GOAL": html.escape(str(scene.get("responsibility") or scene.get("narrative_goal"))),
                "EVENT_TEXT": html.escape(event_text),
                "EVENT_AT": fmt(event_at),
            },
        )
        if creative:
            scene_html = re.sub(
                r"\n  <script>\n    window\.__motionReady.*?\n  </script>",
                "",
                scene_html,
                flags=re.DOTALL,
            )
        (compositions / f"{scene_id}.html").write_text(scene_html, encoding="utf-8")
        assertions = [
            {"kind": "appearsBy", "selector": f"#{scene_id}-card", "bySec": min(0.7, duration * 0.25)},
            {"kind": "appearsBy", "selector": f"#{scene_id}-event", "bySec": min(duration - 0.1, event_at + 0.55)},
        ]
        if not creative:
            assertions.append(
                {"kind": "keepsMoving", "withinSelector": f"#{scene_id}", "maxStaticSec": min(2, max(0.8, duration * 0.35))}
            )
        motion = {
            "duration": duration,
            "assertions": assertions,
        }
        (compositions / f"{scene_id}.motion.json").write_text(json.dumps(motion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        hosts.append(
            f'      <div id="host-{scene_id}" data-hf-id="hf-host-{scene_id}" class="clip scene-host" '
            f'data-composition-id="{scene_id}" data-composition-src="compositions/{scene_id}.html" '
            f'data-start="{fmt(global_start)}" data-duration="{fmt(duration)}" data-track-index="1" '
            f'data-width="{width}" data-height="{height}" style="z-index:{index + 1}"></div>'
        )
        caption_id = f"caption-{index + 1:02d}"
        zh = html.escape(str(scene.get("narration", "")))
        en_text = scene.get("narration_en", "") if subtitle_mode in {"zh-en", "bilingual"} else ""
        en = f'<span class="caption-en">{html.escape(str(en_text))}</span>' if en_text else ""
        captions.append(
            f'          <div id="{caption_id}" data-hf-id="hf-{caption_id}" class="caption">'
            f'<span class="caption-zh">{zh}</span>{en}</div>'
        )
        caption_in = global_start + min(0.18, duration * 0.08)
        caption_out = global_start + max(0.2, duration - 0.12)
        timeline_lines.append(
            f'      tl.fromTo("#{caption_id}", {{ opacity: 0, y: 12 }}, '
            f'{{ opacity: 1, y: 0, duration: .24, ease: "power3.out" }}, {fmt(caption_in)});'
        )
        timeline_lines.append(
            f'      tl.to("#{caption_id}", {{ opacity: 0, y: -7, duration: .08, ease: "power2.in" }}, {fmt(caption_out)});'
        )

        audio_file = scene.get("audio_file")
        if audio_file:
            audio_offset = float(scene.get("audio_offset", 0))
            audio_duration = float(scene.get("audio_duration", max(0.1, duration - audio_offset)))
            audio_start = global_start + audio_offset
            audio_tracks.append(
                f'      <audio id="voice-{scene_id}" data-hf-id="hf-voice-{scene_id}" class="clip" '
                f'src="{html.escape(str(audio_file), quote=True)}" data-start="{fmt(audio_start)}" '
                f'data-duration="{fmt(audio_duration)}" data-track-index="10" data-volume="1"></audio>'
            )
        global_start += duration

    index_html = replace_tokens(
        index_template,
        {
            "PROJECT_ID": data["project"],
            "WIDTH": str(width),
            "HEIGHT": str(height),
            "DURATION": fmt(global_start),
            "CAPTION_SIZE": str(caption_size),
            "CAPTION_EN_SIZE": str(caption_en_size),
            "SCENE_HOSTS": "\n".join(hosts),
            "CAPTIONS": "\n".join(captions),
            "AUDIO_TRACKS": "\n".join(audio_tracks),
            "TIMELINE_JS": "\n".join(timeline_lines),
        },
    )
    (project / "index.html").write_text(index_html, encoding="utf-8")
    if not creative:
        index_motion = {
            "duration": global_start,
            "assertions": [{"kind": "keepsMoving", "withinSelector": "#root", "maxStaticSec": 2}],
        }
        (project / "index.motion.json").write_text(
            json.dumps(index_motion, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return {"project": data["project"], "width": width, "height": height, "duration": global_start, "scenes": len(data["scenes"])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--creative", action="store_true", help="Accept the lightweight creative manifest and do not require perpetual motion.")
    args = parser.parse_args()
    result = build(args.manifest.resolve(), args.project.resolve(), creative=args.creative)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
