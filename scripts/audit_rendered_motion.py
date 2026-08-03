#!/usr/bin/env python3
"""Audit rendered motion review evidence and reject stale or self-declared release records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from audit_motion_contract import audit_contract, load_json as load_motion_contract


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(project: Path, value: Any, label: str) -> Path | None:
    if not nonempty(value):
        return None
    project_root = project.resolve()
    path = (project_root / str(value).removeprefix("./")).resolve()
    try:
        path.relative_to(project_root)
    except ValueError as exc:
        raise ValueError(f"{label} escapes the project root") from exc
    return path


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("review root must be an object")
    return data


def validate(data: dict[str, Any], *, project: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if not nonempty(data.get("shot_id")):
        errors.append("shot_id: required")
    bindings = (
        ("motion_contract", "motion_contract_sha256"),
        ("rendered_mp4", "rendered_mp4_sha256"),
        ("contact_sheet", "contact_sheet_sha256"),
    )
    resolved_bindings: dict[str, Path] = {}
    for path_field, hash_field in bindings:
        try:
            path = resolve(project, data.get(path_field), path_field)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        declared = data.get(hash_field)
        if path is None:
            errors.append(f"{path_field}: required")
        elif not path.is_file():
            errors.append(f"{path_field}: file does not exist: {path}")
        elif not isinstance(declared, str) or not SHA256_RE.match(declared):
            errors.append(f"{hash_field}: expected a SHA-256 digest")
        elif sha256(path) != declared:
            errors.append(f"{hash_field}: evidence is stale because the file changed")
        else:
            resolved_bindings[path_field] = path

    expected_actors: dict[str, dict[str, Any]] = {}
    contract_path = resolved_bindings.get("motion_contract")
    if contract_path is not None:
        try:
            contract_data = load_motion_contract(contract_path, "motion contract")
            contract_errors, contract_warnings, derived = audit_contract(
                contract_data,
                contract_path=contract_path,
                project=project,
                phase="release",
            )
            errors.extend(f"motion_contract: {message}" for message in contract_errors)
            warnings.extend(f"motion_contract: {message}" for message in contract_warnings)
            if derived.get("shot_id") != data.get("shot_id"):
                errors.append("shot_id: rendered review must match its motion contract")
            expected_actors = {
                actor["actor_id"]: actor
                for actor in derived.get("actors", [])
                if isinstance(actor, dict) and isinstance(actor.get("actor_id"), str)
            }
        except (OSError, ValueError) as exc:
            errors.append(f"motion_contract: {exc}")

    frames = data.get("evidence_frames")
    if not isinstance(frames, list) or len(frames) < 3:
        errors.append("evidence_frames: expected at least three rendered frames")
        frames = []
    seen_times: set[float] = set()
    for index, frame in enumerate(frames):
        base = f"evidence_frames[{index}]"
        if not isinstance(frame, dict):
            errors.append(f"{base}: expected an object")
            continue
        if not nonempty(frame.get("label")):
            errors.append(f"{base}.label: required")
        value = frame.get("time")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            errors.append(f"{base}.time: expected a non-negative number")
        elif float(value) in seen_times:
            errors.append(f"{base}.time: duplicate proof time")
        else:
            seen_times.add(float(value))
        try:
            path = resolve(project, frame.get("path"), f"{base}.path")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        declared = frame.get("sha256")
        if path is None or not path.is_file():
            errors.append(f"{base}.path: evidence frame is missing")
        elif not isinstance(declared, str) or not SHA256_RE.match(declared):
            errors.append(f"{base}.sha256: expected a SHA-256 digest")
        elif sha256(path) != declared:
            errors.append(f"{base}.sha256: frame changed after review package creation")

    actors = data.get("actors")
    if not isinstance(actors, list) or not actors:
        errors.append("actors: add rendered review results")
        actors = []
    reviewed_actor_ids: set[str] = set()
    for index, actor in enumerate(actors):
        base = f"actors[{index}]"
        if not isinstance(actor, dict):
            errors.append(f"{base}: expected an object")
            continue
        if not nonempty(actor.get("actor_id")):
            errors.append(f"{base}.actor_id: required")
            actor_id = ""
        else:
            actor_id = str(actor["actor_id"])
            reviewed_actor_ids.add(actor_id)
        expected = expected_actors.get(actor_id)
        if expected is None and expected_actors:
            errors.append(f"{base}.actor_id: not present in the bound motion contract")
        elif expected is not None:
            if actor.get("expected_rendered_facing") != expected.get("rendered_facing"):
                errors.append(f"{base}.expected_rendered_facing: must match the bound motion contract")
            if actor.get("expected_travel_direction") != expected.get("travel_direction"):
                errors.append(f"{base}.expected_travel_direction: must match the bound motion contract")
        required = actor.get("required_checks")
        observed = actor.get("observed")
        if not isinstance(required, dict) or not isinstance(observed, dict):
            errors.append(f"{base}: required_checks and observed are required")
            continue
        for check, enabled in required.items():
            if enabled is True and observed.get(check) != "pass":
                errors.append(f"{base}.observed.{check}: expected pass")
            if enabled is False and observed.get(check) not in {"not-required", "pass"}:
                errors.append(f"{base}.observed.{check}: expected not-required or pass")
        if actor.get("decision") != "approved":
            errors.append(f"{base}.decision: expected approved")
        if not nonempty(actor.get("review_notes")):
            errors.append(f"{base}.review_notes: explain the observed rendered result")

    missing_actors = sorted(set(expected_actors) - reviewed_actor_ids)
    if missing_actors:
        errors.append(f"actors: missing bound motion-contract actors: {', '.join(missing_actors)}")

    if data.get("decision") != "approved":
        errors.append("decision: expected approved")
    if not nonempty(data.get("review_notes")):
        errors.append("review_notes: required")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    review = args.review.expanduser().resolve()
    project = args.project.expanduser().resolve()
    try:
        errors, warnings = validate(load(review), project=project)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors, warnings = [str(exc)], []
    result = {
        "ok": not errors and (not warnings or not args.strict),
        "errors": errors,
        "warnings": warnings,
        "review": str(review),
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("PASS: rendered motion" if result["ok"] else "FAIL: rendered motion")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
