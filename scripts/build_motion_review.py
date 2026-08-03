#!/usr/bin/env python3
"""Extract rendered motion proof frames and build a review contact sheet with expected arrows."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from audit_motion_contract import audit_contract, load_json, project_path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], direction: str, color: str, label: str) -> None:
    length = 110
    sign = -1 if direction == "left" else 1
    end = (start[0] + sign * length, start[1])
    draw.line([start, end], fill=color, width=6)
    draw.polygon(
        [end, (end[0] - sign * 18, end[1] - 12), (end[0] - sign * 18, end[1] + 12)],
        fill=color,
    )
    draw.text((min(start[0], end[0]), start[1] + 10), label, fill=color)


def relative(project: Path, path: Path) -> str:
    return str(path.resolve().relative_to(project.resolve()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", nargs="?", type=Path, help="legacy positional motion-contract path")
    parser.add_argument("--contract", dest="contract_option", type=Path, help="motion-contract path")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--video", required=True)
    parser.add_argument("--output", required=True, type=Path, help="rendered-motion-review JSON path")
    parser.add_argument("--evidence-dir", type=Path, help="optional extracted-frame/contact-sheet directory")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    selected_contract = args.contract_option or args.contract
    if selected_contract is None:
        parser.error("provide --contract (or the legacy positional contract path)")
    contract = selected_contract.expanduser().resolve()
    output = args.output.expanduser().resolve()
    try:
        if shutil.which(args.ffmpeg) is None:
            raise ValueError(f"ffmpeg not found: {args.ffmpeg}")
        video = project_path(project, args.video, "video")
        if not video.is_file():
            raise ValueError(f"video does not exist: {video}")
        data = load_json(contract, "motion contract")
        errors, warnings, derived = audit_contract(
            data, contract_path=contract, project=project, phase="release"
        )
        if errors:
            raise ValueError("; ".join(errors))
        legacy_output_directory = output.suffix.lower() != ".json"
        review_path = contract.parent / "rendered-motion-review.json" if legacy_output_directory else output
        evidence_dir = (
            output
            if legacy_output_directory
            else (args.evidence_dir.expanduser().resolve() if args.evidence_dir else review_path.parent / "review" / "motion")
        )
        review_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        roles: dict[str, float] = {}
        for actor in derived["actors"]:
            for role, value in actor["proof_times"].items():
                key = f"{role}-{float(value):.3f}"
                roles[key] = float(value)
        frames: list[dict[str, Any]] = []
        images: list[tuple[str, float, Image.Image]] = []
        for index, (label, time) in enumerate(sorted(roles.items(), key=lambda item: item[1])):
            frame_path = evidence_dir / f"frame-{index:02d}-{label}.png"
            result = subprocess.run(
                [
                    args.ffmpeg,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-ss",
                    f"{time:.6f}",
                    "-i",
                    str(video),
                    "-frames:v",
                    "1",
                    "-y",
                    str(frame_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0 or not frame_path.is_file():
                raise ValueError(f"frame extraction failed at {time:.3f}s: {result.stderr.strip()}")
            frames.append(
                {
                    "label": label,
                    "time": time,
                    "path": relative(project, frame_path),
                    "sha256": sha256(frame_path),
                }
            )
            images.append((label, time, Image.open(frame_path).convert("RGB")))

        thumb_width = 480
        header = 86
        rows: list[Image.Image] = []
        for label, time, source in images:
            height = round(source.height * thumb_width / source.width)
            panel = Image.new("RGB", (thumb_width, height + header), "white")
            panel.paste(source.resize((thumb_width, height), Image.Resampling.LANCZOS), (0, header))
            draw = ImageDraw.Draw(panel)
            draw.text((12, 8), f"{label}  t={time:.3f}s", fill="black", font=ImageFont.load_default())
            y = 36
            for actor in derived["actors"]:
                travel = actor["travel_direction"]
                facing = actor["rendered_facing"]
                if travel in {"left", "right"}:
                    arrow(draw, (150, y + 8), travel, "#1769aa", f"travel:{actor['actor_id']}")
                if facing in {"left", "right"}:
                    arrow(draw, (330, y + 8), facing, "#c62828", f"facing:{actor['actor_id']}")
                y += 22
            rows.append(panel)
        columns = 2
        panel_height = max(panel.height for panel in rows)
        sheet = Image.new("RGB", (thumb_width * columns, panel_height * ((len(rows) + 1) // 2)), "#ddd8ce")
        for index, panel in enumerate(rows):
            sheet.paste(panel, ((index % columns) * thumb_width, (index // columns) * panel_height))
        sheet_path = evidence_dir / "motion-contact-sheet.png"
        sheet.save(sheet_path)

        review = {
            "schema_version": 1,
            "shot_id": derived["shot_id"],
            "motion_contract": relative(project, contract),
            "motion_contract_sha256": derived["contract_sha256"],
            "rendered_mp4": relative(project, video),
            "rendered_mp4_sha256": sha256(video),
            "contact_sheet": relative(project, sheet_path),
            "contact_sheet_sha256": sha256(sheet_path),
            "evidence_frames": frames,
            "actors": [
                {
                    "actor_id": actor["actor_id"],
                    "expected_rendered_facing": actor["rendered_facing"],
                    "expected_travel_direction": actor["travel_direction"],
                    "required_checks": {
                        "direction": True,
                        "support": True,
                        "contact": actor["contact_required"],
                        "identity": True,
                        "result": True,
                    },
                    "observed": {
                        "direction": "pending",
                        "support": "pending",
                        "contact": "pending" if actor["contact_required"] else "not-required",
                        "identity": "pending",
                        "result": "pending",
                    },
                    "decision": "pending",
                    "review_notes": "",
                }
                for actor in derived["actors"]
            ],
            "warnings": warnings,
            "package_notes": [
                "Legacy directory-style --output was used; pass a .json review path for new work."
            ] if legacy_output_directory else [],
            "decision": "pending",
            "review_notes": "",
        }
        review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result_payload = {
            "ok": True,
            "review": str(review_path),
            "contact_sheet": str(sheet_path),
            "frames": len(frames),
        }
    except (OSError, ValueError, KeyError) as exc:
        result_payload = {"ok": False, "error": str(exc)}
    if args.as_json:
        print(json.dumps(result_payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"PASS: review package {result_payload['review']}"
            if result_payload["ok"]
            else f"FAIL: {result_payload['error']}"
        )
    return 0 if result_payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
