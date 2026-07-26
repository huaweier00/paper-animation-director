#!/usr/bin/env python3
"""Probe narration files for duration, streams, loudness, and silence intervals using FFmpeg."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


AUDIO_EXTENSIONS = {".mp3", ".wav", ".aiff", ".aif", ".m4a", ".aac", ".flac", ".ogg"}


def collect(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        path = path.expanduser().resolve()
        if path.is_dir():
            files.extend(item for item in path.rglob("*") if item.suffix.lower() in AUDIO_EXTENSIONS)
        elif path.suffix.lower() in AUDIO_EXTENSIONS:
            files.append(path)
    return sorted(set(files))


def run_text(command: list[str]) -> str:
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return process.stdout + process.stderr


def probe(path: Path, silence_noise: str, silence_duration: float) -> dict:
    raw = run_text([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size,bit_rate:stream=codec_name,codec_type,sample_rate,channels",
        "-of", "json", str(path),
    ])
    data = json.loads(raw)
    audio_stream = next((stream for stream in data.get("streams", []) if stream.get("codec_type") == "audio"), {})
    duration = float(data.get("format", {}).get("duration", 0))
    analysis = run_text([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", f"silencedetect=noise={silence_noise}:d={silence_duration},ebur128=peak=true",
        "-f", "null", "-",
    ])
    silence_starts = [float(value) for value in re.findall(r"silence_start:\s*([0-9.]+)", analysis)]
    silence_ends = [float(value) for value in re.findall(r"silence_end:\s*([0-9.]+)", analysis)]
    intervals = []
    for index, start in enumerate(silence_starts):
        end = silence_ends[index] if index < len(silence_ends) else duration
        intervals.append({"start": round(start, 6), "end": round(end, 6), "duration": round(max(0, end - start), 6)})
    loudness_matches = re.findall(r"\bI:\s*(-?inf|[-0-9.]+)\s*LUFS", analysis)
    peak_matches = re.findall(r"\bPeak:\s*(-?inf|[-0-9.]+)\s*dBFS", analysis)
    leading = intervals[0]["duration"] if intervals and intervals[0]["start"] <= 0.02 else 0
    trailing = intervals[-1]["duration"] if intervals and abs(intervals[-1]["end"] - duration) <= 0.05 else 0
    return {
        "file": str(path),
        "duration": round(duration, 6),
        "codec": audio_stream.get("codec_name"),
        "sample_rate": int(audio_stream.get("sample_rate", 0) or 0),
        "channels": int(audio_stream.get("channels", 0) or 0),
        "integrated_lufs": None if not loudness_matches or loudness_matches[-1] == "-inf" else float(loudness_matches[-1]),
        "true_peak_dbfs": None if not peak_matches or peak_matches[-1] == "-inf" else float(peak_matches[-1]),
        "leading_silence": round(float(leading), 6),
        "trailing_silence": round(float(trailing), 6),
        "silence_intervals": intervals,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--silence-noise", default="-45dB")
    parser.add_argument("--silence-duration", type=float, default=0.15)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required")
    files = collect(args.paths)
    if not files:
        raise SystemExit("No supported audio files found")
    items = [probe(path, args.silence_noise, args.silence_duration) for path in files]
    payload = {"items": items, "count": len(items), "total_duration": round(sum(item["duration"] for item in items), 6)}
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Saved {output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
