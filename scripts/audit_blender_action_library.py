#!/usr/bin/env python3
"""Audit a modular Blender paper-physics action library."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


KINDS = {"rigid-body", "rigid-body-collision", "hinge", "cloth", "soft-body"}
ROLE_REQUIREMENTS = {
    "rigid-body": {"active", "support"},
    "rigid-body-collision": {"active", "impactor", "support"},
    "hinge": {"active", "anchor"},
    "cloth": {"cloth", "pins"},
    "soft-body": {"active"},
}


def audit(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if data.get("engine") != "blender":
        errors.append("engine: expected blender")
    if data.get("plane") != "camera-facing-xz":
        errors.append("plane: expected camera-facing-xz")
    actions = data.get("actions")
    if not isinstance(actions, list) or not actions:
        errors.append("actions: at least one action required")
        actions = []
    ids: set[str] = set()
    for index, action in enumerate(actions):
        field = f"actions[{index}]"
        if not isinstance(action, dict):
            errors.append(f"{field}: object required")
            continue
        action_id = action.get("id")
        if not isinstance(action_id, str) or not action_id:
            errors.append(f"{field}.id: required")
        elif action_id in ids:
            errors.append(f"{field}.id: duplicate {action_id!r}")
        else:
            ids.add(action_id)
        kind = action.get("kind")
        if kind not in KINDS:
            errors.append(f"{field}.kind: expected one of {sorted(KINDS)}")
            continue
        roles = action.get("required_roles")
        if not isinstance(roles, list) or not ROLE_REQUIREMENTS[kind].issubset(set(roles)):
            errors.append(f"{field}.required_roles: missing {sorted(ROLE_REQUIREMENTS[kind])}")
        if action.get("bake_required") is not True:
            errors.append(f"{field}.bake_required: must be true")
        if not isinstance(action.get("parameters"), dict):
            errors.append(f"{field}.parameters: object required")
    release = data.get("release_contract")
    required_release = {
        "editable_blend_required",
        "baked_cache_required",
        "build_record_required",
        "transparent_master_required",
        "placeholder_media_forbidden",
    }
    if not isinstance(release, dict):
        errors.append("release_contract: object required")
    else:
        for key in sorted(required_release):
            if release.get(key) is not True:
                errors.append(f"release_contract.{key}: must be true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("manifest root must be an object")
        errors = audit(data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    result = {"manifest": str(args.manifest), "approved": not errors, "errors": errors}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in errors:
            print(f"ERROR: {item}")
        print("PASS: Blender action library approved" if not errors else "FAIL: Blender action library remains locked")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
