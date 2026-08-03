#!/usr/bin/env python3
"""Validate that one rendered shot is ready to release before the next begins."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from audit_engine_inputs import (
    find_project_root,
    load_json as load_engine_json,
    validate_engine_inputs,
)
from audit_rendered_motion import load as load_motion_review
from audit_rendered_motion import validate as validate_rendered_motion

BASE_REQUIRED_CHECKS = (
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
ROUTING_REQUIRED_CHECKS = ("engine_plan_fulfilled", "deterministic_seek")
MOTION_REQUIRED_CHECKS = ("motion_integrity",)
VISUAL_REQUIRED_CHECKS = (
    "art_direction_match",
    "focal_hierarchy",
    "value_separation",
    "palette_lighting_coherence",
    "character_environment_integration",
    "asset_finish",
    "phone_size_readability",
)
REQUIRED_CHECKS = (
    *BASE_REQUIRED_CHECKS,
    *ROUTING_REQUIRED_CHECKS,
    *VISUAL_REQUIRED_CHECKS,
    *MOTION_REQUIRED_CHECKS,
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
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_path(base: Path, value: Any) -> Path | None:
    if not nonempty(value):
        return None
    path = Path(value)
    return path if path.is_absolute() else base / path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bind_hash(
    errors: list[str],
    *,
    label: str,
    declared: Any,
    path: Path | None,
    check_paths: bool,
) -> None:
    if not isinstance(declared, str) or not SHA256_RE.match(declared):
        errors.append(f"{label}: expected a lowercase SHA-256 digest")
    elif check_paths and path is not None and path.is_file() and sha256(path) != declared:
        errors.append(f"{label}: evidence is stale because the bound file changed")


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

    schema_version = data.get("schema_version", 1)
    if schema_version not in {1, 2, 3, 4}:
        errors.append("schema_version: expected 1 (legacy), 2 (hybrid), 3 (premium visual), or 4 (motion-evidence release)")
    hybrid_release = schema_version in {2, 3, 4}
    premium_visual_release = schema_version in {3, 4}
    motion_evidence_release = schema_version == 4
    motion_required = data.get("motion_required") if motion_evidence_release else False
    if schema_version == 1:
        warnings.append(
            "schema_version: legacy v1 release; use v2 with shot_capabilities and "
            "engine_plan when this shot is revised"
        )
    elif schema_version == 2:
        warnings.append(
            "schema_version: v2 hybrid release has no premium visual-direction gate; "
            "use v3 when this shot is revised"
        )
    elif schema_version == 3:
        warnings.append(
            "schema_version: v3 premium visual release has no hash-bound rendered motion evidence; "
            "use v4 when this shot is revised"
        )
    elif not isinstance(motion_required, bool):
        errors.append("motion_required: schema v4 must explicitly declare true or false")
        motion_required = False

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
    if motion_evidence_release:
        bind_hash(
            errors,
            label="rendered_mp4_sha256",
            declared=data.get("rendered_mp4_sha256"),
            path=rendered,
            check_paths=check_paths,
        )

    required_records = {
        "animation_decision": "point to the reviewed animation-decision.json",
    }
    if hybrid_release:
        required_records.update(
            {
                "shot_capabilities": "point to the reviewed shot-capabilities.json",
                "engine_plan": "point to the generated and reviewed engine-plan.json",
                "engine_inputs": "point to the audited engine-inputs.json",
            }
        )
    if premium_visual_release:
        required_records["visual_direction_contract"] = (
            "point to the approved story manifest or visual-direction contract"
        )
    if motion_evidence_release and motion_required:
        required_records.update(
            {
                "motion_contract": "point to the audited motion-contract.json",
                "rendered_motion_review": "point to the approved hash-bound rendered-motion-review.json",
            }
        )
    resolved_records: dict[str, Path] = {}
    for field, guidance in required_records.items():
        record_path = resolve_path(base, data.get(field))
        if record_path is None:
            errors.append(f"{field}: {guidance}")
        elif check_paths and not record_path.is_file():
            errors.append(f"{field}: file does not exist: {record_path}")
        else:
            resolved_records[field] = record_path

    if motion_evidence_release:
        record_hashes = data.get("record_sha256")
        if not isinstance(record_hashes, dict):
            errors.append("record_sha256: bind every required upstream record")
            record_hashes = {}
        for field in required_records:
            bind_hash(
                errors,
                label=f"record_sha256.{field}",
                declared=record_hashes.get(field),
                path=resolved_records.get(field),
                check_paths=check_paths,
            )
        if check_paths:
            for field, record_path in resolved_records.items():
                if field == "visual_direction_contract" or not record_path.is_file():
                    continue
                try:
                    upstream = load_json(record_path)
                except ValueError as exc:
                    errors.append(f"{field}: {exc}")
                    continue
                if upstream.get("shot_id") != data.get("shot_id"):
                    errors.append(f"{field}.shot_id: must match the release shot_id")

    if (
        hybrid_release
        and check_paths
        and "engine_plan" in resolved_records
        and "engine_inputs" in resolved_records
        and resolved_records["engine_plan"].is_file()
        and resolved_records["engine_inputs"].is_file()
    ):
        try:
            engine_plan = load_engine_json(resolved_records["engine_plan"], "engine plan")
            engine_inputs = load_engine_json(resolved_records["engine_inputs"], "engine inputs")
            input_errors, input_warnings = validate_engine_inputs(
                engine_inputs,
                engine_plan,
                project_root=find_project_root(base),
                phase="release",
                check_paths=True,
            )
            errors.extend(f"engine_inputs_audit: {message}" for message in input_errors)
            warnings.extend(f"engine_inputs_audit: {message}" for message in input_warnings)
        except ValueError as exc:
            errors.append(f"engine_inputs_audit: {exc}")

    if motion_evidence_release and motion_required and check_paths and "rendered_motion_review" in resolved_records:
        review_path = resolved_records["rendered_motion_review"]
        if review_path.is_file():
            try:
                motion_errors, motion_warnings = validate_rendered_motion(
                    load_motion_review(review_path),
                    project=find_project_root(base),
                )
                errors.extend(f"rendered_motion_review: {message}" for message in motion_errors)
                warnings.extend(f"rendered_motion_review: {message}" for message in motion_warnings)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"rendered_motion_review: {exc}")

    checks = data.get("checks")
    if not isinstance(checks, dict):
        errors.append("checks: expected an object")
        checks = {}
    if motion_evidence_release and motion_required:
        required_checks = REQUIRED_CHECKS
    elif premium_visual_release:
        required_checks = (*BASE_REQUIRED_CHECKS, *ROUTING_REQUIRED_CHECKS, *VISUAL_REQUIRED_CHECKS)
    elif hybrid_release:
        required_checks = (*BASE_REQUIRED_CHECKS, *ROUTING_REQUIRED_CHECKS)
    else:
        required_checks = BASE_REQUIRED_CHECKS
    for key in required_checks:
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

    frame_hashes = data.get("proof_frame_sha256") if motion_evidence_release else {}
    if motion_evidence_release and not isinstance(frame_hashes, dict):
        errors.append("proof_frame_sha256: bind every required rendered proof frame")
        frame_hashes = {}
    if motion_evidence_release:
        for key in REQUIRED_FRAMES:
            bind_hash(
                errors,
                label=f"proof_frame_sha256.{key}",
                declared=frame_hashes.get(key),
                path=resolve_path(base, frames.get(key)),
                check_paths=check_paths,
            )

    contact_required = bool(data.get("contact_required"))
    if contact_required:
        contact = resolve_path(base, frames.get("contact"))
        if contact is None:
            errors.append("proof_frames.contact: required for this contact shot")
        elif check_paths and not contact.is_file():
            errors.append(f"proof_frames.contact: file does not exist: {contact}")
        if motion_evidence_release:
            bind_hash(
                errors,
                label="proof_frame_sha256.contact",
                declared=frame_hashes.get("contact"),
                path=contact,
                check_paths=check_paths,
            )

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
