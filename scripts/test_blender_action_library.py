from __future__ import annotations

import unittest

from audit_blender_action_library import audit
from blender_action_library import ACTION_PRESETS, preset


class BlenderActionLibraryTests(unittest.TestCase):
    def manifest(self) -> dict:
        return {
            "schema_version": 1,
            "engine": "blender",
            "plane": "camera-facing-xz",
            "actions": [
                {
                    "id": "paper-impact",
                    "kind": "rigid-body-collision",
                    "required_roles": ["active", "impactor", "support"],
                    "bake_required": True,
                    "parameters": {},
                }
            ],
            "release_contract": {
                "editable_blend_required": True,
                "baked_cache_required": True,
                "build_record_required": True,
                "transparent_master_required": True,
                "placeholder_media_forbidden": True,
            },
        }

    def test_manifest_passes(self) -> None:
        self.assertEqual(audit(self.manifest()), [])

    def test_unbaked_action_is_rejected(self) -> None:
        manifest = self.manifest()
        manifest["actions"][0]["bake_required"] = False
        self.assertTrue(any("bake_required" in item for item in audit(manifest)))

    def test_runtime_presets_are_copy_safe(self) -> None:
        value = preset("rigid-drop")
        value["mass"] = 99
        self.assertNotEqual(ACTION_PRESETS["rigid-drop"]["mass"], 99)


if __name__ == "__main__":
    unittest.main()
