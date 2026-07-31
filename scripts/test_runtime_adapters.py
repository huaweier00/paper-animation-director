#!/usr/bin/env python3
"""Run the bundled JavaScript adapter tests from Python discovery."""

from __future__ import annotations

import pathlib
import subprocess
import unittest


class RuntimeAdapterTests(unittest.TestCase):
    def test_node_runtime_adapters(self) -> None:
        scripts = [
            pathlib.Path(__file__).with_name("test_pixi_runtime.mjs"),
            pathlib.Path(__file__).with_name("test_rive_runtime.mjs"),
            pathlib.Path(__file__).with_name("test_three_runtime.mjs"),
        ]
        for script in scripts:
            with self.subTest(script=script.name):
                result = subprocess.run(
                    ["node", "--test", str(script)],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
