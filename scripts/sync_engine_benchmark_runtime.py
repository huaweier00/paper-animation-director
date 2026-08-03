#!/usr/bin/env python3
"""Sync verified project-template runtime modules into engine benchmarks."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


BENCHMARK_FILES = {
    "pixi-paper-effects": (
        "hybrid-bootstrap.js",
        "hybrid-runtime.js",
        "deterministic.js",
        "adapters/pixi-seekable.js",
        "effects/paper-particles.js",
        "effects/paper-masks.js",
    ),
    "rive-linear-character": (
        "hybrid-bootstrap.js",
        "hybrid-runtime.js",
        "deterministic.js",
        "adapters/rive-seekable.js",
    ),
    "three-paper-diorama": (
        "hybrid-bootstrap.js",
        "hybrid-runtime.js",
        "deterministic.js",
        "adapters/three-seekable.js",
        "scenes/paper-diorama-2_5d.js",
        "scenes/declarative-paper-2_5d.js",
    ),
}


def sync(skill_root: Path, check: bool = False) -> list[str]:
    runtime = skill_root / "assets" / "project-template" / "runtime"
    benchmark_root = skill_root / "assets" / "engine-benchmarks"
    differences: list[str] = []
    for benchmark, relative_paths in BENCHMARK_FILES.items():
        for relative_path in relative_paths:
            source = runtime / relative_path
            target = benchmark_root / benchmark / "assets" / "runtime" / relative_path
            if not source.is_file():
                raise FileNotFoundError(f"missing runtime source: {source}")
            if target.is_file() and target.read_bytes() == source.read_bytes():
                continue
            differences.append(f"{benchmark}:{relative_path}")
            if not check:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    return differences


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift and exit non-zero instead of copying source-of-truth files",
    )
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parent.parent
    differences = sync(skill_root, check=args.check)
    if differences:
        verb = "drift" if args.check else "synced"
        print(f"{verb}:")
        print("\n".join(f"- {item}" for item in differences))
        if args.check:
            raise SystemExit(1)
    else:
        print("engine benchmark runtimes are in sync")


if __name__ == "__main__":
    main()
