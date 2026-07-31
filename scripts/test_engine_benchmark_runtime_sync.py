#!/usr/bin/env python3
"""Ensure engine benchmarks use the project runtime source of truth."""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sync_engine_benchmark_runtime import sync


class EngineBenchmarkRuntimeSyncTests(unittest.TestCase):
    def test_benchmark_runtime_files_match_project_template(self) -> None:
        skill_root = pathlib.Path(__file__).resolve().parent.parent
        self.assertEqual(sync(skill_root, check=True), [])


if __name__ == "__main__":
    unittest.main()
