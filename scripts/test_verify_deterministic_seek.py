#!/usr/bin/env python3
"""Unit tests for ordered/shuffled seek evidence comparison."""

from __future__ import annotations

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from verify_deterministic_seek import (
    compare_capture_dirs,
    parse_times,
    shuffled_times,
)


def write_frame(directory: Path, index: int, time: str, payload: bytes) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"frame-{index:02d}-at-{time}s.png").write_bytes(payload)


class DeterministicSeekTests(unittest.TestCase):
    def test_equal_frames_pass_regardless_of_capture_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="seek-proof-") as directory:
            root = Path(directory)
            ordered = root / "ordered"
            shuffled = root / "shuffled"
            times = parse_times("0,2.2,5.65,9.8")
            for index, time in enumerate(times):
                label = str(time)
                payload = f"pixels:{label}".encode()
                write_frame(ordered, index, label, payload)
            for index, time in enumerate(shuffled_times(times)):
                label = str(time)
                payload = f"pixels:{label}".encode()
                write_frame(shuffled, index, label, payload)
            samples, errors = compare_capture_dirs(ordered, shuffled, times)
            self.assertEqual(errors, [])
            self.assertEqual(len(samples), 4)
            self.assertTrue(all(item["equal"] for item in samples))

    def test_pixel_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="seek-proof-") as directory:
            root = Path(directory)
            ordered = root / "ordered"
            shuffled = root / "shuffled"
            times = [Decimal("0"), Decimal("1")]
            write_frame(ordered, 0, "0", b"same")
            write_frame(ordered, 1, "1", b"ordered")
            write_frame(shuffled, 0, "1", b"shuffled")
            write_frame(shuffled, 1, "0", b"same")
            _, errors = compare_capture_dirs(ordered, shuffled, times)
            self.assertTrue(any("1s" in error and "differ" in error for error in errors), errors)

    def test_duplicate_or_negative_times_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate"):
            parse_times("0,1,1")
        with self.assertRaisesRegex(ValueError, "non-negative"):
            parse_times("0,-1")


if __name__ == "__main__":
    unittest.main()
