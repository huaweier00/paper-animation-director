#!/usr/bin/env python3
"""Extract proof, identity, and occlusion frames into a labeled review contact sheet."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def manifest_times(path: Path) -> list[float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    times: list[float] = []
    scene_start = 0.0
    for scene in data.get("scenes", []):
        duration = float(scene.get("duration", 0))
        review_contract = scene.get("review_contract", {})
        for review_time in review_contract.get("review_times", []):
            if isinstance(review_time, (int, float)):
                times.append(scene_start + float(review_time))
        for occlusion in review_contract.get("intentional_occlusions", []):
            if not isinstance(occlusion, dict):
                continue
            for key in ("start", "maximum_time", "end", "identity_proof_time"):
                if isinstance(occlusion.get(key), (int, float)):
                    times.append(scene_start + float(occlusion[key]))
        for event in scene.get("events", []):
            if isinstance(event.get("proof_time"), (int, float)):
                times.append(scene_start + float(event["proof_time"]))
        if not any(isinstance(event.get("proof_time"), (int, float)) for event in scene.get("events", [])) and duration > 0:
            times.append(scene_start + duration * 0.5)
        scene_start += duration
    if scene_start > 0:
        times.extend([0.0, max(0, scene_start - 0.05)])
    return sorted(set(round(max(0, value), 3) for value in times))


def parse_times(value: str) -> list[float]:
    return [float(part.strip()) for part in value.split(",") if part.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--times", type=parse_times)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--cell-width", type=int, default=560)
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is required")
    if args.columns <= 0 or args.cell_width < 160:
        raise SystemExit("columns must be positive and cell-width at least 160")
    times = list(args.times or [])
    if not times and args.manifest:
        times = manifest_times(args.manifest.expanduser().resolve())
    times = sorted(set(round(max(0, value), 3) for value in times))
    if not times:
        raise SystemExit("Provide --times or a manifest with proof_time values")

    video = args.video.expanduser().resolve()
    output = args.output.expanduser().resolve()
    font = ImageFont.load_default()
    label_height = 28
    frames: list[tuple[float, Image.Image]] = []
    with tempfile.TemporaryDirectory(prefix="paper-review-") as temporary:
        temp = Path(temporary)
        for index, time in enumerate(times):
            frame_path = temp / f"frame-{index:03d}.png"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(time), "-i", str(video),
                "-frames:v", "1", "-update", "1", "-vf", f"scale={args.cell_width}:-2", str(frame_path),
            ], check=True)
            frames.append((time, Image.open(frame_path).convert("RGB").copy()))

    cell_height = max(frame.height for _, frame in frames) + label_height
    rows = math.ceil(len(frames) / args.columns)
    sheet = Image.new("RGB", (args.columns * args.cell_width, rows * cell_height), (26, 23, 20))
    draw = ImageDraw.Draw(sheet)
    for index, (time, frame) in enumerate(frames):
        col = index % args.columns
        row = index // args.columns
        x = col * args.cell_width
        y = row * cell_height
        sheet.paste(frame, (x, y + label_height))
        draw.rectangle((x, y, x + args.cell_width, y + label_height), fill=(34, 30, 27))
        draw.text((x + 10, y + 7), f"{index + 1}. {time:.3f}s", fill=(245, 237, 216), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() in {".jpg", ".jpeg"}:
        sheet.save(output, quality=92, subsampling=0)
    else:
        sheet.save(output)
    print(f"Saved {len(frames)} proof frames to {output}")


if __name__ == "__main__":
    main()
