#!/usr/bin/env python3
"""Audit a declarative Three.js 2.5D depth-board/model scene manifest."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


KINDS = {"plane", "shape", "model"}
MOTIONS = {"static", "parallax", "bob", "sway"}


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("scene manifest root must be an object")
    return value


def local_asset(root: Path, value: Any, field: str, required: bool) -> list[str]:
    if not isinstance(value, str) or not value:
        return [f"{field}: local source required"] if required else []
    if value.startswith(("http://", "https://", "//", "data:")):
        return [f"{field}: runtime-network assets are forbidden"]
    target = (root / value.removeprefix("./")).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return [f"{field}: source escapes project root"]
    if required and not target.is_file():
        return [f"{field}: file not found: {target}"]
    return []


def audit(data: dict[str, Any], *, root: Path, phase: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if data.get("previous_frame_effects_forbidden") is not True:
        errors.append("previous_frame_effects_forbidden: must be true")
    if data.get("local_assets_only") is not True:
        errors.append("local_assets_only: must be true")
    camera = data.get("camera")
    if not isinstance(camera, dict):
        errors.append("camera: object required")
    else:
        near, far = camera.get("near"), camera.get("far")
        if not finite(near) or not finite(far) or float(near) <= 0 or float(far) <= float(near):
            errors.append("camera: require 0 < near < far")
        if camera.get("kind") not in {"perspective", "orthographic"}:
            errors.append("camera.kind: expected perspective or orthographic")
    layers = data.get("layers")
    if not isinstance(layers, list) or not layers:
        errors.append("layers: at least one layer required")
        layers = []
    ids: set[str] = set()
    depths: dict[str, float] = {}
    for index, layer in enumerate(layers):
        field = f"layers[{index}]"
        if not isinstance(layer, dict):
            errors.append(f"{field}: object required")
            continue
        layer_id = layer.get("id")
        if not isinstance(layer_id, str) or not layer_id:
            errors.append(f"{field}.id: required")
        elif layer_id in ids:
            errors.append(f"{field}.id: duplicate {layer_id!r}")
        else:
            ids.add(layer_id)
        kind = layer.get("kind")
        if kind not in KINDS:
            errors.append(f"{field}.kind: expected one of {sorted(KINDS)}")
        depth = layer.get("depth")
        if not finite(depth):
            errors.append(f"{field}.depth: finite number required")
        elif isinstance(layer_id, str):
            depths[layer_id] = float(depth)
        motion = layer.get("motion")
        if not isinstance(motion, dict) or motion.get("kind") not in MOTIONS:
            errors.append(f"{field}.motion.kind: expected one of {sorted(MOTIONS)}")
        if kind == "shape":
            points = layer.get("points")
            if not isinstance(points, list) or len(points) < 3:
                errors.append(f"{field}.points: shape requires at least three points")
        if kind == "model":
            required = layer.get("required") is not False and phase == "release"
            problems = local_asset(root, layer.get("source"), f"{field}.source", required)
            (errors if required else warnings).extend(problems)
    order = data.get("occlusion_order")
    if not isinstance(order, list) or set(order) != ids or len(order) != len(ids):
        errors.append("occlusion_order: must name every layer exactly once")
    elif all(item in depths for item in order):
        values = [depths[item] for item in order]
        if values != sorted(values):
            errors.append("occlusion_order: must follow ascending depth from back to front")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--phase", choices=("development", "release"), default="development")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        path = args.manifest.expanduser().resolve()
        data = load(path)
        root = args.project.expanduser().resolve() if args.project else path.parent
        errors, warnings = audit(data, root=root, phase=args.phase)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors, warnings = [str(exc)], []
    result = {"manifest": str(args.manifest), "approved": not errors, "errors": errors, "warnings": warnings}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in warnings:
            print(f"WARNING: {item}")
        for item in errors:
            print(f"ERROR: {item}")
        print("PASS: Three scene approved" if not errors else "FAIL: Three scene remains locked")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
