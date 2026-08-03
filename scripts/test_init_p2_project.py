#!/usr/bin/env python3
"""Integration tests for portable P2 project initialization."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("init_paper_project.py")
SKILL_ROOT = SCRIPT.parent.parent


class InitP2ProjectTests(unittest.TestCase):
    def test_new_project_contains_portable_p2_runtime_tools_and_manifests(self) -> None:
        with tempfile.TemporaryDirectory(prefix="paper-p2-init-") as directory:
            output = Path(directory) / "project"
            manifest = (
                SKILL_ROOT
                / "assets"
                / "project-template"
                / "manifests"
                / "story-manifest.example.json"
            )
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--manifest",
                    str(manifest),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            for relative in (
                "tools/paper-pipeline/build_routed_shot.py",
                "tools/paper-pipeline/bind_release_evidence.py",
                "tools/paper-pipeline/audit_motion_contract.py",
                "tools/paper-pipeline/audit_rendered_motion.py",
                "tools/paper-pipeline/build_motion_review.py",
                "tools/paper-pipeline/compile_motion_contract.py",
                "tools/paper-pipeline/inspect_rive_asset.mjs",
                "tools/paper-pipeline/probe_webgpu_runtime.mjs",
                "tools/paper-pipeline/profile_multi_engine.mjs",
                "tools/paper-pipeline/blender_action_library.py",
                "tools/assets/project-template/manifests/rive-character-rig.example.json",
                "tools/assets/project-template/manifests/three-declarative-scene.example.json",
                "tools/assets/project-template/manifests/webgpu-capability.example.json",
                "tools/assets/project-template/manifests/performance-budget.example.json",
                "assets/runtime/effects/paper-masks.js",
                "assets/runtime/scenes/declarative-paper-2_5d.js",
                "assets/runtime/motion-contract.js",
                "shots/scene-01-find-seed/spatial-contract.json",
                "shots/scene-01-find-seed/motion-contract.json",
            ):
                self.assertTrue((output / relative).is_file(), relative)
            package = json.loads((output / "package.json").read_text(encoding="utf-8"))
            self.assertIn("shot:build", package["scripts"])
            motion = json.loads(
                (output / "shots/scene-01-find-seed/motion-contract.json").read_text(encoding="utf-8")
            )
            self.assertEqual(motion["shot_id"], "scene-01-find-seed")
            self.assertEqual(motion["actors"][0]["expected_facing"], "right")


if __name__ == "__main__":
    unittest.main()
