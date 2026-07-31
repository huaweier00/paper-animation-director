#!/usr/bin/env python3
"""Produce and audit a baked Blender paper-animation layer for HyperFrames."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any


FRAME_RE = re.compile(r"^frame_(\d{4})\.png$")
SHOT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_header(path: Path) -> tuple[int, int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"not a PNG file: {path}")
        length = struct.unpack(">I", handle.read(4))[0]
        chunk_type = handle.read(4)
        if chunk_type != b"IHDR" or length != 13:
            raise ValueError(f"invalid PNG IHDR: {path}")
        width, height, _depth, color_type, _compression, _filter, _interlace = struct.unpack(
            ">IIBBBBB", handle.read(13)
        )
    return width, height, color_type


def resolve_executable(explicit: str | None, name: str, common: list[Path]) -> str:
    if explicit:
        path = shutil.which(explicit) or (explicit if Path(explicit).is_file() else None)
        if path:
            return str(path)
        raise ValueError(f"{name} executable does not exist: {explicit}")
    discovered = shutil.which(name)
    if discovered:
        return discovered
    for path in common:
        if path.is_file():
            return str(path)
    raise ValueError(f"{name} is required but was not found")


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def blender_version(blender: str) -> str:
    result = subprocess.run([blender, "--version"], check=True, text=True, capture_output=True)
    first = result.stdout.splitlines()[0] if result.stdout else "Blender unknown"
    return first.removeprefix("Blender ").strip()


def ffprobe_json(ffprobe: str, media: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_name,width,height,pix_fmt,avg_frame_rate,nb_frames",
            "-of",
            "json",
            str(media),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def validate_frames(
    frames_dir: Path,
    *,
    expected_count: int,
    expected_width: int,
    expected_height: int,
) -> list[Path]:
    frames = sorted(path for path in frames_dir.iterdir() if FRAME_RE.match(path.name))
    expected_names = [f"frame_{index:04d}.png" for index in range(1, expected_count + 1)]
    actual_names = [path.name for path in frames]
    if actual_names != expected_names:
        missing = sorted(set(expected_names) - set(actual_names))
        extra = sorted(set(actual_names) - set(expected_names))
        raise ValueError(f"frame sequence is incomplete; missing={missing[:8]}, extra={extra[:8]}")
    types: set[int] = set()
    for path in frames:
        width, height, color_type = png_header(path)
        if (width, height) != (expected_width, expected_height):
            raise ValueError(f"unexpected frame dimensions at {path}: {width}x{height}")
        types.add(color_type)
    if types != {6}:
        raise ValueError(f"all Blender frames must be RGBA PNG (PNG color type 6), found {sorted(types)}")
    proof_indices = [0, max(0, round(expected_count * 0.42) - 1), max(0, round(expected_count * 0.68) - 1), -1]
    proof_hashes = [sha256(frames[index]) for index in proof_indices]
    if len(set(proof_hashes)) < 3:
        raise ValueError("rendered sequence does not show enough visual change across proof frames")
    return frames


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--shot-id",
        help="name the HyperFrames media <shot-id>-alpha.webm; defaults to paper-impact-alpha.webm",
    )
    parser.add_argument("--blender")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--frames", type=int, default=48)
    parser.add_argument("--samples", type=int, default=32)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.shot_id and not SHOT_ID_RE.fullmatch(args.shot_id):
        raise SystemExit("--shot-id must be kebab-case")

    output = args.output.expanduser().resolve()
    if output.exists() and any(output.iterdir()) and not args.force:
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {output}; pass --force after review")
    output.mkdir(parents=True, exist_ok=True)
    frames_dir = output / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    blender = resolve_executable(
        args.blender,
        "blender",
        [Path("/Applications/Blender.app/Contents/MacOS/Blender")],
    )
    ffmpeg = resolve_executable(args.ffmpeg, "ffmpeg", [])
    ffprobe = resolve_executable(args.ffprobe, "ffprobe", [])
    builder = Path(__file__).resolve().with_name("build_blender_paper_impact.py")
    run(
        [
            blender,
            "--background",
            "--factory-startup",
            "--python-exit-code",
            "1",
            "--python",
            str(builder),
            "--",
            "--output",
            str(output),
            "--width",
            str(args.width),
            "--height",
            str(args.height),
            "--fps",
            str(args.fps),
            "--frames",
            str(args.frames),
            "--samples",
            str(args.samples),
        ]
    )

    frames = validate_frames(
        frames_dir,
        expected_count=args.frames,
        expected_width=args.width,
        expected_height=args.height,
    )
    build_record_path = output / "blender-build.json"
    build_record = json.loads(build_record_path.read_text(encoding="utf-8"))
    if build_record.get("physics", {}).get("baked") is not True:
        raise ValueError("Blender rigid-body point cache was not baked")

    media = output / (f"{args.shot_id}-alpha.webm" if args.shot_id else "paper-impact-alpha.webm")
    run(
        [
            ffmpeg,
            "-y",
            "-framerate",
            str(args.fps),
            "-start_number",
            "1",
            "-i",
            str(frames_dir / "frame_%04d.png"),
            "-an",
            "-c:v",
            "libvpx-vp9",
            "-lossless",
            "1",
            "-auto-alt-ref",
            "0",
            "-pix_fmt",
            "yuva420p",
            "-metadata:s:v:0",
            "alpha_mode=1",
            str(media),
        ]
    )
    probe = ffprobe_json(ffprobe, media)
    streams = probe.get("streams", [])
    if len(streams) != 1 or streams[0].get("codec_name") != "vp9":
        raise ValueError(f"expected one VP9 video stream, got {streams}")
    if (streams[0].get("width"), streams[0].get("height")) != (args.width, args.height):
        raise ValueError(f"encoded video dimensions do not match requested dimensions: {streams[0]}")

    proof_frames = [frames[0], frames[round(args.frames * 0.42) - 1], frames[round(args.frames * 0.68) - 1], frames[-1]]
    manifest = {
        "schema_version": 1,
        "engine": "blender",
        "engine_version": blender_version(blender),
        "delivery": "pre-render-alpha",
        "clock": "hyperframes-media-seek",
        "source": {
            "blend": "paper-impact.blend",
            "builder": builder.name,
            "build_record": build_record_path.name,
            "physics_baked": True,
            "cache_preserved_in_blend": True,
            "external_cache": bool(build_record.get("physics", {}).get("cache_external")),
        },
        "render": {
            "frame_start": 1,
            "frame_end": args.frames,
            "frame_count": args.frames,
            "fps": args.fps,
            "duration_seconds": args.frames / args.fps,
            "width": args.width,
            "height": args.height,
            "png_color_type": 6,
        },
        "media": {
            "path": media.name,
            "codec": "vp9",
            "pixel_format_requested": "yuva420p",
            "alpha_mode": 1,
            "sha256": sha256(media),
            "bytes": media.stat().st_size,
            "ffprobe": probe,
        },
        "proof_frames": [
            {"path": path.relative_to(output).as_posix(), "sha256": sha256(path)} for path in proof_frames
        ],
    }
    manifest_path = output / "prerender-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(output), "manifest": str(manifest_path)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
