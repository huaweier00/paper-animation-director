#!/usr/bin/env python3
"""Unit tests for dependency-lock and offline-policy doctor checks."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from doctor_paper_pipeline import audit_lock, selected_engines


class PaperPipelineDoctorTests(unittest.TestCase):
    def test_exact_package_and_lock_versions_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="paper-doctor-") as directory:
            root = Path(directory)
            package = {
                "name": "demo",
                "dependencies": {"gsap": "3.15.0"},
                "devDependencies": {"hyperframes": "0.7.83"},
            }
            lock = {
                "name": "demo",
                "lockfileVersion": 3,
                "packages": {
                    "": package,
                    "node_modules/gsap": {"version": "3.15.0"},
                    "node_modules/hyperframes": {"version": "0.7.83"},
                },
            }
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            (root / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
            errors, warnings, versions = audit_lock(root)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])
            self.assertEqual(versions["gsap"], "3.15.0")

    def test_lock_drift_and_semver_ranges_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="paper-doctor-") as directory:
            root = Path(directory)
            package = {
                "name": "demo",
                "dependencies": {"gsap": "^3.15.0"},
                "devDependencies": {},
            }
            lock = {
                "name": "demo",
                "lockfileVersion": 3,
                "packages": {
                    "": {
                        "name": "demo",
                        "dependencies": {"gsap": "3.14.0"},
                        "devDependencies": {},
                    },
                    "node_modules/gsap": {"version": "3.14.0"},
                },
            }
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            (root / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
            errors, _, _ = audit_lock(root)
            self.assertTrue(any("exact version" in error for error in errors), errors)

    def test_selected_engines_are_discovered_from_shots(self) -> None:
        with tempfile.TemporaryDirectory(prefix="paper-doctor-") as directory:
            root = Path(directory)
            plan = root / "shots" / "scene-01" / "engine-plan.json"
            plan.parent.mkdir(parents=True)
            plan.write_text(
                json.dumps({"engines": ["gsap-dom", "pixijs-webgpu"]}),
                encoding="utf-8",
            )
            self.assertEqual(selected_engines(root), {"gsap-dom", "pixijs-webgpu"})


if __name__ == "__main__":
    unittest.main()
