#!/usr/bin/env python3
"""Validate a paper-animation medium contract before production or release."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROUTES = {"shadow-theatre", "cutout-paper", "painterly-limited"}
PHASES = {"planning", "production", "release"}
PERFORMANCE_MODES = {
    "articulated-rig",
    "pose-replacement",
    "connected-ensemble",
    "full-scene-state",
    "selective-local-motion",
    "deliberate-still",
}
BASE_FORBIDDEN = {
    "root-transform-as-hero-acting",
    "camera-motion-as-action-proof",
    "surface-texture-as-material-proof",
    "same-pose-across-incompatible-intentions",
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_json(path: Path, label: str = "medium contract") -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} root must be an object")
    return data


def _required_text(errors: list[str], obj: dict[str, Any], prefix: str, fields: tuple[str, ...]) -> None:
    for field in fields:
        if not nonempty(obj.get(field)):
            errors.append(f"{prefix}.{field}: required")


def validate_medium_contract(
    data: dict[str, Any], *, phase: str = "planning"
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if phase not in PHASES:
        errors.append(f"phase: expected one of {sorted(PHASES)}")
    if data.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if not nonempty(data.get("project_id")):
        errors.append("project_id: required")
    route = data.get("route")
    if route not in ROUTES:
        errors.append(f"route: expected one of {sorted(ROUTES)}")
    status = data.get("status")
    if status not in {"draft", "approved", "rejected"}:
        errors.append("status: expected draft, approved, or rejected")
    elif phase in {"production", "release"} and status != "approved":
        errors.append(f"status: {phase} requires approved")

    truth = data.get("medium_truth")
    if not isinstance(truth, dict):
        errors.append("medium_truth: required object")
        truth = {}
    _required_text(errors, truth, "medium_truth", ("material", "performer", "space", "light", "sound"))

    policy = data.get("performance_policy")
    if not isinstance(policy, dict):
        errors.append("performance_policy: required object")
        policy = {}
    for field in (
        "actor_internal_change_required",
        "presentation_only_not_action_proof",
        "earned_stillness_required",
        "pose_reuse_requires_compatible_intent",
    ):
        if policy.get(field) is not True:
            errors.append(f"performance_policy.{field}: expected true")
    allowed_modes = policy.get("allowed_modes")
    if not isinstance(allowed_modes, list) or not allowed_modes:
        errors.append("performance_policy.allowed_modes: add at least one route-capable mode")
        allowed_modes = []
    else:
        invalid = sorted({item for item in allowed_modes if item not in PERFORMANCE_MODES})
        if invalid:
            errors.append(f"performance_policy.allowed_modes: invalid modes {invalid}")
        if all(item == "deliberate-still" for item in allowed_modes):
            errors.append("performance_policy.allowed_modes: route must support an active performance mode")

    forbidden = data.get("forbidden_shortcuts")
    if not isinstance(forbidden, list) or not all(nonempty(item) for item in forbidden):
        errors.append("forbidden_shortcuts: expected a non-empty string list")
        forbidden_set: set[str] = set()
    else:
        forbidden_set = set(forbidden)
        missing = sorted(BASE_FORBIDDEN - forbidden_set)
        if missing:
            errors.append(f"forbidden_shortcuts: missing core bans {missing}")

    if route == "shadow-theatre":
        shadow = data.get("shadow_theatre")
        if not isinstance(shadow, dict):
            errors.append("shadow_theatre: route requires a route-specific object")
            shadow = {}
        screen = shadow.get("screen") if isinstance(shadow.get("screen"), dict) else {}
        if screen.get("type") != "rear-lit-translucent":
            errors.append("shadow_theatre.screen.type: expected rear-lit-translucent")
        for field in ("transmitted_light", "screen_plane_required", "performer_distance_affects_projection"):
            if screen.get(field) is not True:
                errors.append(f"shadow_theatre.screen.{field}: expected true")
        articulation = shadow.get("articulation") if isinstance(shadow.get("articulation"), dict) else {}
        if articulation.get("required") is not True:
            errors.append("shadow_theatre.articulation.required: expected true")
        if articulation.get("puppet_model_required") is not True:
            errors.append("shadow_theatre.articulation.puppet_model_required: expected true")
        if not nonempty(articulation.get("control_logic")):
            errors.append("shadow_theatre.articulation.control_logic: required")
        audio = shadow.get("audio") if isinstance(shadow.get("audio"), dict) else {}
        allowed_audio = audio.get("allowed_modes")
        required_audio = {"full-performance", "dialogue-and-sound-design"}
        if not isinstance(allowed_audio, list) or not required_audio.intersection(allowed_audio):
            errors.append("shadow_theatre.audio.allowed_modes: include a spoken/sung performance mode")
        if audio.get("silent_allowed") is not False:
            errors.append("shadow_theatre.audio.silent_allowed: expected false")
        if audio.get("music_only_allowed") is not False:
            errors.append("shadow_theatre.audio.music_only_allowed: expected false")
        for shortcut in ("opaque-full-body-png-as-shadow-puppet", "silent-shadow-theatre-master"):
            if shortcut not in forbidden_set:
                errors.append(f"forbidden_shortcuts: shadow route must ban {shortcut}")
        if "articulated-rig" not in allowed_modes and "pose-replacement" not in allowed_modes:
            errors.append("performance_policy.allowed_modes: shadow route needs articulation or pose replacement")
    elif route == "cutout-paper":
        cutout = data.get("cutout_paper")
        if not isinstance(cutout, dict):
            errors.append("cutout_paper: route requires a route-specific object")
            cutout = {}
        _required_text(errors, cutout, "cutout_paper", ("construction", "material_behavior", "depth_model"))
        if cutout.get("performer_model_required") is not True:
            errors.append("cutout_paper.performer_model_required: expected true")
        if not {"articulated-rig", "pose-replacement", "connected-ensemble", "full-scene-state"}.intersection(allowed_modes):
            errors.append("performance_policy.allowed_modes: cutout route needs a constructed performance mode")
    elif route == "painterly-limited":
        painterly = data.get("painterly_limited")
        if not isinstance(painterly, dict):
            errors.append("painterly_limited: route requires a route-specific object")
            painterly = {}
        _required_text(errors, painterly, "painterly_limited", ("paint_system", "integration_model", "state_change_model"))
        if painterly.get("claims_shadow_physics") is not False:
            errors.append("painterly_limited.claims_shadow_physics: expected false")
        if not {"pose-replacement", "articulated-rig", "full-scene-state", "selective-local-motion"}.intersection(allowed_modes):
            errors.append("performance_policy.allowed_modes: painterly route needs an authored local/pose/state mode")

    benchmark = data.get("benchmark")
    if not isinstance(benchmark, dict):
        errors.append("benchmark: required object")
        benchmark = {}
    if not nonempty(benchmark.get("shot_id")):
        errors.append("benchmark.shot_id: required")
    proves = benchmark.get("proves")
    if not isinstance(proves, list) or len(proves) < 3 or not all(nonempty(item) for item in proves):
        errors.append("benchmark.proves: add at least three observable capabilities")
    if phase in {"production", "release"}:
        if benchmark.get("status") != "approved":
            errors.append(f"benchmark.status: {phase} requires approved")
        if not nonempty(benchmark.get("rendered_mp4")):
            errors.append("benchmark.rendered_mp4: required after benchmark approval")

    approval = data.get("approval")
    if not isinstance(approval, dict):
        errors.append("approval: required object")
    elif phase in {"production", "release"}:
        _required_text(errors, approval, "approval", ("reviewer", "notes"))

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--phase", choices=sorted(PHASES), default="planning")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = load_json(args.contract.expanduser().resolve())
        errors, warnings = validate_medium_contract(data, phase=args.phase)
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
        print("PASS: medium contract" if result["ok"] else "FAIL: medium contract")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
