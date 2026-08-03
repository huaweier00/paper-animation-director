#!/usr/bin/env python3
"""Bind a release index to exact shot-release records and the final master."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve(project: Path, value: Any, label: str) -> Path:
    if not nonempty(value):
        raise ValueError(f"{label}: missing path")
    raw = str(value)
    if raw.startswith(("http://", "https://", "//", "data:")):
        raise ValueError(f"{label}: runtime-network paths are forbidden")
    root = project.resolve()
    path = (root / raw.removeprefix("./")).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label}: path escapes the project root") from exc
    if not path.is_file():
        raise ValueError(f"{label}: file does not exist: {path}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bind(data: dict[str, Any], *, project: Path) -> dict[str, Any]:
    if data.get("schema_version") != 1:
        raise ValueError("release-index schema_version must be 1")
    shots = data.get("ordered_shots")
    if not isinstance(shots, list) or not shots:
        raise ValueError("ordered_shots: expected a non-empty list")
    for index, item in enumerate(shots):
        if not isinstance(item, dict):
            raise ValueError(f"ordered_shots[{index}]: expected object")
        release = resolve(project, item.get("release"), f"ordered_shots[{index}].release")
        item["release_sha256"] = sha256(release)
    master = data.get("master")
    if not isinstance(master, dict):
        raise ValueError("master: expected object")
    master["sha256"] = sha256(resolve(project, master.get("path"), "master.path"))
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    index = args.index.expanduser().resolve()
    project = args.project.expanduser().resolve() if args.project else index.parent
    output = args.output.expanduser().resolve() if args.output else index
    try:
        data = json.loads(index.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("release index root must be an object")
        bound = bind(data, project=project)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(bound, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = {"ok": True, "output": str(output)}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"ok": False, "error": str(exc)}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"PASS: bound {result['output']}" if result["ok"] else f"FAIL: {result['error']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
