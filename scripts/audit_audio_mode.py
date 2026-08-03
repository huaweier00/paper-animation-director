#!/usr/bin/env python3
"""Validate route-aware audio policy and confirm required streams in a rendered video."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from audit_medium_contract import load_json as load_medium_json
from audit_performance_contract import nonempty, project_path


MODES = {"full-performance", "dialogue-and-sound-design", "music-and-effects", "intentional-silent"}
PHASES = {"planning", "release"}


def load_json(path: Path, label: str = "audio contract") -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} root must be an object")
    return data


def probe_audio_streams(video: Path, ffprobe: str = "ffprobe") -> int:
    binary = shutil.which(ffprobe) if Path(ffprobe).name == ffprobe else ffprobe
    if not binary:
        raise ValueError("ffprobe is required to verify final audio streams")
    result = subprocess.run(
        [
            str(binary),
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "json",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "ffprobe could not inspect the video")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("ffprobe returned invalid JSON") from exc
    streams = data.get("streams", []) if isinstance(data, dict) else []
    return len(streams) if isinstance(streams, list) else 0


def validate_audio_contract(
    data: dict[str, Any],
    *,
    medium: dict[str, Any],
    phase: str = "planning",
    project: Path | None = None,
    video: Path | None = None,
    ffprobe: str = "ffprobe",
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    derived: dict[str, Any] = {}

    if data.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if not nonempty(data.get("project_id")):
        errors.append("project_id: required")
    route = data.get("medium_route")
    if route != medium.get("route"):
        errors.append("medium_route: must match medium-contract.json route")
    mode = data.get("mode")
    if mode not in MODES:
        errors.append(f"mode: expected one of {sorted(MODES)}")
    if data.get("status") not in {"draft", "approved", "rejected"}:
        errors.append("status: expected draft, approved, or rejected")
    elif phase == "release" and data.get("status") != "approved":
        errors.append("status: release requires approved")

    lines = data.get("expected_spoken_or_sung_lines")
    if not isinstance(lines, int) or isinstance(lines, bool) or lines < 0:
        errors.append("expected_spoken_or_sung_lines: expected a non-negative integer")
        lines = 0
    if mode in {"full-performance", "dialogue-and-sound-design"} and lines == 0:
        errors.append("expected_spoken_or_sung_lines: spoken/sung mode requires at least one expected line")
    if route == "shadow-theatre" and mode not in {"full-performance", "dialogue-and-sound-design"}:
        errors.append("mode: shadow-theatre requires full-performance or dialogue-and-sound-design")
    if mode == "intentional-silent" and not nonempty(data.get("intentional_silence_rationale")):
        errors.append("intentional_silence_rationale: silent mode requires a narrative and rhythmic rationale")

    expected = data.get("expected_in_master")
    if not isinstance(expected, list) or not expected or not all(nonempty(item) for item in expected):
        errors.append("expected_in_master: add the required final mix components")

    if phase == "release":
        if mode != "intentional-silent":
            if not nonempty(data.get("cue_ledger")):
                errors.append("cue_ledger: release requires a measured cue ledger")
            if lines > 0:
                stems = data.get("dry_stems")
                if not isinstance(stems, list) or not stems or not all(nonempty(item) for item in stems):
                    errors.append("dry_stems: expected spoken/sung lines require recoverable dry stems")
        if project is not None:
            path_fields = ["cue_ledger"] if nonempty(data.get("cue_ledger")) else []
            for field in path_fields:
                try:
                    path = project_path(project, data[field], field)
                except ValueError as exc:
                    errors.append(str(exc))
                else:
                    if not path.is_file():
                        errors.append(f"{field}: file does not exist: {path}")
            for field in ("dry_stems", "music_and_effect_stems"):
                values = data.get(field, [])
                if not isinstance(values, list):
                    continue
                for index, value in enumerate(values):
                    try:
                        path = project_path(project, value, f"{field}[{index}]")
                    except ValueError as exc:
                        errors.append(str(exc))
                    else:
                        if not path.is_file():
                            errors.append(f"{field}[{index}]: file does not exist: {path}")
        if video is None:
            errors.append("video: release requires the rendered master or shot video")
        elif not video.is_file():
            errors.append(f"video: file does not exist: {video}")
        else:
            try:
                stream_count = probe_audio_streams(video, ffprobe=ffprobe)
            except ValueError as exc:
                errors.append(f"video: {exc}")
            else:
                derived["audio_streams"] = stream_count
                if mode == "intentional-silent":
                    if stream_count:
                        warnings.append("video: intentional-silent mode contains an audio stream; confirm it is deliberate silence")
                elif stream_count < 1:
                    errors.append("video: declared audio mode requires at least one audio stream")

    approval = data.get("approval")
    if not isinstance(approval, dict):
        errors.append("approval: required object")
    elif phase == "release":
        for field in ("reviewer", "notes"):
            if not nonempty(approval.get(field)):
                errors.append(f"approval.{field}: release requires a value")

    return errors, warnings, derived


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--medium-contract", type=Path)
    parser.add_argument("--video", type=Path)
    parser.add_argument("--phase", choices=sorted(PHASES), default="release")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    medium_path = args.medium_contract.expanduser().resolve() if args.medium_contract else project / "medium-contract.json"
    video = args.video.expanduser().resolve() if args.video else None
    try:
        data = load_json(args.contract.expanduser().resolve())
        medium = load_medium_json(medium_path)
        errors, warnings, derived = validate_audio_contract(
            data, medium=medium, phase=args.phase, project=project, video=video, ffprobe=args.ffprobe
        )
    except (OSError, ValueError) as exc:
        errors, warnings, derived = [str(exc)], [], {}
    result = {"ok": not errors and (not warnings or not args.strict), "phase": args.phase, "errors": errors, "warnings": warnings, "derived": derived}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("PASS: audio mode" if result["ok"] else "FAIL: audio mode")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
