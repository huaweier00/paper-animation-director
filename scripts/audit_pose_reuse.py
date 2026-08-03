#!/usr/bin/env python3
"""Detect production-pose reuse across incompatible shot intentions or states."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from audit_performance_contract import load_json, nonempty


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def performance_contract_paths(project: Path) -> list[Path]:
    return sorted(project.glob("shots/*/performance-contract.json"))


def validate_pose_reuse(project: Path) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    usages: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    paths = performance_contract_paths(project)
    if not paths:
        return ["shots: no performance-contract.json records found"], warnings, {"contracts": 0, "groups": []}

    for path in paths:
        try:
            data = load_json(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        shot_id = data.get("shot_id")
        actors = data.get("actors", [])
        if not isinstance(actors, list):
            errors.append(f"{path}: actors must be a list")
            continue
        for index, actor in enumerate(actors):
            if not isinstance(actor, dict):
                continue
            asset = actor.get("production_asset")
            if not isinstance(asset, dict):
                continue
            actor_id = actor.get("actor_id")
            digest = asset.get("sha256")
            if not nonempty(actor_id) or not isinstance(digest, str) or not SHA256_RE.match(digest):
                continue
            authorization = asset.get("reuse_authorization")
            if not isinstance(authorization, dict):
                authorization = {}
            usages[(str(actor_id), digest)].append(
                {
                    "path": str(path),
                    "shot_id": shot_id,
                    "actor_index": index,
                    "asset_id": asset.get("asset_id"),
                    "state": asset.get("performance_state"),
                    "objective": actor.get("objective"),
                    "attention": [actor.get("initial_attention"), actor.get("final_attention")],
                    "authorization": authorization,
                }
            )

    groups: list[dict[str, Any]] = []
    for (actor_id, digest), items in sorted(usages.items()):
        states = {item["state"] for item in items if nonempty(item.get("state"))}
        objectives = {item["objective"] for item in items if nonempty(item.get("objective"))}
        attentions = {
            json.dumps(item["attention"], ensure_ascii=False, sort_keys=True)
            for item in items
        }
        group = {
            "actor_id": actor_id,
            "sha256": digest,
            "uses": items,
            "states": sorted(states),
            "objective_count": len(objectives),
            "attention_count": len(attentions),
        }
        groups.append(group)
        if len(items) < 2:
            continue
        incompatible = len(states) > 1 or len(objectives) > 1 or len(attentions) > 1
        if not incompatible:
            continue
        unauthorized = [
            item
            for item in items
            if item["authorization"].get("approved") is not True
            or not nonempty(item["authorization"].get("reason"))
        ]
        if unauthorized:
            shot_names = [str(item.get("shot_id")) for item in unauthorized]
            errors.append(
                f"actor {actor_id!r} reuses asset hash {digest[:12]} across incompatible intentions/states "
                f"without explicit approval in shots {shot_names}"
            )
        else:
            compatible_states = set()
            for item in items:
                values = item["authorization"].get("compatible_states", [])
                if isinstance(values, list):
                    compatible_states.update(str(value) for value in values if nonempty(value))
            if states and not states.issubset(compatible_states):
                errors.append(
                    f"actor {actor_id!r} reuse approval does not enumerate every compatible performance state: "
                    f"missing {sorted(states - compatible_states)}"
                )
            else:
                warnings.append(
                    f"actor {actor_id!r} intentionally reuses one production pose across {len(items)} different shot contexts"
                )

    return errors, warnings, {"contracts": len(paths), "groups": groups}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    try:
        if not project.is_dir():
            raise ValueError(f"project does not exist: {project}")
        errors, warnings, derived = validate_pose_reuse(project)
    except (OSError, ValueError) as exc:
        errors, warnings, derived = [str(exc)], [], {}
    result = {"ok": not errors and (not warnings or not args.strict), "errors": errors, "warnings": warnings, "derived": derived}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("PASS: pose reuse" if result["ok"] else "FAIL: pose reuse")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
