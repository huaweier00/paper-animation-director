from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from audit_rive_rig import audit


class AuditRiveRigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        asset = self.root / "hero.riv"
        asset.write_bytes(b"RIVE")
        self.digest = hashlib.sha256(asset.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def benchmark_manifest(self) -> dict:
        return {
            "schema_version": 1,
            "rig_id": "hero",
            "profile": "benchmark-linear",
            "asset": "hero.riv",
            "artboard": "Character",
            "state_machine_forbidden": True,
            "animations": {
                "locomotion": {
                    "name": "Walk",
                    "playback": "native",
                    "duration_seconds": None,
                }
            },
            "anchors": {},
            "facing": ["right"],
        }

    def inspection(self) -> dict:
        return {
            "ok": True,
            "asset_sha256": self.digest,
            "artboards": [
                {
                    "name": "Character",
                    "animations": ["Walk"],
                    "state_machines": [],
                }
            ],
        }

    def test_benchmark_contract_passes_runtime_inspection(self) -> None:
        errors, warnings = audit(
            self.benchmark_manifest(),
            root=self.root,
            phase="release",
            inspection=self.inspection(),
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_missing_animation_is_rejected(self) -> None:
        inspection = self.inspection()
        inspection["artboards"][0]["animations"] = ["Idle"]
        errors, _ = audit(
            self.benchmark_manifest(),
            root=self.root,
            phase="release",
            inspection=inspection,
        )
        self.assertTrue(any("animation not found" in item for item in errors))

    def test_production_profile_requires_standard_anchors(self) -> None:
        manifest = self.benchmark_manifest()
        manifest["profile"] = "production-hero"
        errors, _ = audit(
            manifest,
            root=self.root,
            phase="release",
            inspection=self.inspection(),
        )
        self.assertTrue(any("animations.idle" in item for item in errors))
        self.assertTrue(any("anchors.head" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
