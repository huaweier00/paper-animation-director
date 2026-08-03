#!/usr/bin/env python3
"""Validate that a shot has actor performance rather than presentation-only motion."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from audit_medium_contract import load_json as load_medium_json
from audit_medium_contract import validate_medium_contract


PHASES = {"planning", "implementation", "release"}
ACTIVE_MODES = {
    "articulated-rig",
    "pose-replacement",
    "connected-ensemble",
    "full-scene-state",
    "selective-local-motion",
}
ALL_MODES = ACTIVE_MODES | {"deliberate-still"}
PRESENTATION_CHANNELS = {
    "root-x",
    "root-y",
    "root-translation",
    "root-rotation",
    "root-scale",
    "opacity",
    "camera",
    "background",
    "particles",
    "surface",
    "text",
    "caption",
}
PERFORMANCE_CHANNEL_MARKERS = {
    "local",
    "joint",
    "limb",
    "head",
    "torso",
    "hand",
    "arm",
    "leg",
    "foot",
    "beak",
    "wing",
    "pose-replacement",
    "complete-pose",
    "state",
    "ensemble",
    "articulated",
    "control",
}
ACTION_PHASES = {"primary-action", "contact", "change", "exact-hold", "substitution"}
RESULT_PHASES = {"settle", "reaction", "recovery", "result", "exact-hold"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_json(path: Path, label: str = "performance contract") -> dict[str, Any]:
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
        raise ValueError(f"{label}: expected a local project path")
    raw = str(value)
    if raw.startswith(("http://", "https://", "//", "data:")):
        raise ValueError(f"{label}: runtime-network paths are forbidden")
    root = project.resolve()
    path = (root / raw.removeprefix("./")).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label}: path escapes the project root") from exc
    return path


def _earned_stillness_errors(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["earned_stillness: deliberate stillness requires an evidence object"]
    for field in ("prior_cause", "present_read", "tension_support", "why_motion_weakens", "exit_condition"):
        if not nonempty(value.get(field)):
            errors.append(f"earned_stillness.{field}: required")
    return errors


def _phase_time(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and float(value) >= 0


def is_performance_channel(value: str) -> bool:
    normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
    if normalized in PRESENTATION_CHANNELS:
        return False
    if any(
        phrase in normalized
        for phrase in (
            "root-only",
            "root-transform-only",
            "presentation-only",
            "whole-image",
            "whole-actor",
        )
    ):
        return False
    return any(marker in normalized for marker in PERFORMANCE_CHANNEL_MARKERS)


def validate_performance_contract(
    data: dict[str, Any],
    *,
    medium: dict[str, Any],
    phase: str = "planning",
    project: Path | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if phase not in PHASES:
        errors.append(f"phase: expected one of {sorted(PHASES)}")
    medium_errors, medium_warnings = validate_medium_contract(
        medium, phase="release" if phase == "release" else "planning"
    )
    errors.extend(f"medium_contract.{item}" for item in medium_errors)
    warnings.extend(f"medium_contract.{item}" for item in medium_warnings)

    if data.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if not nonempty(data.get("shot_id")):
        errors.append("shot_id: required")
    route = data.get("medium_route")
    if route != medium.get("route"):
        errors.append("medium_route: must match medium-contract.json route")
    if not nonempty(data.get("responsibility")):
        errors.append("responsibility: required")
    motion_required = data.get("motion_required")
    if not isinstance(motion_required, bool):
        errors.append("motion_required: expected true or false")
        motion_required = True
    if data.get("presentation_motion_is_not_proof") is not True:
        errors.append("presentation_motion_is_not_proof: expected true")

    allowed_modes = set(medium.get("performance_policy", {}).get("allowed_modes", []))
    actors = data.get("actors")
    if not isinstance(actors, list):
        errors.append("actors: expected a list")
        actors = []
    if motion_required and not actors:
        errors.append("actors: action-bearing shot requires at least one performer")

    shot_phase_names: set[str] = set()
    asset_actor_pairs: set[tuple[str, str]] = set()
    for index, actor in enumerate(actors):
        prefix = f"actors[{index}]"
        if not isinstance(actor, dict):
            errors.append(f"{prefix}: expected object")
            continue
        for field in ("actor_id", "objective", "initial_attention", "final_attention", "lead_control", "support"):
            if not nonempty(actor.get(field)):
                errors.append(f"{prefix}.{field}: required")
        mode = actor.get("performance_mode")
        if mode not in ALL_MODES:
            errors.append(f"{prefix}.performance_mode: expected one of {sorted(ALL_MODES)}")
        elif allowed_modes and mode not in allowed_modes:
            errors.append(f"{prefix}.performance_mode: {mode!r} is not allowed by the selected medium")
        if motion_required and mode == "deliberate-still":
            warnings.append(f"{prefix}.performance_mode: still performer inside motion-required shot needs a reacting active performer")

        phases = actor.get("phases")
        if not isinstance(phases, list) or not phases:
            errors.append(f"{prefix}.phases: add observable performance phases")
            phases = []
        actor_times: list[float] = []
        local_channel_found = False
        for phase_index, item in enumerate(phases):
            phase_prefix = f"{prefix}.phases[{phase_index}]"
            if not isinstance(item, dict):
                errors.append(f"{phase_prefix}: expected object")
                continue
            name = item.get("name")
            if not nonempty(name):
                errors.append(f"{phase_prefix}.name: required")
            else:
                shot_phase_names.add(name)
            if not _phase_time(item.get("time")):
                errors.append(f"{phase_prefix}.time: expected a non-negative number")
            else:
                actor_times.append(float(item["time"]))
            if not nonempty(item.get("visible_change")):
                errors.append(f"{phase_prefix}.visible_change: required")
            channel = item.get("channel")
            if not nonempty(channel):
                errors.append(f"{phase_prefix}.channel: required")
            else:
                if is_performance_channel(str(channel)):
                    local_channel_found = True
        if actor_times != sorted(actor_times):
            errors.append(f"{prefix}.phases: times must be ordered")
        if motion_required and mode in ACTIVE_MODES and not local_channel_found:
            errors.append(f"{prefix}.phases: active performer has only presentation/root channels")

        asset = actor.get("production_asset")
        if not isinstance(asset, dict):
            errors.append(f"{prefix}.production_asset: required object")
            asset = {}
        if not nonempty(asset.get("asset_id")):
            errors.append(f"{prefix}.production_asset.asset_id: required")
        asset_status = asset.get("status", "approved" if SHA256_RE.match(str(asset.get("sha256", ""))) else "planned")
        if asset_status not in {"planned", "approved", "rejected"}:
            errors.append(f"{prefix}.production_asset.status: expected planned, approved, or rejected")
        if phase == "release":
            if asset_status != "approved":
                errors.append(f"{prefix}.production_asset.status: release requires approved")
            if not isinstance(asset.get("sha256"), str) or not SHA256_RE.match(asset["sha256"]):
                errors.append(f"{prefix}.production_asset.sha256: release requires a lowercase SHA-256")
            if not nonempty(asset.get("performance_state")):
                errors.append(f"{prefix}.production_asset.performance_state: release requires an authored state")
        actor_id = actor.get("actor_id")
        asset_id = asset.get("asset_id")
        if nonempty(actor_id) and nonempty(asset_id):
            pair = (str(actor_id), str(asset_id))
            if pair in asset_actor_pairs:
                errors.append(f"{prefix}.production_asset.asset_id: duplicate actor asset use inside one shot")
            asset_actor_pairs.add(pair)

    if motion_required:
        if not ACTION_PHASES.intersection(shot_phase_names):
            errors.append("actors.phases: action-bearing shot needs a primary action/contact/change/hold/substitution phase")
        if not RESULT_PHASES.intersection(shot_phase_names):
            errors.append("actors.phases: action-bearing shot needs a settle/reaction/recovery/result/hold phase")
    else:
        errors.extend(_earned_stillness_errors(data.get("earned_stillness")))
        if actors and any(actor.get("performance_mode") != "deliberate-still" for actor in actors if isinstance(actor, dict)):
            errors.append("actors: motion_required false permits only deliberate-still performer modes")

    sound_cues = data.get("sound_cues")
    if not isinstance(sound_cues, list):
        errors.append("sound_cues: expected a list")
        sound_cues = []
    if route == "shadow-theatre" and motion_required and not sound_cues:
        errors.append("sound_cues: shadow-theatre action requires sound-linked performance cues")
    cue_ids: set[str] = set()
    for index, cue in enumerate(sound_cues):
        prefix = f"sound_cues[{index}]"
        if not isinstance(cue, dict):
            errors.append(f"{prefix}: expected object")
            continue
        for field in ("id", "type", "binds_to"):
            if not nonempty(cue.get(field)):
                errors.append(f"{prefix}.{field}: required")
        if not _phase_time(cue.get("time")):
            errors.append(f"{prefix}.time: expected a non-negative number")
        if nonempty(cue.get("id")):
            if cue["id"] in cue_ids:
                errors.append(f"{prefix}.id: duplicate cue id")
            cue_ids.add(cue["id"])

    if phase == "release":
        review = data.get("rendered_review")
        if not isinstance(review, dict):
            errors.append("rendered_review: release requires an evidence object")
            review = {}
        if review.get("status") != "approved":
            errors.append("rendered_review.status: release requires approved")
        for field in ("video", "reviewer", "notes"):
            if not nonempty(review.get(field)):
                errors.append(f"rendered_review.{field}: required")
        observed = review.get("observed_performance")
        if not isinstance(observed, list) or not observed or not all(nonempty(item) for item in observed):
            errors.append("rendered_review.observed_performance: add observed rendered evidence")
        digest = review.get("video_sha256")
        if not isinstance(digest, str) or not SHA256_RE.match(digest):
            errors.append("rendered_review.video_sha256: expected a lowercase SHA-256")
        if project is not None and nonempty(review.get("video")):
            try:
                video = project_path(project, review["video"], "rendered_review.video")
            except ValueError as exc:
                errors.append(str(exc))
            else:
                if not video.is_file():
                    errors.append(f"rendered_review.video: file does not exist: {video}")
                elif isinstance(digest, str) and SHA256_RE.match(digest) and sha256(video) != digest:
                    errors.append("rendered_review.video_sha256: evidence is stale because the video changed")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--medium-contract", required=True, type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--phase", choices=sorted(PHASES), default="planning")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    project = args.project.expanduser().resolve() if args.project else None
    try:
        data = load_json(args.contract.expanduser().resolve())
        medium = load_medium_json(args.medium_contract.expanduser().resolve())
        errors, warnings = validate_performance_contract(data, medium=medium, phase=args.phase, project=project)
    except (OSError, ValueError) as exc:
        errors, warnings = [str(exc)], []
    result = {"ok": not errors and (not warnings or not args.strict), "phase": args.phase, "errors": errors, "warnings": warnings}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("PASS: performance contract" if result["ok"] else "FAIL: performance contract")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
