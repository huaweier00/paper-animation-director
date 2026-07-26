#!/usr/bin/env python3
"""Validate a paper-animation story manifest and report actionable findings."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VALID_ASPECTS = {"16:9", "9:16", "1:1", "4:5"}
VALID_SUBTITLES = {"none", "zh", "en", "zh-en", "source", "bilingual"}
VALID_AUDIO = {"dialogue-only", "full-mix", "stems", "silent"}


def finding(severity: str, path: str, message: str) -> dict[str, str]:
    return {"severity": severity, "path": path, "message": message}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_manifest(data: Any, project_dir: Path | None = None) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [finding("error", "$", "manifest root must be a JSON object")]

    project = data.get("project")
    if not nonempty(project):
        out.append(finding("error", "project", "project is required"))
    elif not ID_RE.match(project):
        out.append(finding("error", "project", "use lowercase letters, digits, and hyphens only"))

    if not nonempty(data.get("story")):
        out.append(finding("error", "story", "story is required"))
    if not nonempty(data.get("message")):
        out.append(finding("warning", "message", "record the intended takeaway or emotional destination"))

    aspect = data.get("aspect", "16:9")
    if aspect not in VALID_ASPECTS:
        out.append(finding("error", "aspect", f"expected one of {sorted(VALID_ASPECTS)}"))
    fps = data.get("fps", 30)
    if fps not in {24, 30, 60}:
        out.append(finding("error", "fps", "fps must be 24, 30, or 60"))
    if data.get("subtitle_mode", "zh") not in VALID_SUBTITLES:
        out.append(finding("error", "subtitle_mode", f"expected one of {sorted(VALID_SUBTITLES)}"))
    if data.get("audio_mode", "dialogue-only") not in VALID_AUDIO:
        out.append(finding("error", "audio_mode", f"expected one of {sorted(VALID_AUDIO)}"))

    characters = data.get("characters")
    character_ids: set[str] = set()
    if not isinstance(characters, list) or not characters:
        out.append(finding("error", "characters", "add at least one recurring character"))
        characters = []
    for index, char in enumerate(characters):
        base = f"characters[{index}]"
        if not isinstance(char, dict):
            out.append(finding("error", base, "character must be an object"))
            continue
        char_id = char.get("id")
        if not nonempty(char_id) or not ID_RE.match(char_id):
            out.append(finding("error", f"{base}.id", "use a non-empty kebab-case id"))
        elif char_id in character_ids:
            out.append(finding("error", f"{base}.id", f"duplicate character id {char_id!r}"))
        else:
            character_ids.add(char_id)
        if not nonempty(char.get("description")):
            out.append(finding("error", f"{base}.description", "describe stable identity and silhouette"))
        if not nonempty(char.get("identity_reference")):
            out.append(finding("warning", f"{base}.identity_reference", "add an approved identity-reference path"))
        elif project_dir and not (project_dir / char["identity_reference"]).exists():
            out.append(finding("warning", f"{base}.identity_reference", "referenced identity image does not exist yet"))
        poses = char.get("required_poses")
        if not isinstance(poses, list) or len(poses) < 4:
            out.append(finding("warning", f"{base}.required_poses", "define at least four observable pose states"))

    scenes = data.get("scenes")
    scene_ids: set[str] = set()
    if not isinstance(scenes, list) or not scenes:
        out.append(finding("error", "scenes", "add at least one scene"))
        scenes = []
    total_duration = 0.0
    for index, scene in enumerate(scenes):
        base = f"scenes[{index}]"
        if not isinstance(scene, dict):
            out.append(finding("error", base, "scene must be an object"))
            continue
        scene_id = scene.get("id")
        if not nonempty(scene_id) or not ID_RE.match(scene_id):
            out.append(finding("error", f"{base}.id", "use a non-empty kebab-case id"))
        elif scene_id in scene_ids:
            out.append(finding("error", f"{base}.id", f"duplicate scene id {scene_id!r}"))
        else:
            scene_ids.add(scene_id)
        if not nonempty(scene.get("narrative_goal")):
            out.append(finding("error", f"{base}.narrative_goal", "state what the audience must understand"))
        if not isinstance(scene.get("narration", ""), str):
            out.append(finding("error", f"{base}.narration", "narration must be a string"))
        duration = scene.get("duration")
        if not isinstance(duration, (int, float)) or duration <= 0:
            out.append(finding("error", f"{base}.duration", "provide a positive measured/planned duration"))
            duration_value = 0.0
        else:
            duration_value = float(duration)
            total_duration += duration_value

        layers = scene.get("layers")
        if not isinstance(layers, list) or len(layers) < 4:
            out.append(finding("warning", f"{base}.layers", "declare useful depth and physical layers; four is the minimum baseline"))

        events = scene.get("events")
        if not isinstance(events, list) or not events:
            out.append(finding("error", f"{base}.events", "add at least one cause/action/result/proof event"))
            events = []
        for event_index, event in enumerate(events):
            event_base = f"{base}.events[{event_index}]"
            if not isinstance(event, dict):
                out.append(finding("error", event_base, "event must be an object"))
                continue
            for key in ("cause", "action", "result", "proof"):
                if not nonempty(event.get(key)):
                    out.append(finding("error", f"{event_base}.{key}", f"{key} is required"))
            start = event.get("start")
            end = event.get("end")
            proof_time = event.get("proof_time")
            if start is not None and (not isinstance(start, (int, float)) or start < 0):
                out.append(finding("error", f"{event_base}.start", "start must be a non-negative scene-relative time"))
            if end is not None and (not isinstance(end, (int, float)) or end <= 0):
                out.append(finding("error", f"{event_base}.end", "end must be a positive scene-relative time"))
            if isinstance(start, (int, float)) and isinstance(end, (int, float)) and end <= start:
                out.append(finding("error", event_base, "event end must be after start"))
            if isinstance(end, (int, float)) and duration_value and end > duration_value + 1e-6:
                out.append(finding("error", f"{event_base}.end", "event exceeds scene duration"))
            if proof_time is None:
                out.append(finding("warning", f"{event_base}.proof_time", "add a review timestamp for the observable proof"))
            elif not isinstance(proof_time, (int, float)) or proof_time < 0 or (duration_value and proof_time > duration_value):
                out.append(finding("error", f"{event_base}.proof_time", "proof_time must fall inside the scene"))

        for ensemble_index, ensemble in enumerate(scene.get("ensemble_actions", [])):
            ens_base = f"{base}.ensemble_actions[{ensemble_index}]"
            if not isinstance(ensemble, dict):
                out.append(finding("error", ens_base, "ensemble action must be an object"))
                continue
            participants = ensemble.get("participants")
            if not isinstance(participants, list) or len(participants) < 2:
                out.append(finding("error", f"{ens_base}.participants", "connected ensemble actions require at least two participants"))
            else:
                for participant in participants:
                    if participant not in character_ids:
                        out.append(finding("error", f"{ens_base}.participants", f"unknown character id {participant!r}"))
            if ensemble.get("ensemble_required") is not True:
                out.append(finding("warning", f"{ens_base}.ensemble_required", "set true when actors share contact or load"))
            if not nonempty(ensemble.get("proof")):
                out.append(finding("error", f"{ens_base}.proof", "describe visible contact/load proof"))

    target = data.get("target_duration")
    if isinstance(target, (int, float)) and scenes and abs(total_duration - float(target)) > 0.05:
        out.append(finding("warning", "target_duration", f"scene durations total {total_duration:.3f}s, not {float(target):.3f}s"))

    delivery = data.get("delivery")
    if not isinstance(delivery, dict):
        out.append(finding("warning", "delivery", "declare master/social delivery requirements"))
    elif delivery.get("social_1080p") and float(delivery.get("social_vmaf_floor", 95)) < 93:
        out.append(finding("warning", "delivery.social_vmaf_floor", "use 95 or higher for a near-transparent social encode"))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read manifest: {exc}", file=sys.stderr)
        raise SystemExit(2)

    findings = validate_manifest(data, args.project_dir.resolve() if args.project_dir else None)
    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    payload = {"ok": errors == 0 and (warnings == 0 or not args.strict), "errors": errors, "warnings": warnings, "findings": findings}
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"[{item['severity'].upper()}] {item['path']}: {item['message']}")
        print(f"Manifest validation: {errors} error(s), {warnings} warning(s)")
    raise SystemExit(1 if errors or (args.strict and warnings) else 0)


if __name__ == "__main__":
    main()
