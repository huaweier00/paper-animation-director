#!/usr/bin/env python3
"""Capture ordered/shuffled HyperFrames seeks and write a byte-stability report."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


FRAME_TIME_RE = re.compile(r"-at-(-?(?:\d+(?:\.\d*)?|\.\d+))s\.png$", re.IGNORECASE)


def parse_times(value: str) -> list[Decimal]:
    times: list[Decimal] = []
    for raw in value.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            time = Decimal(raw)
        except InvalidOperation as exc:
            raise ValueError(f"invalid seek time {raw!r}") from exc
        if not time.is_finite() or time < 0:
            raise ValueError(f"seek times must be finite and non-negative, got {raw!r}")
        if time in times:
            raise ValueError(f"duplicate seek time {raw!r}")
        times.append(time)
    if len(times) < 2:
        raise ValueError("provide at least two unique seek times")
    return times


def format_time(value: Decimal) -> str:
    normalized = format(value.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized or "0"


def shuffled_times(times: list[Decimal]) -> list[Decimal]:
    shuffled = list(reversed(times[::2])) + list(times[1::2])
    if shuffled == times:
        shuffled = [*times[1:], times[0]]
    return shuffled


def index_frames(directory: Path) -> dict[Decimal, Path]:
    frames: dict[Decimal, Path] = {}
    for path in sorted(directory.glob("*.png")):
        match = FRAME_TIME_RE.search(path.name)
        if not match:
            continue
        time = Decimal(match.group(1))
        if time in frames:
            raise ValueError(
                f"duplicate frame for {format_time(time)}s in {directory}: "
                f"{frames[time].name}, {path.name}"
            )
        frames[time] = path
    return frames


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compare_capture_dirs(
    ordered_dir: Path,
    shuffled_dir: Path,
    times: list[Decimal],
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    ordered = index_frames(ordered_dir)
    shuffled = index_frames(shuffled_dir)
    expected = set(times)
    for label, frames in (("ordered", ordered), ("shuffled", shuffled)):
        missing = sorted(expected - set(frames))
        extra = sorted(set(frames) - expected)
        if missing:
            errors.append(
                f"{label}: missing frames at {', '.join(format_time(item) for item in missing)}s"
            )
        if extra:
            errors.append(
                f"{label}: unexpected frames at {', '.join(format_time(item) for item in extra)}s"
            )

    samples: list[dict[str, Any]] = []
    for time in times:
        first = ordered.get(time)
        second = shuffled.get(time)
        if first is None or second is None:
            continue
        first_hash = sha256(first)
        second_hash = sha256(second)
        equal = first_hash == second_hash and first.read_bytes() == second.read_bytes()
        samples.append(
            {
                "time": float(time),
                "ordered": str(first),
                "shuffled": str(second),
                "sha256": first_hash,
                "shuffled_sha256": second_hash,
                "equal": equal,
            }
        )
        if not equal:
            errors.append(f"{format_time(time)}s: ordered and shuffled PNGs differ")
    return samples, errors


def resolve_hyperframes(project: Path, requested: str | None) -> Path:
    if requested:
        path = Path(requested).expanduser().absolute()
    else:
        path = project / "node_modules" / ".bin" / "hyperframes"
    if not path.is_file():
        raise ValueError(
            f"local HyperFrames binary not found: {path}. "
            "Install the pinned lockfile first; deterministic proof never falls back to an online npx fetch."
        )
    return path


def run_snapshot(
    hyperframes: Path,
    project: Path,
    output: Path,
    times: list[Decimal],
    *,
    timeout_ms: int,
) -> list[str]:
    command = [
        str(hyperframes),
        "snapshot",
        str(project),
        "--output",
        str(output),
        "--at",
        ",".join(format_time(item) for item in times),
        "--no-end",
        "--describe",
        "false",
        "--timeout",
        str(timeout_ms),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValueError(f"snapshot failed: {detail}")
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--at", required=True, help="comma-separated absolute seconds")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--hyperframes", help="path to the pinned local HyperFrames binary")
    parser.add_argument("--timeout", type=int, default=5000)
    parser.add_argument(
        "--compare-only",
        action="store_true",
        help="do not capture; compare ordered/ and shuffled/ under --output",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        project = args.project.expanduser().resolve()
        if not project.is_dir():
            raise ValueError(f"project does not exist: {project}")
        times = parse_times(args.at)
        run_name = datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
        output = (
            args.output.expanduser().resolve()
            if args.output
            else project / "shots" / args.shot_id / "review" / "deterministic-seek" / run_name
        )
        ordered_dir = output / "ordered"
        shuffled_dir = output / "shuffled"
        if not args.compare_only:
            if output.exists() and any(output.iterdir()):
                raise ValueError(f"refusing to mix evidence into non-empty output: {output}")
            ordered_dir.mkdir(parents=True, exist_ok=True)
            shuffled_dir.mkdir(parents=True, exist_ok=True)
            hyperframes = resolve_hyperframes(project, args.hyperframes)
            ordered_command = run_snapshot(
                hyperframes, project, ordered_dir, times, timeout_ms=args.timeout
            )
            shuffled_command = run_snapshot(
                hyperframes,
                project,
                shuffled_dir,
                shuffled_times(times),
                timeout_ms=args.timeout,
            )
        else:
            ordered_command = []
            shuffled_command = []
        samples, errors = compare_capture_dirs(ordered_dir, shuffled_dir, times)
        result = {
            "schema_version": 1,
            "shot_id": args.shot_id,
            "clock": "hyperframes-absolute-seconds",
            "comparison": "byte-identical PNG comparison between ordered and shuffled seeks",
            "ordered_times": [float(item) for item in times],
            "shuffled_times": [float(item) for item in shuffled_times(times)],
            "ordered_directory": str(ordered_dir),
            "shuffled_directory": str(shuffled_dir),
            "ordered_command": ordered_command,
            "shuffled_command": shuffled_command,
            "samples": samples,
            "all_equal": not errors and len(samples) == len(times),
            "errors": errors,
            "result": "pass" if not errors and len(samples) == len(times) else "fail",
        }
        output.mkdir(parents=True, exist_ok=True)
        report_path = output / "deterministic-seek-report.json"
        report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        result["report"] = str(report_path)
    except (OSError, ValueError) as exc:
        result = {
            "schema_version": 1,
            "shot_id": args.shot_id,
            "all_equal": False,
            "errors": [str(exc)],
            "result": "fail",
        }

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
        if result.get("result") == "pass":
            print(f"PASS: {len(result['samples'])} seek samples are byte-identical")
            print(f"Report: {result['report']}")
        else:
            print("FAIL: deterministic seek proof did not pass")
    return 0 if result.get("result") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
