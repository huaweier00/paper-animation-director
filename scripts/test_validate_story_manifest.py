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

    def test_rejects_missing_model_pack_in_premium_production(self) -> None:
        data = load_example()
        del data["characters"][0]["identity_model_pack"]
        self.assertIn("characters[0].identity_model_pack", error_paths(data))

    def test_rejects_one_sided_model_pack(self) -> None:
        data = load_example()
        data["characters"][0]["identity_model_pack"]["views"] = [
            {"view": "left-profile", "path": "left.png"}
        ]
        self.assertIn("characters[0].identity_model_pack.views", error_paths(data))

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

    def test_rejects_social_logo_before_promise(self) -> None:
        data = load_example()
        data["social_contract"]["opening"]["logo_before_promise"] = True
        self.assertIn("social_contract.opening.logo_before_promise", error_paths(data))

    def test_rejects_late_social_promise_proof(self) -> None:
        data = load_example()
        data["social_contract"]["opening"]["visual_proof_by"] = 4.0
        self.assertIn("social_contract.opening.visual_proof_by", error_paths(data))

    def test_rejects_first_shot_whose_promise_proof_lands_late(self) -> None:
        data = load_example()
        for beat in data["scenes"][0]["visual_beats"]:
            if beat["function"] == "promise-proof":
                beat["time"] = 3.4
        self.assertIn("scenes[0].visual_beats", error_paths(data))

    def test_rejects_missing_save_object(self) -> None:
        data = load_example()
        del data["social_contract"]["value"]["save_object"]
        self.assertIn("social_contract.value.save_object", error_paths(data))

    def test_rejects_unapproved_animatic_in_production(self) -> None:
        data = load_example()
        data["social_contract"]["animatic"]["hook_review"] = "pending"
        self.assertIn("social_contract.animatic.hook_review", error_paths(data))

    def test_rejects_missing_visual_direction_in_production(self) -> None:
        data = load_example()
        del data["visual_direction"]
        self.assertIn("visual_direction", error_paths(data))

    def test_editorial_phase_allows_visual_direction_to_be_pending(self) -> None:
        data = load_example()
        del data["visual_direction"]
        findings = validate_manifest(data, phase="editorial")
        self.assertNotIn("visual_direction", {item["path"] for item in findings if item["severity"] == "error"})

    def test_rejects_fewer_than_three_art_routes(self) -> None:
        data = load_example()
        data["visual_direction"]["lookdev"]["route_candidates"] = data["visual_direction"]["lookdev"]["route_candidates"][:2]
        self.assertIn("visual_direction.lookdev.route_candidates", error_paths(data))

    def test_rejects_production_hero_frame_as_lookdev_reference(self) -> None:
        data = load_example()
        data["visual_direction"]["lookdev"]["hero_frames"][0]["reference_only"] = False
        self.assertIn("visual_direction.lookdev.hero_frames[0].reference_only", error_paths(data))

    def test_rejects_first_plausible_auto_accept_policy(self) -> None:
        data = load_example()
        data["visual_direction"]["asset_policy"]["first_plausible_auto_accept"] = True
        self.assertIn("visual_direction.asset_policy.first_plausible_auto_accept", error_paths(data))

    def test_rejects_approved_dominant_asset_without_quality_review(self) -> None:
        data = load_example()
        data["scenes"][0]["asset_plan"]["assets"][0]["status"] = "approved"
        self.assertIn("scenes[0].asset_plan.assets[0].quality_review", error_paths(data))

    def test_approved_dominant_asset_passes_with_candidate_and_composite_evidence(self) -> None:
        data = load_example()
        asset = data["scenes"][0]["asset_plan"]["assets"][0]
        asset["status"] = "approved"
        asset["quality_review"] = {
            "candidates_compared": 3,
            "selected_candidate": "background-c",
            "rejection_notes": ["A lost the focal corridor.", "B used incompatible light."],
            "source_dimensions": [3072, 5461],
            "art_direction_match": "pass",
            "composite_test": "pass",
            "phone_size_readability": "pass",
            "finish": "pass",
        }
        self.assertEqual(validate_manifest(data), [])

    def test_editorial_phase_allows_pending_animatic(self) -> None:
        data = load_example()
        data["social_contract"]["animatic"]["hook_review"] = "pending"
        data["social_contract"]["animatic"]["full_edit_review"] = "pending"
        findings = validate_manifest(data, phase="editorial")
        self.assertNotIn("social_contract.animatic.hook_review", {item["path"] for item in findings if item["severity"] == "error"})

    def test_rejects_social_scene_without_visual_beats(self) -> None:
        data = load_example()
        del data["scenes"][0]["visual_beats"]
        self.assertIn("scenes[0].visual_beats", error_paths(data))

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

    def test_contact_sheet_includes_social_visual_beats(self) -> None:
        data = load_example()
        with tempfile.TemporaryDirectory(prefix="paper-social-review-test-") as directory:
            temporary = Path(directory) / "manifest.json"
            temporary.write_text(json.dumps(data), encoding="utf-8")
            times = manifest_times(temporary)
        self.assertTrue({0.0, 1.1, 2.6, 11.8}.issubset(set(times)))

    def test_mutations_do_not_leak_between_examples(self) -> None:
        first = load_example()
        second = copy.deepcopy(first)
        second["characters"][0]["identity_reference"]["view"] = "side"
        self.assertEqual(validate_manifest(first), [])
        self.assertIn("characters[0].identity_reference.view", error_paths(second))


if __name__ == "__main__":
    unittest.main()
