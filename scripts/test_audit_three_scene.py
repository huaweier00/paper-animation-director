from __future__ import annotations

import unittest
from pathlib import Path

from audit_three_scene import audit


class AuditThreeSceneTests(unittest.TestCase):
    def manifest(self) -> dict:
        return {
            "schema_version": 1,
            "previous_frame_effects_forbidden": True,
            "local_assets_only": True,
            "camera": {"kind": "perspective", "near": 0.1, "far": 100},
            "layers": [
                {
                    "id": "back",
                    "kind": "plane",
                    "depth": -2,
                    "motion": {"kind": "static"},
                },
                {
                    "id": "front",
                    "kind": "shape",
                    "depth": 1,
                    "points": [[0, 0], [1, 0], [0, 1]],
                    "motion": {"kind": "bob"},
                },
            ],
            "occlusion_order": ["back", "front"],
        }

    def test_valid_depth_scene_passes(self) -> None:
        errors, warnings = audit(self.manifest(), root=Path("."), phase="release")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_depth_order_drift_is_rejected(self) -> None:
        manifest = self.manifest()
        manifest["occlusion_order"] = ["front", "back"]
        errors, _ = audit(manifest, root=Path("."), phase="release")
        self.assertTrue(any("ascending depth" in item for item in errors))

    def test_required_model_must_be_local_at_release(self) -> None:
        manifest = self.manifest()
        manifest["layers"].append(
            {
                "id": "model",
                "kind": "model",
                "depth": 0,
                "source": "missing.glb",
                "motion": {"kind": "static"},
            }
        )
        manifest["occlusion_order"] = ["back", "model", "front"]
        errors, _ = audit(manifest, root=Path("."), phase="release")
        self.assertTrue(any("file not found" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
