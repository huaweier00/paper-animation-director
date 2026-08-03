#!/usr/bin/env python3
"""Compile a validated motion contract into an implementation-ready deterministic track."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from audit_motion_contract import audit_contract, load_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    contract = args.contract.expanduser().resolve()
    project = args.project.expanduser().resolve()
    output = args.output.expanduser().resolve()
    try:
        data = load_json(contract, "motion contract")
        errors, warnings, derived = audit_contract(
            data, contract_path=contract, project=project, phase="implementation"
        )
        if errors:
            raise ValueError("; ".join(errors))
        width = int(derived["frame"]["width"])
        height = int(derived["frame"]["height"])
        tracks = []
        for actor in derived["actors"]:
            start = actor["start"]
            end = actor["end"]
            tracks.append(
                {
                    "actor_id": actor["actor_id"],
                    "selector": actor["selector"],
                    "engine": actor["engine"],
                    "asset_id": actor["asset_id"],
                    "start_px": [round(float(start[0]) * width, 4), round(float(start[1]) * height, 4)],
                    "end_px": [round(float(end[0]) * width, 4), round(float(end[1]) * height, 4)],
                    "delta_px": [round(float(actor["delta"][0]) * width, 4), round(float(actor["delta"][1]) * height, 4)],
                    "active": actor["active"],
                    "scale_x": actor["scale_x"],
                    "intrinsic_facing": actor["intrinsic_facing"],
                    "rendered_facing": actor["rendered_facing"],
                    "travel_direction": actor["travel_direction"],
                    "proof_times": actor["proof_times"],
                }
            )
        payload = {
            "schema_version": 1,
            "shot_id": derived["shot_id"],
            "clock": "hyperframes-absolute-seconds",
            "coordinate_space": "normalized-stage-anchor-compiled-to-pixels",
            "frame": {"width": width, "height": height},
            "duration": derived["duration"],
            "source_contract": str(contract.relative_to(project)),
            "source_contract_sha256": derived["contract_sha256"],
            "warnings": warnings,
            "tracks": tracks,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = {"ok": True, "output": str(output), "tracks": len(tracks)}
    except (OSError, ValueError, KeyError) as exc:
        result = {"ok": False, "error": str(exc)}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"PASS: wrote {result['output']}" if result["ok"] else f"FAIL: {result['error']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
