#!/usr/bin/env python3
"""Tests for production hybrid-shot scaffolding."""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).with_name("scaffold_hybrid_shot.py")
SKILL_ROOT = SCRIPT.parent.parent


class HybridScaffolderTests(unittest.TestCase):
    def test_scaffold_mounts_verified_adapters_and_writes_asset_gates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            project = root / "project"
            project.mkdir()
            (project / "story-manifest.json").write_text(
                json.dumps(
                    {
                        "aspect": "16:9",
                        "scenes": [{"id": "scene-01", "duration": 3.2}],
                    }
                ),
                encoding="utf-8",
            )
            plan = root / "engine-plan.json"
            plan.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "shot_id": "scene-01",
                        "orchestrator": "hyperframes",
                        "engines": [
                            "gsap-dom",
                            "rive",
                            "pixijs-webgpu",
                            "three-webgpu",
                            "blender",
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), "--plan", str(plan), "--project", str(project)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["verified_adapters_mounted"])
            self.assertEqual(report["required_asset_gates"], ["rive", "blender"])

            composition = (project / "compositions" / "scene-01.html").read_text(encoding="utf-8")
            self.assertIn("mountPixiPaperEffects", composition)
            self.assertIn("mountRiveLinearAnimation", composition)
            self.assertIn("mountThreeSeekableScene", composition)
            self.assertIn("createDeclarativePaperScene", composition)
            self.assertIn("scene_manifest", composition)
            self.assertIn("compiled-motion-track.json", composition)
            self.assertIn("applyGsapMotion", composition)
            self.assertIn("seekTimelineToPending", composition)
            self.assertNotIn('<script type="module">', composition)
            self.assertIn('await import("./node_modules/three/build/three.webgpu.js")', composition)
            self.assertIn(
                'data-required-asset="./shots/scene-01/assets/prerender/scene-01-alpha.webm"',
                composition,
            )
            self.assertIn("video.src = config.asset", composition)
            self.assertNotIn("Diagnostic only", composition)
            self.assertNotIn("seededUnit", composition)

            inputs_path = project / "shots" / "scene-01" / "engine-inputs.json"
            inputs = json.loads(inputs_path.read_text(encoding="utf-8"))
            self.assertEqual(inputs["schema_version"], 2)
            self.assertTrue(inputs["engines"]["pixijs-webgpu"]["ready"])
            self.assertTrue(inputs["engines"]["three-webgpu"]["ready"])
            self.assertFalse(inputs["engines"]["rive"]["ready"])
            self.assertFalse(inputs["engines"]["blender"]["ready"])
            self.assertTrue(
                (project / "assets" / "runtime" / "effects" / "paper-particles.js").is_file()
            )
            self.assertTrue(
                (project / "assets" / "runtime" / "effects" / "paper-masks.js").is_file()
            )
            self.assertTrue((project / "assets" / "runtime" / "motion-contract.js").is_file())
            self.assertTrue(
                (
                    project
                    / "assets"
                    / "runtime"
                    / "scenes"
                    / "declarative-paper-2_5d.js"
                ).is_file()
            )
            self.assertTrue((project / "shots" / "scene-01" / "three-scene.json").is_file())
            self.assertTrue((project / "shots" / "scene-01" / "rive-rig.json").is_file())
            self.assertTrue((project / "shots" / "scene-01" / "performance-budget.json").is_file())
            self.assertTrue((project / "shots" / "scene-01" / "webgpu-capability.json").is_file())
            self.assertTrue((project / "blender-action-library.json").is_file())

    def test_creative_template_is_minimal_and_production_lock_pins_engines(self) -> None:
        package = json.loads(
            (SKILL_ROOT / "assets" / "project-template" / "package.json").read_text(encoding="utf-8")
        )
        self.assertEqual(package["dependencies"], {"gsap": "3.15.0"})
        self.assertEqual(package["devDependencies"]["hyperframes"], "0.7.83")
        lock = json.loads(
            (SKILL_ROOT / "assets" / "project-template" / "package-lock.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(lock["lockfileVersion"], 3)
        production_dependencies = lock["packages"][""]["dependencies"]
        self.assertEqual(production_dependencies["gsap"], "3.15.0")
        self.assertEqual(production_dependencies["pixi.js"], "8.19.0")
        self.assertEqual(production_dependencies["@rive-app/canvas-advanced-single"], "2.39.1")
        self.assertEqual(production_dependencies["three"], "0.185.1")
        self.assertEqual(lock["packages"][""]["devDependencies"], package["devDependencies"])
        policy = json.loads(
            (
                SKILL_ROOT
                / "assets"
                / "project-template"
                / "offline-dependency-policy.json"
            ).read_text(encoding="utf-8")
        )
        self.assertTrue(policy["policies"]["runtime_network_forbidden"])
        self.assertTrue(policy["policies"]["lock_drift_blocks_render"])
        index = (SKILL_ROOT / "assets" / "project-template" / "index.html").read_text(encoding="utf-8")
        self.assertIn("./node_modules/gsap/dist/gsap.min.js", index)
        self.assertNotIn("cdn.jsdelivr.net", index)


if __name__ == "__main__":
    unittest.main()
