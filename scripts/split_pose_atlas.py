#!/usr/bin/env python3
"""Split a regular pose atlas into complete cells, optionally trim alpha, and write a manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def pad_image(image: Image.Image, padding: int) -> Image.Image:
    if padding <= 0:
        return image
    canvas = Image.new("RGBA", (image.width + padding * 2, image.height + padding * 2), (0, 0, 0, 0))
    canvas.alpha_composite(image, (padding, padding))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--cols", required=True, type=int)
    parser.add_argument("--rows", required=True, type=int)
    parser.add_argument("--trim", action="store_true")
    parser.add_argument("--padding", type=int, default=0)
    parser.add_argument("--alpha-threshold", type=int, default=8)
    parser.add_argument("--prefix", default="pose")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.cols <= 0 or args.rows <= 0 or args.padding < 0:
        raise SystemExit("cols and rows must be positive; padding cannot be negative")
    source = args.input.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    image = Image.open(source).convert("RGBA")
    cell_width = image.width // args.cols
    cell_height = image.height // args.rows
    if image.width % args.cols or image.height % args.rows:
        print("[WARNING] atlas dimensions are not evenly divisible; trailing pixels remain in the last row/column")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"source": str(source), "atlas_size": [image.width, image.height], "cols": args.cols, "rows": args.rows, "poses": []}

    pose_index = 0
    for row in range(args.rows):
        for col in range(args.cols):
            pose_index += 1
            left = col * cell_width
            top = row * cell_height
            right = image.width if col == args.cols - 1 else (col + 1) * cell_width
            bottom = image.height if row == args.rows - 1 else (row + 1) * cell_height
            cell = image.crop((left, top, right, bottom))
            alpha = cell.getchannel("A")
            mask = alpha.point(lambda value: 255 if value > args.alpha_threshold else 0)
            bbox = mask.getbbox()
            if not bbox:
                raise SystemExit(f"Cell row={row + 1} col={col + 1} is fully transparent")
            touches = []
            if bbox[0] <= 1:
                touches.append("left")
            if bbox[1] <= 1:
                touches.append("top")
            if bbox[2] >= cell.width - 1:
                touches.append("right")
            if bbox[3] >= cell.height - 1:
                touches.append("bottom")
            if args.trim:
                cell = cell.crop(bbox)
            cell = pad_image(cell, args.padding)
            filename = f"{args.prefix}-{pose_index:02d}.png"
            destination = output_dir / filename
            if destination.exists() and not args.overwrite:
                raise SystemExit(f"Output exists; pass --overwrite to replace it: {destination}")
            cell.save(destination)
            entry = {
                "id": pose_index,
                "row": row + 1,
                "col": col + 1,
                "file": filename,
                "cell_box": [left, top, right, bottom],
                "content_box": list(bbox),
                "output_size": [cell.width, cell.height],
                "touches_cell_edges": touches,
            }
            manifest["poses"].append(entry)
            suffix = f" warning=touches-{','.join(touches)}" if touches else ""
            print(f"{filename}: {cell.width}x{cell.height}{suffix}")

    manifest_path = output_dir / "poses-manifest.json"
    if manifest_path.exists() and not args.overwrite:
        raise SystemExit(f"Manifest exists; pass --overwrite to replace it: {manifest_path}")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(manifest['poses'])} poses and {manifest_path}")


if __name__ == "__main__":
    main()
