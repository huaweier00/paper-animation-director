#!/usr/bin/env python3
"""Integration test for the one-command routed shot preparer."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from build_routed_shot import previous_shot_ids
from init_paper_project import build_audio_contract, build_medium_contract, build_performance_contract


SCRIPT = Path(__file__).with_name("build_routed_shot.py")
EXAMPLE = SCRIPT.parent.parent / "assets" / "project-template" / "manifests" / "story-manifest.example.json"


class BuildRoutedShotTests(unittest.TestCase):
    def test_previous_shot_ids_follow_manifest_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ordered-release-") as directory:
            project = Path(directory)
            (project / "story-manifest.json").write_text(
                json.dumps({"scenes": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}),
                encoding="utf-8",
            )
            self.assertEqual(previous_shot_ids(project, "c"), ["a", "b"])

    def test_prepare_routes_scaffolds_and_audits_one_shot(self) -> None:
        with tempfile.TemporaryDirectory(prefix="build-routed-shot-") as directory:
            project = Path(directory)
            shot = project / "shots" / "scene-test"
            shot.mkdir(parents=True)
            manifest = json.loads(EXAMPLE.read_text(encoding="utf-8"))
            manifest["project"] = "test-project"
            scene = manifest["scenes"][0]
            scene["id"] = "scene-test"
            scene["duration"] = 6.0
            manifest["scenes"] = [scene]
            manifest["target_duration"] = 6.0
            manifest["performance_benchmark_shot"] = "scene-test"
            (project / "story-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            medium = build_medium_contract(manifest)
            (project / "medium-contract.json").write_text(json.dumps(medium), encoding="utf-8")
            (project / "audio-contract.json").write_text(
                json.dumps(build_audio_contract(manifest, medium["route"])),
                encoding="utf-8",
            )
            (shot / "performance-contract.json").write_text(
                json.dumps(build_performance_contract(scene, medium["route"])),
                encoding="utf-8",
            )
            (shot / "spatial-contract.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "shot_id": "scene-test",
                        "spatial_contract": scene["spatial_contract"],
                        "asset_plan": scene["asset_plan"],
                        "review_contract": scene["review_contract"],
                    }
                ),
                encoding="utf-8",
            )
            actor = scene["spatial_contract"]["actors"][0]
            (shot / "motion-contract.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "shot_id": "scene-test",
                        "duration": 6.0,
                        "frame": {"width": 1080, "height": 1920},
                        "actors": [
                            {
                                "actor_id": actor["id"],
                                "expected_facing": "right",
                                "asset_status": "planned",
                                "asset_facts": "shots/scene-test/asset-facts/bird.json",
                                "implementation": {"engine": "gsap-dom", "selector": "#scene-test-bird", "source": "compositions/scene-test.html"},
                                "active": [0.2, 4.8],
                                "start": [0.1, 0.7],
                                "end": [0.7, 0.7],
                                "locomotion": "forward-travel",
                                "exception_reason": "",
                                "instance_transform": {"scale_x": 1, "rotation_degrees": 0},
                                "mirror": {"applied": False, "policy": "forbidden"},
                                "support": {"mode": "grounded", "surface": "ground", "baseline": 0.82},
                                "contact": {"required": False, "target": "", "time": None},
                                "proof_times": {"entry": 0.2, "early": 1.2, "midpoint": 2.5, "late": 3.7, "exit": 4.8},
                            }
                        ],
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
                    "medium-contract-planning",
                    "audio-contract-planning",
                    "performance-contract-planning",
                    "story-manifest-production",
                    "animation-decision-planning",
                    "motion-contract-planning",
                    "route-capabilities",
                    "scaffold-shot",
                    "audit-engine-inputs-development",
                ],
            )


if __name__ == "__main__":
    unittest.main()
