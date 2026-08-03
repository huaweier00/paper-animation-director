#!/usr/bin/env python3
"""Audit planned and implemented paper-animation motion against observed asset facts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


FACING_X = {"left": -1.0, "right": 1.0, "front": 0.0}
LOCOMOTION = {"forward-travel", "backward-travel", "stationary"}
PHASES = {"planning", "implementation", "release"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} root must be an object")
    return data


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def project_path(project: Path, value: Any, label: str) -> Path:
    if not nonempty(value):
        raise ValueError(f"{label} must be a non-empty local path")
    raw = str(value)
    if raw.startswith(("http://", "https://", "//", "data:")):
        raise ValueError(f"{label} must be a local project path")
    project_root = project.resolve()
    candidate = (project_root / raw.removeprefix("./")).resolve()
    try:
        candidate.relative_to(project_root)
    except ValueError as exc:
        raise ValueError(f"{label} escapes the project root: {raw}") from exc
    return candidate


def point(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value)
        and all(0 <= float(item) <= 1 for item in value)
    )


def time_window(value: Any, duration: float) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value)
        and 0 <= float(value[0]) < float(value[1]) <= duration
    )


def validate_asset_facts(
    data: dict[str, Any],
    *,
    facts_path: Path,
    project: Path,
    phase: str,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    derived: dict[str, Any] = {"facts_path": str(facts_path)}

    if data.get("schema_version") != 1:
        errors.append("asset_facts.schema_version: expected 1")
    for field in ("asset_id", "identity_id", "file", "kind"):
        if not nonempty(data.get(field)):
            errors.append(f"asset_facts.{field}: required")

    facing = data.get("intrinsic_facing")
    if facing not in FACING_X:
        errors.append("asset_facts.intrinsic_facing: expected left, right, or front")
    forward_axis = data.get("forward_axis")
    if not (
        isinstance(forward_axis, list)
        and len(forward_axis) == 2
        and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in forward_axis)
        and math.hypot(float(forward_axis[0]), float(forward_axis[1])) > 0.5
    ):
        errors.append("asset_facts.forward_axis: provide a non-zero two-dimensional vector")
    elif facing in {"left", "right"} and math.copysign(1, float(forward_axis[0])) != math.copysign(1, FACING_X[facing]):
        errors.append("asset_facts.forward_axis: x direction contradicts intrinsic_facing")

    orientation = data.get("orientation_review")
    if not isinstance(orientation, dict):
        errors.append("asset_facts.orientation_review: required")
        orientation = {}
    if orientation.get("status") != "approved":
        errors.append("asset_facts.orientation_review.status: expected approved")
    for field in ("observed_head_side", "observed_chest_side", "observed_gaze", "reviewer", "evidence"):
        if not nonempty(orientation.get(field)):
            errors.append(f"asset_facts.orientation_review.{field}: required")
    if facing in {"left", "right"}:
        for field in ("observed_head_side", "observed_chest_side"):
            observed = orientation.get(field)
            if observed not in {facing, "not-applicable"}:
                errors.append(f"asset_facts.orientation_review.{field}: must agree with intrinsic_facing")

    mirror_policy = data.get("mirror_policy")
    if mirror_policy not in {"forbidden", "allowed-after-audit"}:
        errors.append("asset_facts.mirror_policy: expected forbidden or allowed-after-audit")
    mirror_audit = data.get("mirror_safety")
    if mirror_policy == "allowed-after-audit":
        required = (
            "costume_hair_asymmetry",
            "text_symbols",
            "handedness_held_objects",
            "light_shadow_direction",
            "contact_load_geometry",
            "adjacent_shot_continuity",
        )
        if not isinstance(mirror_audit, dict):
            errors.append("asset_facts.mirror_safety: required when mirroring may be allowed")
        else:
            for field in required:
                if mirror_audit.get(field) is not True:
                    errors.append(f"asset_facts.mirror_safety.{field}: expected true")

    declared_hash = data.get("sha256")
    if not isinstance(declared_hash, str) or not SHA256_RE.match(declared_hash):
        errors.append("asset_facts.sha256: expected a lowercase SHA-256 digest")
    try:
        media = project_path(project, data.get("file"), "asset_facts.file")
        evidence = project_path(project, orientation.get("evidence"), "asset_facts.orientation_review.evidence")
    except ValueError as exc:
        errors.append(str(exc))
        media = evidence = None
    if phase in {"implementation", "release"}:
        if media is not None and not media.is_file():
            errors.append(f"asset_facts.file: file does not exist: {media}")
        if evidence is not None and not evidence.is_file():
            errors.append(f"asset_facts.orientation_review.evidence: file does not exist: {evidence}")
    if media is not None and media.is_file() and isinstance(declared_hash, str) and SHA256_RE.match(declared_hash):
        observed_hash = sha256(media)
        derived["observed_sha256"] = observed_hash
        if observed_hash != declared_hash:
            errors.append("asset_facts.sha256: current media differs from the reviewed artifact")

    derived.update(
        {
            "asset_id": data.get("asset_id"),
            "intrinsic_facing": facing,
            "forward_axis": forward_axis,
            "mirror_policy": mirror_policy,
        }
    )
    return errors, warnings, derived


def audit_contract(
    data: dict[str, Any],
    *,
    contract_path: Path,
    project: Path,
    phase: str,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    derived_actors: list[dict[str, Any]] = []

    if data.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if not nonempty(data.get("shot_id")):
        errors.append("shot_id: required")
    duration_value = data.get("duration")
    if not isinstance(duration_value, (int, float)) or isinstance(duration_value, bool) or duration_value <= 0:
        errors.append("duration: expected a positive number")
        duration = 1.0
    else:
        duration = float(duration_value)
    frame = data.get("frame")
    if not isinstance(frame, dict):
        errors.append("frame: expected width and height")
        frame = {}
    for field in ("width", "height"):
        value = frame.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            errors.append(f"frame.{field}: expected a positive integer")

    actors = data.get("actors")
    if not isinstance(actors, list) or not actors:
        errors.append("actors: add at least one moving or explicitly stationary actor")
        actors = []
    seen: set[str] = set()
    for index, actor in enumerate(actors):
        base = f"actors[{index}]"
        if not isinstance(actor, dict):
            errors.append(f"{base}: expected an object")
            continue
        actor_id = actor.get("actor_id")
        if not nonempty(actor_id):
            errors.append(f"{base}.actor_id: required")
            continue
        if actor_id in seen:
            errors.append(f"{base}.actor_id: duplicate {actor_id!r}")
        seen.add(actor_id)

        expected_facing = actor.get("expected_facing")
        if expected_facing not in FACING_X:
            errors.append(f"{base}.expected_facing: expected left, right, or front")

        asset_status = actor.get("asset_status")
        if asset_status not in {"planned", "approved"}:
            errors.append(f"{base}.asset_status: expected planned or approved")
        facts_value = actor.get("asset_facts")
        asset_derived: dict[str, Any] = {}
        facts_path: Path | None = None
        if nonempty(facts_value):
            try:
                facts_path = project_path(project, facts_value, f"{base}.asset_facts")
            except ValueError as exc:
                errors.append(str(exc))
        else:
            errors.append(f"{base}.asset_facts: declare the intended asset-facts path")
        if phase in {"implementation", "release"} and asset_status != "approved":
            errors.append(f"{base}.asset_status: implementation/release requires approved")
        if facts_path and facts_path.is_file():
            try:
                facts = load_json(facts_path, f"{base} asset facts")
                facts_errors, facts_warnings, asset_derived = validate_asset_facts(
                    facts, facts_path=facts_path, project=project, phase=phase
                )
                errors.extend(f"{base}.{message}" for message in facts_errors)
                warnings.extend(f"{base}.{message}" for message in facts_warnings)
                if expected_facing in FACING_X and facts.get("intrinsic_facing") != expected_facing:
                    errors.append(f"{base}.expected_facing: approved asset facts disagree")
            except ValueError as exc:
                errors.append(str(exc))
        elif phase in {"implementation", "release"}:
            errors.append(f"{base}.asset_facts: file does not exist: {facts_path}")

        implementation = actor.get("implementation")
        if not isinstance(implementation, dict):
            errors.append(f"{base}.implementation: required")
            implementation = {}
        for field in ("engine", "selector", "source"):
            if not nonempty(implementation.get(field)):
                errors.append(f"{base}.implementation.{field}: required")
        if phase in {"implementation", "release"} and nonempty(implementation.get("source")):
            try:
                source = project_path(project, implementation["source"], f"{base}.implementation.source")
                if not source.is_file():
                    errors.append(f"{base}.implementation.source: file does not exist: {source}")
                else:
                    source_text = source.read_text(encoding="utf-8", errors="replace")
                    if nonempty(implementation.get("selector")) and implementation["selector"].lstrip("#.") not in source_text:
                        warnings.append(f"{base}.implementation.selector: selector token was not found in the source")
                    if "compiled-motion-track.json" not in source_text or "applyGsapMotion" not in source_text:
                        warnings.append(
                            f"{base}.implementation.source: use the compiled motion track and applyGsapMotion instead of retyping travel transforms"
                        )
            except ValueError as exc:
                errors.append(str(exc))

        active = actor.get("active")
        if not time_window(active, duration):
            errors.append(f"{base}.active: expected [start, end] inside the shot duration")
            active_start, active_end = 0.0, duration
        else:
            active_start, active_end = float(active[0]), float(active[1])
        start = actor.get("start")
        end = actor.get("end")
        if not point(start):
            errors.append(f"{base}.start: expected normalized [x, y]")
            start = [0.0, 0.0]
        if not point(end):
            errors.append(f"{base}.end: expected normalized [x, y]")
            end = [0.0, 0.0]
        dx = float(end[0]) - float(start[0])
        dy = float(end[1]) - float(start[1])
        distance = math.hypot(dx, dy)

        locomotion = actor.get("locomotion")
        if locomotion not in LOCOMOTION:
            errors.append(f"{base}.locomotion: expected one of {sorted(LOCOMOTION)}")
        transform = actor.get("instance_transform")
        if not isinstance(transform, dict):
            errors.append(f"{base}.instance_transform: required")
            transform = {}
        scale_x = transform.get("scale_x")
        if not isinstance(scale_x, (int, float)) or isinstance(scale_x, bool) or abs(float(scale_x)) < 0.001:
            errors.append(f"{base}.instance_transform.scale_x: expected a non-zero number")
            scale_x = 1.0
        rotation = transform.get("rotation_degrees")
        if not isinstance(rotation, (int, float)) or isinstance(rotation, bool):
            errors.append(f"{base}.instance_transform.rotation_degrees: expected a number")

        mirror = actor.get("mirror")
        if not isinstance(mirror, dict):
            errors.append(f"{base}.mirror: required")
            mirror = {}
        mirrored = float(scale_x) < 0
        if mirror.get("applied") is not mirrored:
            errors.append(f"{base}.mirror.applied: must equal whether scale_x is negative")
        if mirrored:
            policy = asset_derived.get("mirror_policy")
            if phase == "planning" and not asset_derived:
                policy = mirror.get("policy")
            if policy != "allowed-after-audit":
                errors.append(f"{base}.mirror: asset is not approved for mirroring")

        intrinsic = asset_derived.get("intrinsic_facing", expected_facing)
        intrinsic_x = FACING_X.get(intrinsic, 0.0)
        rendered_x = intrinsic_x * (-1.0 if mirrored else 1.0)
        rendered_facing = "front" if rendered_x == 0 else ("right" if rendered_x > 0 else "left")
        travel_direction = "stationary" if distance <= 0.01 else ("right" if dx > 0 else "left")
        alignment = 0.0 if distance <= 0.01 else rendered_x * dx / max(abs(dx), 1e-9)
        if locomotion == "stationary" and distance > 0.01:
            errors.append(f"{base}.locomotion: stationary conflicts with the start/end displacement")
        if locomotion in {"forward-travel", "backward-travel"} and distance <= 0.01:
            errors.append(f"{base}.locomotion: travel requires a material start/end displacement")
        if locomotion == "forward-travel" and alignment <= 0:
            errors.append(f"{base}: rendered facing conflicts with forward travel")
        if locomotion == "backward-travel":
            if alignment >= 0:
                errors.append(f"{base}: backward travel must visibly oppose rendered facing")
            if not nonempty(actor.get("exception_reason")):
                errors.append(f"{base}.exception_reason: explain the visible retreat")

        support = actor.get("support")
        if not isinstance(support, dict):
            errors.append(f"{base}.support: required")
            support = {}
        if support.get("mode") not in {"grounded", "airborne", "attached"}:
            errors.append(f"{base}.support.mode: expected grounded, airborne, or attached")
        if not nonempty(support.get("surface")):
            errors.append(f"{base}.support.surface: required")

        contact = actor.get("contact")
        if not isinstance(contact, dict):
            errors.append(f"{base}.contact: required")
            contact = {}
        contact_required = contact.get("required") is True
        if contact_required:
            if not nonempty(contact.get("target")):
                errors.append(f"{base}.contact.target: required")
            value = contact.get("time")
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not active_start <= float(value) <= active_end:
                errors.append(f"{base}.contact.time: expected a time inside the active interval")

        proof = actor.get("proof_times")
        if not isinstance(proof, dict):
            errors.append(f"{base}.proof_times: expected named proof times")
            proof = {}
        required_roles = {"entry", "midpoint", "exit"}
        if locomotion != "stationary":
            required_roles.update({"early", "late"})
        if contact_required:
            required_roles.update({"contact", "settle"})
        for role in sorted(required_roles):
            value = proof.get(role)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= float(value) <= duration:
                errors.append(f"{base}.proof_times.{role}: required inside shot duration")
        numeric_proof = [float(value) for value in proof.values() if isinstance(value, (int, float)) and not isinstance(value, bool)]
        if len(numeric_proof) != len(set(numeric_proof)):
            errors.append(f"{base}.proof_times: proof times must be unique")

        derived_actors.append(
            {
                "actor_id": actor_id,
                "selector": implementation.get("selector"),
                "engine": implementation.get("engine"),
                "asset_id": asset_derived.get("asset_id"),
                "intrinsic_facing": intrinsic,
                "rendered_facing": rendered_facing,
                "travel_direction": travel_direction,
                "alignment": alignment,
                "distance": round(distance, 8),
                "start": start,
                "end": end,
                "delta": [round(dx, 8), round(dy, 8)],
                "active": [active_start, active_end],
                "scale_x": float(scale_x),
                "proof_times": proof,
                "contact_required": contact_required,
                "asset_facts": asset_derived,
            }
        )

    return errors, warnings, {
        "shot_id": data.get("shot_id"),
        "duration": duration,
        "frame": frame,
        "contract": str(contract_path),
        "contract_sha256": sha256(contract_path) if contract_path.is_file() else None,
        "actors": derived_actors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--phase", choices=sorted(PHASES), default="planning")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    contract = args.contract.expanduser().resolve()
    project = args.project.expanduser().resolve()
    try:
        data = load_json(contract, "motion contract")
        errors, warnings, derived = audit_contract(
            data, contract_path=contract, project=project, phase=args.phase
        )
    except (OSError, ValueError) as exc:
        errors, warnings, derived = [str(exc)], [], {}
    result = {
        "ok": not errors and (not warnings or not args.strict),
        "phase": args.phase,
        "errors": errors,
        "warnings": warnings,
        "derived": derived,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("PASS: motion contract" if result["ok"] else "FAIL: motion contract")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
