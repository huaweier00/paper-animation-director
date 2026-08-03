#!/usr/bin/env python3
"""Audit a standard Rive character-rig contract and optional WASM inspection."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


PLAYBACK = {"native", "loop", "clamp", "ping-pong"}
PROFILES = {"benchmark-linear", "production-hero"}
PRODUCTION_ANIMATIONS = {"idle", "locomotion"}
PRODUCTION_ANCHORS = {
    "root",
    "head",
    "left_hand",
    "right_hand",
    "left_foot",
    "right_foot",
}


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value


def local_file(root: Path, value: Any, field: str, suffixes: set[str]) -> tuple[Path | None, list[str]]:
    if not isinstance(value, str) or not value.strip():
        return None, [f"{field}: local path required"]
    if value.startswith(("http://", "https://", "//", "data:")):
        return None, [f"{field}: runtime-network assets are forbidden"]
    candidate = (root / value.removeprefix("./")).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None, [f"{field}: asset escapes project root"]
    errors = []
    if candidate.suffix.lower() not in suffixes:
        errors.append(f"{field}: expected one of {sorted(suffixes)}")
    if not candidate.is_file():
        errors.append(f"{field}: file not found: {candidate}")
    return candidate, errors


def audit(
    manifest: dict[str, Any],
    *,
    root: Path,
    phase: str,
    inspection: dict[str, Any] | None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    profile = manifest.get("profile")
    if manifest.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if profile not in PROFILES:
        errors.append(f"profile: expected one of {sorted(PROFILES)}")
    if not isinstance(manifest.get("rig_id"), str) or not manifest["rig_id"].strip():
        errors.append("rig_id: non-empty stable id required")
    asset, asset_errors = local_file(root, manifest.get("asset"), "asset", {".riv"})
    errors.extend(asset_errors)
    if not isinstance(manifest.get("artboard"), str) or not manifest["artboard"].strip():
        errors.append("artboard: non-empty name required")
    if manifest.get("state_machine_forbidden") is not True:
        errors.append("state_machine_forbidden: must be true for absolute-time release")

    animations = manifest.get("animations")
    if not isinstance(animations, dict) or not animations:
        errors.append("animations: at least one named linear animation is required")
        animations = {}
    if profile == "production-hero":
        for name in sorted(PRODUCTION_ANIMATIONS - set(animations)):
            errors.append(f"animations.{name}: required by production-hero profile")
    selected_names: set[str] = set()
    for role, item in animations.items():
        field = f"animations.{role}"
        if not isinstance(item, dict):
            errors.append(f"{field}: expected object")
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{field}.name: required")
        else:
            selected_names.add(name)
        playback = item.get("playback")
        if playback not in PLAYBACK:
            errors.append(f"{field}.playback: expected one of {sorted(PLAYBACK)}")
        duration = item.get("duration_seconds")
        if playback != "native" and (
            not isinstance(duration, (int, float))
            or isinstance(duration, bool)
            or not math.isfinite(float(duration))
            or float(duration) <= 0
        ):
            errors.append(f"{field}.duration_seconds: positive finite value required for {playback}")

    anchors = manifest.get("anchors")
    if not isinstance(anchors, dict):
        errors.append("anchors: expected object")
        anchors = {}
    if profile == "production-hero":
        for name in sorted(PRODUCTION_ANCHORS - set(anchors)):
            errors.append(f"anchors.{name}: required by production-hero profile")
        _, identity_errors = local_file(
            root,
            manifest.get("identity_reference"),
            "identity_reference",
            {".png", ".jpg", ".jpeg", ".webp"},
        )
        errors.extend(identity_errors)
        _, fallback_errors = local_file(
            root,
            manifest.get("fallback"),
            "fallback",
            {".webm", ".mov", ".mp4"},
        )
        if phase == "release":
            errors.extend(fallback_errors)
        else:
            warnings.extend(fallback_errors)
    facing = manifest.get("facing")
    if not isinstance(facing, list) or not facing or any(not isinstance(x, str) for x in facing):
        errors.append("facing: declare at least one authored facing")

    if inspection is None:
        message = "inspection_report: run inspect_rive_asset.mjs against the real .riv asset"
        (errors if phase == "release" else warnings).append(message)
    else:
        if inspection.get("ok") is not True:
            errors.append("inspection_report: runtime inspection did not pass")
        artboards = inspection.get("artboards")
        matching = None
        if isinstance(artboards, list):
            matching = next(
                (
                    item
                    for item in artboards
                    if isinstance(item, dict) and item.get("name") == manifest.get("artboard")
                ),
                None,
            )
        if not matching:
            errors.append(f"inspection_report: artboard not found: {manifest.get('artboard')!r}")
        else:
            available = set(matching.get("animations", []))
            for name in sorted(selected_names - available):
                errors.append(f"inspection_report: animation not found in artboard: {name!r}")
        if asset and asset.is_file():
            digest = hashlib.sha256(asset.read_bytes()).hexdigest()
            if inspection.get("asset_sha256") != digest:
                errors.append("inspection_report: asset SHA-256 does not match current .riv file")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--inspection", type=Path)
    parser.add_argument("--phase", choices=("development", "release"), default="development")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        manifest_path = args.manifest.expanduser().resolve()
        root = args.project.expanduser().resolve() if args.project else manifest_path.parent.parent
        manifest = load_json(manifest_path, "Rive rig manifest")
        inspection_path = args.inspection
        if inspection_path is None and isinstance(manifest.get("inspection_report"), str):
            inspection_path = root / manifest["inspection_report"]
        inspection = load_json(inspection_path.resolve(), "Rive inspection") if inspection_path else None
        errors, warnings = audit(manifest, root=root, phase=args.phase, inspection=inspection)
    except (OSError, ValueError) as exc:
        errors, warnings = [str(exc)], []
    result = {
        "manifest": str(args.manifest),
        "phase": args.phase,
        "approved": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in warnings:
            print(f"WARNING: {item}")
        for item in errors:
            print(f"ERROR: {item}")
        print("PASS: Rive rig approved" if not errors else "FAIL: Rive rig remains locked")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
