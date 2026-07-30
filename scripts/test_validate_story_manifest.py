#!/usr/bin/env python3
"""Regression tests for identity-only and shot-spatial manifest gates."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from make_review_contact_sheet import manifest_times
from validate_story_manifest import validate_manifest


ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "assets" / "project-template" / "manifests" / "story-manifest.example.json"


def load_example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def error_paths(data: dict) -> set[str]:
    return {item["path"] for item in validate_manifest(data) if item["severity"] == "error"}


class ManifestValidationTests(unittest.TestCase):
    def test_example_passes(self) -> None:
        self.assertEqual(validate_manifest(load_example()), [])

    def test_rejects_identity_image_as_animation_asset(self) -> None:
        data = load_example()
        data["characters"][0]["identity_reference"]["animation_use"] = True
        self.assertIn("characters[0].identity_reference.animation_use", error_paths(data))

    def test_rejects_legacy_global_pose_inventory(self) -> None:
        data = load_example()
        data["characters"][0]["required_poses"] = ["neutral", "walk-left", "walk-right", "final"]
        self.assertIn("characters[0].required_poses", error_paths(data))

    def test_rejects_wrong_facing_for_travel_vector(self) -> None:
        data = load_example()
        data["scenes"][0]["spatial_contract"]["actors"][0]["travel"]["facing"] = "left"
        self.assertIn("scenes[0].spatial_contract.actors[0].travel.facing", error_paths(data))

    def test_rejects_non_passable_obstacle_in_motion_corridor(self) -> None:
        data = load_example()
        data["scenes"][0]["spatial_contract"]["obstacles"].append(
            {
                "id": "blocking-table",
                "zone": [0.40, 0.60, 0.52, 0.82],
                "passable": False,
            }
        )
        self.assertIn("scenes[0].spatial_contract.obstacles[0]", error_paths(data))

    def test_rejects_semantically_wrong_action_target(self) -> None:
        data = load_example()
        actor = data["scenes"][0]["spatial_contract"]["actors"][0]
        actor["action"]["type"] = "write-on"
        actor["action"]["target"] = "seed"
        self.assertIn("scenes[0].spatial_contract.actors[0].action.target", error_paths(data))

    def test_rejects_asset_direction_that_disagrees_with_shot(self) -> None:
        data = load_example()
        asset = data["scenes"][0]["asset_plan"]["assets"][1]
        asset["screen_direction"] = "right-to-left"
        self.assertIn("scenes[0].asset_plan.assets[1].screen_direction", error_paths(data))

    def test_rejects_missing_head_protection(self) -> None:
        data = load_example()
        data["scenes"][0]["review_contract"]["protected_regions"].remove("head")
        self.assertIn("scenes[0].review_contract.protected_regions", error_paths(data))

    def test_rejects_undeclared_character_occluder(self) -> None:
        data = load_example()
        data["scenes"][0]["spatial_contract"]["occluders"].append(
            {
                "id": "doorframe",
                "zone": [0.45, 0.10, 0.52, 0.90],
                "depth": "foreground",
                "may_cover_characters": True,
            }
        )
        self.assertIn("scenes[0].spatial_contract.occluders", error_paths(data))

    def test_contact_sheet_includes_occlusion_review_times(self) -> None:
        data = load_example()
        data["scenes"][0]["spatial_contract"]["occluders"].append(
            {
                "id": "doorframe",
                "zone": [0.45, 0.10, 0.52, 0.90],
                "depth": "foreground",
                "may_cover_characters": True,
            }
        )
        data["scenes"][0]["review_contract"]["intentional_occlusions"].append(
            {
                "actor_id": "bird",
                "occluder_id": "doorframe",
                "start": 1.0,
                "maximum_time": 1.5,
                "end": 2.0,
                "reason": "The bird passes behind a visible doorframe.",
                "identity_proof_time": 0.5,
            }
        )
        self.assertEqual(validate_manifest(data), [])
        with tempfile.TemporaryDirectory(prefix="paper-review-test-") as directory:
            temporary = Path(directory) / "manifest.json"
            temporary.write_text(json.dumps(data), encoding="utf-8")
            times = manifest_times(temporary)
        self.assertTrue({0.5, 1.0, 1.5, 2.0}.issubset(set(times)))

    def test_mutations_do_not_leak_between_examples(self) -> None:
        first = load_example()
        second = copy.deepcopy(first)
        second["characters"][0]["identity_reference"]["view"] = "side"
        self.assertEqual(validate_manifest(first), [])
        self.assertIn("characters[0].identity_reference.view", error_paths(second))


if __name__ == "__main__":
    unittest.main()
