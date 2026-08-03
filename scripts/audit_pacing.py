#!/usr/bin/env python3
"""Audit narration gaps, scene tails, activity coverage, social hooks, and visual-beat density."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def merge_intervals(intervals: Iterable[tuple[float, float, str]]) -> list[tuple[float, float, set[str]]]:
    merged: list[tuple[float, float, set[str]]] = []
    for start, end, label in sorted(intervals, key=lambda item: (item[0], item[1])):
        if end <= start:
            continue
        if merged and start <= merged[-1][1] + 0.01:
            old_start, old_end, labels = merged[-1]
            merged[-1] = (old_start, max(old_end, end), labels | {label})
        else:
            merged.append((start, end, {label}))
    return merged


def gaps(duration: float, intervals: list[tuple[float, float, set[str]]]) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    cursor = 0.0
    for start, end, _ in intervals:
        if start > cursor:
            result.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < duration:
        result.append((cursor, duration))
    return result


def voice_lookup(path: Path | None) -> dict[str, dict]:
    if not path:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    lookup: dict[str, dict] = {}
    for item in data.get("items", []):
        file = str(item.get("file", ""))
        if file:
            lookup[file] = item
            lookup[Path(file).name] = item
    return lookup


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--voice-manifest", type=Path)
    parser.add_argument("--max-dead", type=float, default=1.2)
    parser.add_argument("--max-voice-gap", type=float, default=0.8)
    parser.add_argument("--max-visual-beat", type=float, default=3.0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    voices = voice_lookup(args.voice_manifest)
    findings: list[dict] = []
    rows: list[dict] = []
    voice_windows: list[tuple[float, float, str]] = []
    visual_beats_global: list[tuple[float, str, str]] = []
    global_start = 0.0

    for index, scene in enumerate(data.get("scenes", [])):
        scene_id = scene.get("id", f"scene-{index + 1}")
        duration = float(scene.get("duration", 0))
        intervals: list[tuple[float, float, str]] = []
        for window in scene.get("activity_windows", []):
            try:
                intervals.append((max(0, float(window["start"])), min(duration, float(window["end"])), str(window.get("type", "activity"))))
            except (KeyError, TypeError, ValueError):
                findings.append({"severity": "error", "scene": scene_id, "message": "invalid activity window"})
        for event in scene.get("events", []):
            if isinstance(event.get("start"), (int, float)) and isinstance(event.get("end"), (int, float)):
                intervals.append((max(0, float(event["start"])), min(duration, float(event["end"])), "event"))

        audio_file = scene.get("audio_file")
        audio_offset = float(scene.get("audio_offset", 0))
        voice_item = voices.get(str(audio_file)) or voices.get(Path(str(audio_file)).name) if audio_file else None
        audio_duration = scene.get("audio_duration")
        if audio_duration is None and voice_item:
            audio_duration = voice_item.get("duration")
        if audio_duration is not None:
            audio_duration = float(audio_duration)
            voice_end = min(duration, audio_offset + audio_duration)
            intervals.append((audio_offset, voice_end, "voice"))
            voice_windows.append((global_start + audio_offset, global_start + voice_end, scene_id))
            if duration - voice_end > args.max_dead:
                tail_activity = any(end > voice_end + 0.05 and label != "voice" for start, end, label in intervals)
                if not tail_activity:
                    findings.append({"severity": "warning", "scene": scene_id, "message": f"voice ends {duration - voice_end:.2f}s before scene end with no declared later activity"})
        elif scene.get("narration") and data.get("audio_mode") != "silent" and args.voice_manifest:
            findings.append({"severity": "warning", "scene": scene_id, "message": "narration has no matched audio duration"})

        merged = merge_intervals(intervals)
        dead = [(start, end) for start, end in gaps(duration, merged) if end - start > args.max_dead]
        for start, end in dead:
            findings.append({"severity": "warning", "scene": scene_id, "message": f"undeclared activity gap {start:.2f}–{end:.2f}s ({end - start:.2f}s)"})
        event_count = max(1, len(scene.get("events", [])))
        beat_span = duration / event_count if duration else 0
        if beat_span > args.max_visual_beat and not scene.get("activity_windows"):
            findings.append({"severity": "warning", "scene": scene_id, "message": f"average {beat_span:.2f}s per declared event; add internal visual beats or activity windows"})

        visual_beats = scene.get("visual_beats", [])
        beat_times: list[float] = []
        if isinstance(visual_beats, list):
            for beat in visual_beats:
                if not isinstance(beat, dict) or not isinstance(beat.get("time"), (int, float)):
                    continue
                beat_time = float(beat["time"])
                if 0 <= beat_time <= duration:
                    beat_times.append(beat_time)
                    visual_beats_global.append((global_start + beat_time, scene_id, str(beat.get("function", "beat"))))
        if beat_times:
            checkpoints = sorted(set(beat_times + [duration]))
            previous_time = 0.0
            for current_time in checkpoints:
                gap = current_time - previous_time
                if gap > args.max_visual_beat and not str(scene.get("long_hold_rationale", "")).strip():
                    findings.append(
                        {
                            "severity": "warning",
                            "scene": scene_id,
                            "message": f"visual-beat gap {previous_time:.2f}–{current_time:.2f}s ({gap:.2f}s) has no long_hold_rationale",
                        }
                    )
                previous_time = current_time
        rows.append({"id": scene_id, "start": global_start, "end": global_start + duration, "duration": duration, "events": len(scene.get("events", [])), "visual_beats": len(beat_times), "dead": dead})
        global_start += duration

    platform = data.get("platform", {})
    social_contract = data.get("social_contract", {})
    destination = str(platform.get("destination", "")).strip().lower() if isinstance(platform, dict) else ""
    if destination in {"douyin", "reels", "shorts", "social-feed"}:
        ordered_beats = sorted(visual_beats_global)
        if not ordered_beats:
            findings.append({"severity": "error", "scene": "global", "message": "social route has no declared visual_beats"})
        elif ordered_beats[0][0] > 0.1:
            findings.append({"severity": "error", "scene": ordered_beats[0][1], "message": f"first visual beat begins at {ordered_beats[0][0]:.2f}s; the feed-native first frame must already carry the event"})

        opening = social_contract.get("opening", {}) if isinstance(social_contract, dict) else {}
        proof_limit = opening.get("visual_proof_by", 3.0) if isinstance(opening, dict) else 3.0
        promise_proofs = [time for time, _scene, function in ordered_beats if function == "promise-proof"]
        if not any(time <= float(proof_limit) for time in promise_proofs):
            findings.append({"severity": "error", "scene": "global", "message": f"no promise-proof visual beat lands by {float(proof_limit):.2f}s"})

        value = social_contract.get("value", {}) if isinstance(social_contract, dict) else {}
        save_object = value.get("save_object", {}) if isinstance(value, dict) else {}
        hold = save_object.get("on_screen_hold") if isinstance(save_object, dict) else None
        save_beats = [time for time, _scene, function in ordered_beats if function == "save-object"]
        if isinstance(hold, (int, float)) and hold > 0:
            if not save_beats:
                findings.append({"severity": "error", "scene": "global", "message": "declared save object has no visual beat"})
            elif global_start - save_beats[-1] + 0.05 < float(hold):
                findings.append({"severity": "warning", "scene": "global", "message": f"save-object hold is {global_start - save_beats[-1]:.2f}s, shorter than declared {float(hold):.2f}s"})

    for previous, current in zip(voice_windows, voice_windows[1:]):
        gap = current[0] - previous[1]
        if gap > args.max_voice_gap:
            findings.append({"severity": "warning", "scene": current[2], "message": f"voice gap after {previous[2]} is {gap:.2f}s"})
        if gap < -0.7:
            findings.append({"severity": "warning", "scene": current[2], "message": f"voice overlaps previous scene by {-gap:.2f}s; confirm intentional J-cut"})

    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    lines = [
        "# Paper-animation pacing audit",
        "",
        f"- Total duration: {global_start:.3f}s",
        f"- Scenes: {len(rows)}",
        f"- Findings: {errors} error(s), {warnings} warning(s)",
        "",
        "## Scene timeline",
        "",
        "| Scene | Start | End | Duration | Events | Visual beats | Dead zones |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        dead_text = ", ".join(f"{start:.2f}–{end:.2f}" for start, end in row["dead"]) or "—"
        lines.append(f"| {row['id']} | {row['start']:.2f} | {row['end']:.2f} | {row['duration']:.2f} | {row['events']} | {row['visual_beats']} | {dead_text} |")
    lines.extend(["", "## Findings", ""])
    if findings:
        for item in findings:
            lines.append(f"- **{item['severity'].upper()} · {item['scene']}** — {item['message']}")
    else:
        lines.append("- No pacing findings.")
    rendered = "\n".join(lines) + "\n"
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Saved {output}")
    else:
        print(rendered, end="")
    raise SystemExit(1 if errors or (args.strict and warnings) else 0)


if __name__ == "__main__":
    main()
