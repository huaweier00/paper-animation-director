#!/usr/bin/env python3
"""Audit routed engine inputs before development preview or formal shot release."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable


KNOWN_ENGINES = {"gsap-dom", "rive", "spine", "pixijs-webgpu", "three-webgpu", "blender"}
PIXEL_ENGINES = {"rive", "spine", "pixijs-webgpu", "three-webgpu"}
PLACEHOLDER_RE = re.compile(
    r"(?:^|[/_-])(?:placeholder|pending|sample|replace-me)(?:$|[/_.-])",
    re.IGNORECASE,
)
NETWORK_RE = re.compile(r"^(?:https?:)?//", re.IGNORECASE)
VALID_PIXI_PRESETS = {
    "hoof-dust",
    "impact-dust",
    "snow",
    "embers",
    "ink-motes",
    "paper-scraps",
    "falling-leaves",
    "rain-streaks",
    "smoke-wisps",
}
VALID_PIXI_MASKS = {"rect", "circle", "polygon", "band"}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{label} has invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} root must be an object")
    return data


def find_project_root(start: Path) -> Path:
    resolved = start.resolve()
    candidates = [resolved, *resolved.parents] if resolved.is_dir() else [resolved.parent, *resolved.parents]
    for candidate in candidates:
        if (candidate / "story-manifest.json").is_file() or (candidate / "hyperframes.json").is_file():
            return candidate
    return resolved if resolved.is_dir() else resolved.parent


def walk_strings(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, f"{path}[{index}]")


def resolve_local_asset(project_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        resolved = path.resolve()
    else:
        normalized = value[2:] if value.startswith("./") else value
        resolved = (project_root / normalized).resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError as exc:
        raise ValueError("asset escapes the project root") from exc
    return resolved


def validate_local_path(
    value: Any,
    *,
    field: str,
    project_root: Path,
    check_paths: bool,
    extensions: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    if not nonempty(value):
        return [f"{field}: provide a local project asset path"]
    assert isinstance(value, str)
    if NETWORK_RE.match(value) or value.startswith("data:"):
        return [f"{field}: render-critical assets must be local, not {value!r}"]
    if PLACEHOLDER_RE.search(value):
        errors.append(f"{field}: placeholder or pending media is forbidden for release: {value!r}")
    try:
        resolved = resolve_local_asset(project_root, value)
    except ValueError as exc:
        errors.append(f"{field}: {exc}")
        return errors
    if extensions and resolved.suffix.lower() not in extensions:
        errors.append(f"{field}: expected one of {sorted(extensions)}, got {resolved.suffix or '<none>'}")
    if check_paths and not resolved.is_file():
        errors.append(f"{field}: file does not exist: {resolved}")
    return errors


def validate_pixi(config: dict[str, Any], *, field: str) -> list[str]:
    errors: list[str] = []
    if config.get("ready") is not True:
        errors.append(f"{field}.ready: PixiJS must be ready when selected")
    if config.get("renderer_preference") not in {"webgpu", "webgl", "auto"}:
        errors.append(f"{field}.renderer_preference: expected webgpu, webgl, or auto")
    pixel_ratio = config.get("pixel_ratio")
    if not finite_number(pixel_ratio) or float(pixel_ratio) <= 0 or float(pixel_ratio) > 4:
        errors.append(f"{field}.pixel_ratio: expected a finite number in (0, 4]")
    masks = config.get("masks", [])
    mask_ids: set[str] = set()
    if not isinstance(masks, list):
        errors.append(f"{field}.masks: expected a list")
        masks = []
    for index, mask in enumerate(masks):
        item = f"{field}.masks[{index}]"
        if not isinstance(mask, dict):
            errors.append(f"{item}: expected an object")
            continue
        mask_id = mask.get("id")
        if not nonempty(mask_id):
            errors.append(f"{item}.id: required")
        elif mask_id in mask_ids:
            errors.append(f"{item}.id: duplicate mask id {mask_id!r}")
        else:
            mask_ids.add(mask_id)
        if mask.get("kind") not in VALID_PIXI_MASKS:
            errors.append(f"{item}.kind: expected one of {sorted(VALID_PIXI_MASKS)}")
        if mask.get("invert") is True:
            errors.append(f"{item}.invert: live inverted masks are not seek-safe; pre-render an alpha matte")
        if mask.get("kind") == "polygon":
            points = mask.get("points")
            if not isinstance(points, list) or len(points) < 3:
                errors.append(f"{item}.points: polygon requires at least three points")
    effects = config.get("effects")
    if not isinstance(effects, list) or not effects:
        errors.append(f"{field}.effects: selected PixiJS route requires at least one effect")
        return errors
    ids: set[str] = set()
    seeds: set[str] = set()
    for index, effect in enumerate(effects):
        item = f"{field}.effects[{index}]"
        if not isinstance(effect, dict):
            errors.append(f"{item}: expected an object")
            continue
        effect_id = effect.get("id")
        if not nonempty(effect_id):
            errors.append(f"{item}.id: required")
        elif effect_id in ids:
            errors.append(f"{item}.id: duplicate effect id {effect_id!r}")
        else:
            ids.add(effect_id)
        if effect.get("preset") not in VALID_PIXI_PRESETS:
            errors.append(f"{item}.preset: expected one of {sorted(VALID_PIXI_PRESETS)}")
        seed = effect.get("seed")
        if not nonempty(seed):
            errors.append(f"{item}.seed: fixed non-empty seed required")
        elif seed in seeds:
            errors.append(f"{item}.seed: duplicate seed {seed!r}; give each causal effect its own seed")
        else:
            seeds.add(seed)
        origin = effect.get("origin")
        if (
            not isinstance(origin, list)
            or len(origin) != 2
            or any(not finite_number(value) or not 0 <= float(value) <= 1 for value in origin)
        ):
            errors.append(f"{item}.origin: expected two normalized values in [0, 1]")
        for key in ("start", "duration"):
            value = effect.get(key)
            if not finite_number(value) or float(value) < 0 or (key == "duration" and float(value) <= 0):
                errors.append(f"{item}.{key}: expected a finite non-negative time with duration > 0")
        count = effect.get("count")
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            errors.append(f"{item}.count: expected a positive integer")
        opacity = effect.get("opacity")
        if not finite_number(opacity) or not 0 <= float(opacity) <= 1:
            errors.append(f"{item}.opacity: expected a finite value in [0, 1]")
        mask_id = effect.get("mask")
        if mask_id is not None and mask_id not in mask_ids:
            errors.append(f"{item}.mask: references unknown mask {mask_id!r}")
    return errors


def validate_engine_inputs(
    data: dict[str, Any],
    plan: dict[str, Any],
    *,
    project_root: Path,
    phase: str,
    check_paths: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    release = phase == "release"

    schema_version = data.get("schema_version")
    if schema_version not in {1, 2}:
        errors.append("schema_version: expected schema_version 1 or 2")
    if data.get("shot_id") != plan.get("shot_id"):
        errors.append(
            f"shot_id: engine inputs {data.get('shot_id')!r} do not match plan {plan.get('shot_id')!r}"
        )
    if data.get("clock") != "hyperframes-absolute-seconds":
        errors.append("clock: expected hyperframes-absolute-seconds")

    planned = plan.get("engines")
    if not isinstance(planned, list) or not planned or any(item not in KNOWN_ENGINES for item in planned):
        errors.append("engine plan: engines must be a non-empty list of known engines")
        planned = []
    configs = data.get("engines")
    if not isinstance(configs, dict):
        errors.append("engines: expected an object")
        configs = {}

    planned_set = set(planned)
    configured_set = set(configs)
    for missing in sorted(planned_set - configured_set):
        errors.append(f"engines.{missing}: selected by engine-plan.json but missing from engine-inputs.json")
    for extra in sorted(configured_set - planned_set):
        errors.append(f"engines.{extra}: configured but not selected by engine-plan.json")

    for string_path, value in walk_strings(data):
        if NETWORK_RE.match(value):
            errors.append(f"{string_path}: runtime network assets are forbidden: {value!r}")
        if release and PLACEHOLDER_RE.search(value):
            errors.append(f"{string_path}: placeholder or pending value is forbidden for release: {value!r}")

    for engine in planned:
        raw = configs.get(engine)
        field = f"engines.{engine}"
        if not isinstance(raw, dict):
            continue
        ready = raw.get("ready")
        if not isinstance(ready, bool):
            errors.append(f"{field}.ready: declare true or false")
            ready = False
        if release and ready is not True:
            errors.append(f"{field}.ready: selected engine must be ready before release")
        elif not release and ready is not True and engine in {"rive", "spine", "blender"}:
            warnings.append(f"{field}.ready: authored asset gate remains pending")

        if engine == "gsap-dom":
            if ready is not True:
                errors.append(f"{field}.ready: GSAP/DOM orchestration must be ready")
        elif engine == "pixijs-webgpu":
            errors.extend(validate_pixi(raw, field=field))
        elif engine == "three-webgpu":
            if ready is not True:
                errors.append(f"{field}.ready: bundled Three.js template must be ready")
            for key in ("alpha", "antialias", "force_webgl"):
                if not isinstance(raw.get(key), bool):
                    errors.append(f"{field}.{key}: declare true or false")
            pixel_ratio = raw.get("pixel_ratio")
            if not finite_number(pixel_ratio) or not 0 < float(pixel_ratio) <= 4:
                errors.append(f"{field}.pixel_ratio: expected a finite number in (0, 4]")
            errors.extend(
                validate_local_path(
                    raw.get("scene_factory"),
                    field=f"{field}.scene_factory",
                    project_root=project_root,
                    check_paths=check_paths and ready is True,
                    extensions={".js", ".mjs"},
                )
            )
            if schema_version == 2:
                errors.extend(
                    validate_local_path(
                        raw.get("scene_manifest"),
                        field=f"{field}.scene_manifest",
                        project_root=project_root,
                        check_paths=check_paths and ready is True,
                        extensions={".json"},
                    )
                )
        elif engine == "rive" and ready is True:
            errors.extend(
                validate_local_path(
                    raw.get("asset"),
                    field=f"{field}.asset",
                    project_root=project_root,
                    check_paths=check_paths,
                    extensions={".riv"},
                )
            )
            for key in ("artboard", "animation", "playback", "fit", "alignment"):
                if not nonempty(raw.get(key)):
                    errors.append(f"{field}.{key}: required for a ready Rive asset")
            if raw.get("state_machine_forbidden") is not True:
                errors.append(f"{field}.state_machine_forbidden: must be true for seekable release")
            if schema_version == 2:
                errors.extend(
                    validate_local_path(
                        raw.get("rig_manifest"),
                        field=f"{field}.rig_manifest",
                        project_root=project_root,
                        check_paths=check_paths,
                        extensions={".json"},
                    )
                )
        elif engine == "spine" and ready is True:
            errors.extend(
                validate_local_path(
                    raw.get("asset"),
                    field=f"{field}.asset",
                    project_root=project_root,
                    check_paths=check_paths,
                    extensions={".json", ".skel"},
                )
            )
            if not nonempty(raw.get("animation")):
                errors.append(f"{field}.animation: required for a ready Spine asset")
            if raw.get("stateful_physics_forbidden") is not True:
                errors.append(f"{field}.stateful_physics_forbidden: must be true for seekable release")
        elif engine == "blender" and ready is True:
            errors.extend(
                validate_local_path(
                    raw.get("asset"),
                    field=f"{field}.asset",
                    project_root=project_root,
                    check_paths=check_paths,
                    extensions={".webm", ".mov", ".mp4"},
                )
            )
            errors.extend(
                validate_local_path(
                    raw.get("source_blend"),
                    field=f"{field}.source_blend",
                    project_root=project_root,
                    check_paths=check_paths,
                    extensions={".blend"},
                )
            )
            if raw.get("physics_baked") is not True:
                errors.append(f"{field}.physics_baked: must be true before release")
            manifest = raw.get("prerender_manifest")
            if release:
                errors.extend(
                    validate_local_path(
                        manifest,
                        field=f"{field}.prerender_manifest",
                        project_root=project_root,
                        check_paths=check_paths,
                        extensions={".json"},
                    )
                )
            if schema_version == 2:
                errors.extend(
                    validate_local_path(
                        raw.get("action_library"),
                        field=f"{field}.action_library",
                        project_root=project_root,
                        check_paths=check_paths,
                        extensions={".json"},
                    )
                )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine_inputs", type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--phase", choices=("development", "release"), default="development")
    parser.add_argument("--skip-path-checks", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        inputs_path = args.engine_inputs.expanduser().resolve()
        plan_path = args.plan.expanduser().resolve()
        project_root = (
            args.project.expanduser().resolve()
            if args.project
            else find_project_root(inputs_path)
        )
        data = load_json(inputs_path, "engine inputs")
        plan = load_json(plan_path, "engine plan")
        errors, warnings = validate_engine_inputs(
            data,
            plan,
            project_root=project_root,
            phase=args.phase,
            check_paths=not args.skip_path_checks,
        )
    except (OSError, ValueError) as exc:
        errors, warnings = [str(exc)], []
        project_root = args.project or Path.cwd()

    result = {
        "engine_inputs": str(args.engine_inputs),
        "engine_plan": str(args.plan),
        "project": str(project_root),
        "phase": args.phase,
        "approved": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("PASS: engine inputs approved" if not errors else "FAIL: engine inputs remain locked")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
