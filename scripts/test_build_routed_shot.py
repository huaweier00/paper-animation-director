#!/usr/bin/env python3
"""Integration test for the one-command routed shot preparer."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_routed_shot.py")


class BuildRoutedShotTests(unittest.TestCase):
    def test_prepare_routes_scaffolds_and_audits_one_shot(self) -> None:
        with tempfile.TemporaryDirectory(prefix="build-routed-shot-") as directory:
            project = Path(directory)
            shot = project / "shots" / "scene-test"
            shot.mkdir(parents=True)
            (project / "story-manifest.json").write_text(
                json.dumps(
                    {
                        "project": "test-project",
                        "aspect": "16:9",
                        "scenes": [{"id": "scene-test", "duration": 3.0}],
                    }
                ),
                encoding="utf-8",
            )
            (shot / "animation-decision.json").write_text(
                json.dumps(
                    {
                        "shot_id": "scene-test",
                        "shot_function": "Show a real local change.",
                        "narrative_responsibility": "The audience sees the actor move.",
                        "responsibility_requires_visible_action": True,
                        "required_visible_changes": ["The connected actor changes pose."],
                        "evidence_is_presentation_only": False,
                        "intentional_ellipsis_or_offscreen_action": False,
                        "ellipsis_rationale": "",
                        "action_carried_elsewhere": [],
                        "architecture_choice": "Complete pose replacement on a locked stage.",
                        "merged_elements": ["The actor remains connected."],
                        "independent_elements": ["The actor changes as one pose."],
                        "camera_and_presentation_role": "The camera remains static.",
                        "why_this_choice": "It directly proves the required local change.",
                        "alternatives_considered": ["Whole-frame motion was rejected."],
                        "risk_flags": ["Keep both feet grounded."],
                        "proof_plan": ["Inspect the first, midpoint, and final frames."],
                    }
                ),
                encoding="utf-8",
            )
            (shot / "shot-capabilities.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "shot_id": "scene-test",
                        "responsibility": "Show one complete connected pose change.",
                        "requirements": {
                            "character_motion": "pose-replacement",
                            "contact": "staged",
                            "spatial_depth": "flat",
                            "camera": "static",
                            "particle_load": "none",
                            "simulation": "none",
                            "typography": "supporting",
                            "reuse": "one-off",
                            "environment_fx": [],
                        },
                        "constraints": {
                            "must_remain_2d": True,
                            "offline_render_allowed": True,
                            "alpha_required": True,
                            "manual_authoring_allowed": True,
                        },
                        "preferences": {
                            "character_engine": "auto",
                            "effects_engine": "auto",
                            "spatial_engine": "auto",
                            "delivery": "auto",
                            "forbid_engines": [],
                        },
                        "proof_requirements": ["The pose change is visible in the rendered shot."],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--project",
                    str(project),
                    "--shot-id",
                    "scene-test",
                    "--phase",
                    "prepare",
                    "--skip-doctor",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertTrue(report["ok"])
            self.assertTrue((shot / "engine-plan.json").is_file())
            self.assertTrue((shot / "engine-inputs.json").is_file())
            self.assertTrue((project / "compositions" / "scene-test.html").is_file())
            self.assertEqual(
                [step["name"] for step in report["steps"]],
                [
                    "animation-decision-planning",
                    "route-capabilities",
                    "scaffold-shot",
                    "audit-engine-inputs-development",
                ],
            )


if __name__ == "__main__":
    unittest.main()
