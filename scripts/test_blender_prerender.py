#!/usr/bin/env python3
"""Unit tests for the Blender pre-render contract and scaffold integration."""

from __future__ import annotations

import struct
import tempfile
import unittest
from pathlib import Path

from render_blender_prerender import png_header, validate_frames
from scaffold_hybrid_shot import layer_markup


def rgba_png_header(width: int, height: int, marker: int) -> bytes:
    # validate_frames intentionally reads only the required PNG signature/IHDR
    # and hashes the complete file; a tiny distinct payload is enough here.
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
        + bytes([marker])
    )


class BlenderPrerenderTests(unittest.TestCase):
    def test_rgba_sequence_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="blender-prerender-test-") as directory:
            root = Path(directory)
            for index in range(1, 5):
                (root / f"frame_{index:04d}.png").write_bytes(rgba_png_header(96, 54, index))
            frames = validate_frames(root, expected_count=4, expected_width=96, expected_height=54)
            self.assertEqual(len(frames), 4)
            self.assertEqual(png_header(frames[0]), (96, 54, 6))

    def test_missing_frame_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="blender-prerender-test-") as directory:
            root = Path(directory)
            for index in (1, 3, 4):
                (root / f"frame_{index:04d}.png").write_bytes(rgba_png_header(96, 54, index))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                validate_frames(root, expected_count=4, expected_width=96, expected_height=54)

    def test_blender_scaffold_is_a_seekable_local_video(self) -> None:
        markup = layer_markup("scene-impact", "blender", 0, 2.0)
        self.assertIn("<video", markup)
        self.assertIn('class="engine-layer clip"', markup)
        self.assertIn('data-start="0"', markup)
        self.assertIn('data-duration="2"', markup)
        self.assertIn(
            'data-required-asset="./shots/scene-impact/assets/prerender/scene-impact-alpha.webm"',
            markup,
        )
        self.assertIn('src="./assets/runtime/placeholders/pending-blender.webm"', markup)
        self.assertNotIn("replace-with-prerender", markup)


if __name__ == "__main__":
    unittest.main()
