#!/usr/bin/env python3
"""Create a high-quality H.264 social derivative and gate it with VMAF."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def probe(path: Path) -> dict:
    process = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", str(path),
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return json.loads(process.stdout)


def vmaf_score(distorted: Path, reference: Path) -> float:
    process = subprocess.run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(distorted), "-i", str(reference),
        "-lavfi", "[0:v]setpts=PTS-STARTPTS[dist];[1:v]setpts=PTS-STARTPTS[ref];[dist][ref]libvmaf=n_threads=8",
        "-an", "-f", "null", "-",
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = process.stdout + process.stderr
    if process.returncode != 0:
        raise RuntimeError("VMAF comparison failed:\n" + output[-3000:])
    match = re.search(r"VMAF score:\s*([0-9.]+)", output)
    if not match:
        raise RuntimeError("VMAF score was not reported")
    return float(match.group(1))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--crf", type=float, default=20)
    parser.add_argument("--preset", default="slow", choices=("medium", "slow", "slower", "veryslow"))
    parser.add_argument("--vmaf-floor", type=float, default=95)
    parser.add_argument("--no-vmaf", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required")
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if source == output:
        raise SystemExit("Input and output must be different files")
    if output.exists() and not args.overwrite:
        raise SystemExit(f"Output exists; pass --overwrite to replace it: {output}")
    if not 0 <= args.crf <= 35 or not 0 <= args.vmaf_floor <= 100:
        raise SystemExit("crf must be 0–35 and vmaf-floor 0–100")
    output.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(prefix=output.stem + "-", suffix=".mp4", dir=output.parent, delete=False)
    temporary = Path(handle.name)
    handle.close()
    temporary.unlink(missing_ok=True)
    try:
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y", "-i", str(source),
            "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
            "-profile:v", "high", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
            "-color_trc", "bt709", "-movflags", "+faststart", "-c:a", "copy", str(temporary),
        ], check=True)
        score = None if args.no_vmaf else vmaf_score(temporary, source)
        if score is not None and score < args.vmaf_floor:
            raise RuntimeError(f"VMAF {score:.3f} is below required floor {args.vmaf_floor:.3f}; lower CRF and retry")
        original = probe(source)
        derivative = probe(temporary)
        original_size = int(original["format"]["size"])
        derivative_size = int(derivative["format"]["size"])
        os.replace(temporary, output)
        payload = {
            "input": str(source),
            "output": str(output),
            "original_bytes": original_size,
            "output_bytes": derivative_size,
            "reduction_percent": round((1 - derivative_size / original_size) * 100, 3),
            "vmaf": None if score is None else round(score, 6),
            "crf": args.crf,
            "preset": args.preset,
            "duration": float(derivative["format"]["duration"]),
            "streams": derivative["streams"],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    main()
