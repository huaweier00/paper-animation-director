#!/usr/bin/env python3
"""Bind a schema-v4 shot release record to the exact records, render, and proof frames."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


RECORD_FIELDS = (
    "animation_decision",
    "shot_capabilities",
    "engine_plan",
    "engine_inputs",
    "visual_direction_contract",
    "motion_contract",
    "rendered_motion_review",
)
FRAME_FIELDS = ("first", "midpoint", "contact", "proof", "final")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve(base: Path, value: Any, field: str) -> Path:
    if not nonempty(value):
        raise ValueError(f"{field}: missing path")
    path = Path(str(value))
    return path if path.is_absolute() else (base / path).resolve()


def sha256(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"file does not exist: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bind(data: dict[str, Any], *, base: Path) -> dict[str, Any]:
    if data.get("schema_version") != 4:
        raise ValueError("evidence binding requires shot-release schema_version 4")
    rendered = resolve(base, data.get("rendered_mp4"), "rendered_mp4")
    data["rendered_mp4_sha256"] = sha256(rendered)

    record_hashes: dict[str, str] = {}
    for field in RECORD_FIELDS:
        if data.get("motion_required") is False and field in {"motion_contract", "rendered_motion_review"}:
            continue
        if nonempty(data.get(field)):
            record_hashes[field] = sha256(resolve(base, data[field], field))
    data["record_sha256"] = record_hashes

    frames = data.get("proof_frames")
    if not isinstance(frames, dict):
        raise ValueError("proof_frames: expected an object")
    required_frames = ["first", "midpoint", "proof", "final"]
    if data.get("contact_required") is True:
        required_frames.append("contact")
    data["proof_frame_sha256"] = {
        field: sha256(resolve(base, frames.get(field), f"proof_frames.{field}"))
        for field in required_frames
    }
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, help="defaults to updating the release record")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    release = args.release.expanduser().resolve()
    output = args.output.expanduser().resolve() if args.output else release
    try:
        data = json.loads(release.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("release record root must be an object")
        bound = bind(data, base=release.parent)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(bound, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = {"ok": True, "output": str(output)}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"ok": False, "error": str(exc)}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"PASS: bound {result['output']}" if result["ok"] else f"FAIL: {result['error']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
