#!/usr/bin/env python3
"""Convert a flat chroma background to alpha with soft edges and light despill."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image


def parse_color(value: str) -> tuple[int, int, int]:
    value = value.strip()
    if value.startswith("#") and len(value) == 7:
        return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]
    parts = [part.strip() for part in value.split(",")]
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        color = tuple(int(part) for part in parts)
        if all(0 <= channel <= 255 for channel in color):
            return color  # type: ignore[return-value]
    raise argparse.ArgumentTypeError("use #rrggbb or r,g,b")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--key-color", type=parse_color, default=parse_color("#ff00ff"))
    parser.add_argument("--tolerance", type=float, default=55)
    parser.add_argument("--softness", type=float, default=42)
    parser.add_argument("--despill", type=float, default=0.65)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if source == output:
        raise SystemExit("Input and output must be different files")
    if output.exists() and not args.overwrite:
        raise SystemExit(f"Output exists; pass --overwrite to replace it: {output}")
    if args.tolerance < 0 or args.softness <= 0 or not 0 <= args.despill <= 1:
        raise SystemExit("tolerance must be non-negative, softness positive, and despill between 0 and 1")

    image = Image.open(source).convert("RGBA")
    key_r, key_g, key_b = args.key_color
    keyed: list[tuple[int, int, int, int]] = []
    removed = 0
    partial = 0
    for red, green, blue, old_alpha in image.getdata():
        distance = math.sqrt((red - key_r) ** 2 + (green - key_g) ** 2 + (blue - key_b) ** 2)
        if distance <= args.tolerance:
            matte = 0
        elif distance >= args.tolerance + args.softness:
            matte = 255
        else:
            matte = round(255 * (distance - args.tolerance) / args.softness)
        alpha = round(old_alpha * matte / 255)
        if alpha == 0:
            removed += 1
        elif alpha < 255:
            partial += 1
        edge_mix = args.despill * (1 - matte / 255)
        neutral = sorted((red, green, blue))[1]
        key_strength = max(key_r, key_g, key_b, 1)
        red = round(red * (1 - edge_mix * key_r / key_strength) + neutral * edge_mix * key_r / key_strength)
        green = round(green * (1 - edge_mix * key_g / key_strength) + neutral * edge_mix * key_g / key_strength)
        blue = round(blue * (1 - edge_mix * key_b / key_strength) + neutral * edge_mix * key_b / key_strength)
        keyed.append((red, green, blue, alpha))
    image.putdata(keyed)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    total = image.width * image.height
    print(f"Saved {output}")
    print(f"size={image.width}x{image.height} removed={removed / total:.2%} partial_edges={partial / total:.2%}")


if __name__ == "__main__":
    main()
