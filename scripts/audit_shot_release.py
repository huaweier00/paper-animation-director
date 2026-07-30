#!/usr/bin/env python3
"""Validate that one rendered shot is ready to release before the next begins."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_CHECKS = (
    "muted_semantics",
    "required_nouns",
    "prop_realism",
    "support_grounding",
    "identity_continuity",
    "animation_responsibility",
    "voice_only",
    "combined_picture_sound_subtitles",
    "caption_safety",
    "rendered_mp4_frames",
    "technical_decode",
)

REQUIRED_FRAMES = ("first", "midpoint", "proof", "final")
PROP_FIELDS = (
    "id",
    "class",
    "silhouette",
    "scale_reference",
    "material_cues",
    "support_or_attachment",
    "state_sequence",
    "proof_time",
    "forbidden_substitutions",
)
LINE_FIELDS = ("id", "speaker", "text", "source", "start", "measured_duration")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_path(base: Path, value: Any) -> Path | None:
    if not nonempty(value):
        return None
    path = Path(value)
    return path if path.is_absolute() else base / path


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"record does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError("release record root must be an object")
    return data


def validate(
    data: dict[str, Any],
    base: Path,
    *,
    strict: bool,
    require_approved: bool,
    check_paths: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not nonempty(data.get("shot_id")):
        errors.append("shot_id: add a stable shot identifier")

    decision = data.get("decision")
    if decision not in {"approved", "rejected", "needs-fix"}:
        errors.append("decision: expected approved, rejected, or needs-fix")
    elif require_approved and decision != "approved":
        errors.append(f"decision: current shot is {decision!r}; next shot remains locked")

    rendered = resolve_path(base, data.get("rendered_mp4"))
    if rendered is None:
        errors.append("rendered_mp4: provide the rendered review MP4")
    elif check_paths and not rendered.is_file():
        errors.append(f"rendered_mp4: file does not exist: {rendered}")

    animation_decision = resolve_path(base, data.get("animation_decision"))
    if animation_decision is None:
        errors.append(
            "animation_decision: point to the reviewed animation-decision.json"
        )
    elif check_paths and not animation_decision.is_file():
        errors.append(
            f"animation_decision: file does not exist: {animation_decision}"
        )

    checks = data.get("checks")
    if not isinstance(checks, dict):
        errors.append("checks: expected an object")
        checks = {}
    for key in REQUIRED_CHECKS:
        status = checks.get(key)
        if status != "pass":
            errors.append(f"checks.{key}: expected pass, got {status!r}")

    frames = data.get("proof_frames")
    if not isinstance(frames, dict):
        errors.append("proof_frames: expected an object")
        frames = {}
    for key in REQUIRED_FRAMES:
        frame = resolve_path(base, frames.get(key))
        if frame is None:
            errors.append(f"proof_frames.{key}: provide a rendered-MP4 frame")
        elif check_paths and not frame.is_file():
            errors.append(f"proof_frames.{key}: file does not exist: {frame}")

    contact_required = bool(data.get("contact_required"))
    if contact_required:
        contact = resolve_path(base, frames.get("contact"))
        if contact is None:
            errors.append("proof_frames.contact: required for this contact shot")
        elif check_paths and not contact.is_file():
            errors.append(f"proof_frames.contact: file does not exist: {contact}")

    critical_props = data.get("critical_props", [])
    if not isinstance(critical_props, list):
        errors.append("critical_props: expected a list")
        critical_props = []
    for index, prop in enumerate(critical_props):
        base_key = f"critical_props[{index}]"
        if not isinstance(prop, dict):
            errors.append(f"{base_key}: expected an object")
            continue
        for field in PROP_FIELDS:
            value = prop.get(field)
            if field in {"state_sequence", "forbidden_substitutions"}:
                if not isinstance(value, list) or not value:
                    errors.append(f"{base_key}.{field}: expected a non-empty list")
            elif field == "proof_time":
                if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
                    errors.append(f"{base_key}.proof_time: expected a non-negative number")
            elif not nonempty(value):
                errors.append(f"{base_key}.{field}: required")
        if prop.get("recognizability_check") != "pass":
            errors.append(f"{base_key}.recognizability_check: expected pass")

    audio_required = data.get("audio_required", True)
    expected_lines = data.get("expected_lines", [])
    if not isinstance(expected_lines, list):
        errors.append("expected_lines: expected a list")
        expected_lines = []
    if audio_required and not expected_lines:
        errors.append("expected_lines: add all required narration/dialogue lines")
    for index, line in enumerate(expected_lines):
        base_key = f"expected_lines[{index}]"
        if not isinstance(line, dict):
            errors.append(f"{base_key}: expected an object")
            continue
        for field in LINE_FIELDS:
            value = line.get(field)
            if field in {"start", "measured_duration"}:
                if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
                    errors.append(f"{base_key}.{field}: expected a non-negative number")
            elif not nonempty(value):
                errors.append(f"{base_key}.{field}: required")
        source = resolve_path(base, line.get("source"))
        if source and check_paths and not source.is_file():
            errors.append(f"{base_key}.source: file does not exist: {source}")
        if line.get("audible_check") != "pass":
            errors.append(f"{base_key}.audible_check: expected pass")

    notes = data.get("review_notes")
    if not nonempty(notes):
        message = "review_notes: record the result and any intentional limitations"
        (errors if strict else warnings).append(message)

    if decision == "approved" and errors:
        errors.append("decision: cannot remain approved while release checks fail")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit one shot release record before beginning the next shot."
    )
    parser.add_argument("record", type=Path, help="Path to shot-release.json")
    parser.add_argument("--strict", action="store_true", help="Promote missing review notes to an error")
    parser.add_argument(
        "--allow-unapproved",
        action="store_true",
        help="Validate a rejected/needs-fix record without requiring approval",
    )
    parser.add_argument(
        "--skip-path-checks",
        action="store_true",
        help="Validate fields without checking referenced files",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    try:
        data = load_json(args.record)
        errors, warnings = validate(
            data,
            args.record.resolve().parent,
            strict=args.strict,
            require_approved=not args.allow_unapproved,
            check_paths=not args.skip_path_checks,
        )
    except ValueError as exc:
        errors, warnings = [str(exc)], []

    result = {
        "record": str(args.record),
        "approved": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("PASS: shot may be released" if not errors else "FAIL: next shot remains locked")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
