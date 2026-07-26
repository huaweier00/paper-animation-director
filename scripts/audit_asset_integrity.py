#!/usr/bin/env python3
"""Audit PNG/JPEG assets for alpha, crop safety, empty content, and suspicious plates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from PIL import Image


EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def iter_images(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        path = path.expanduser().resolve()
        if path.is_dir():
            files.extend(item for item in path.rglob("*") if item.suffix.lower() in EXTENSIONS)
        elif path.suffix.lower() in EXTENSIONS:
            files.append(path)
    return sorted(set(files))


def audit(path: Path, kind: str, margin: int, alpha_threshold: int) -> dict:
    item = {"file": str(path), "errors": [], "warnings": []}
    try:
        with Image.open(path) as source:
            image = source.convert("RGBA")
    except Exception as exc:
        item["errors"].append(f"cannot open image: {exc}")
        return item
    width, height = image.size
    alpha = image.getchannel("A")
    mask = alpha.point(lambda value: 255 if value > alpha_threshold else 0)
    bbox = mask.getbbox()
    opaque_count = sum(1 for value in alpha.getdata() if value > alpha_threshold)
    coverage = opaque_count / max(1, width * height)
    item.update({"width": width, "height": height, "mode": "RGBA", "alpha_coverage": round(coverage, 6), "bbox": bbox})
    if not bbox:
        item["errors"].append("image is fully transparent")
        return item
    left, top, right, bottom = bbox
    touches = {
        "left": left <= margin,
        "top": top <= margin,
        "right": right >= width - margin,
        "bottom": bottom >= height - margin,
    }
    item["touches_edges"] = [name for name, value in touches.items() if value]
    if kind in {"character", "prop", "effect"}:
        if source.mode not in {"RGBA", "LA", "PA"} and "transparency" not in source.info:
            item["errors"].append("isolated asset has no alpha channel")
        if item["touches_edges"]:
            item["warnings"].append("visible pixels touch crop safety margin: " + ", ".join(item["touches_edges"]))
        if coverage > 0.94:
            item["warnings"].append("isolated asset covers almost the entire rectangle; check for an unremoved background plate")
        if coverage < 0.002:
            item["warnings"].append("very little visible content; check scale or accidental key removal")
    if width < 64 or height < 64:
        item["warnings"].append("asset is unusually small for animation")
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--kind", choices=("character", "prop", "effect", "background"), default="character")
    parser.add_argument("--margin", type=int, default=2)
    parser.add_argument("--alpha-threshold", type=int, default=8)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    files = iter_images(args.paths)
    if not files:
        raise SystemExit("No supported images found")
    items = [audit(path, args.kind, args.margin, args.alpha_threshold) for path in files]
    errors = sum(len(item["errors"]) for item in items)
    warnings = sum(len(item["warnings"]) for item in items)
    payload = {"ok": errors == 0 and (warnings == 0 or not args.strict), "files": len(items), "errors": errors, "warnings": warnings, "items": items}
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in items:
            print(f"{item['file']} — {item.get('width', '?')}x{item.get('height', '?')} coverage={item.get('alpha_coverage', '?')}")
            for message in item["errors"]:
                print(f"  [ERROR] {message}")
            for message in item["warnings"]:
                print(f"  [WARNING] {message}")
        print(f"Asset audit: {errors} error(s), {warnings} warning(s) across {len(items)} file(s)")
    raise SystemExit(1 if errors or (args.strict and warnings) else 0)


if __name__ == "__main__":
    main()
