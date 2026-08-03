#!/usr/bin/env python3
"""Regression tests for medium, performance, sound, and pose-reuse gates."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from audit_audio_mode import validate_audio_contract
from audit_medium_contract import validate_medium_contract
from audit_performance_contract import validate_performance_contract
from audit_pose_reuse import validate_pose_reuse
from init_paper_project import build_audio_contract, build_medium_contract, build_performance_contract


MANIFESTS = Path(__file__).resolve().parent.parent / "assets" / "project-template" / "manifests"


def example(name: str) -> dict:
    return json.loads((MANIFESTS / name).read_text(encoding="utf-8"))


class MediumContractTests(unittest.TestCase):
    def test_shadow_example_passes_release_shape(self) -> None:
        errors, warnings = validate_medium_contract(example("medium-contract.example.json"), phase="release")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_shadow_route_rejects_opaque_png_shortcut(self) -> None:
        contract = example("medium-contract.example.json")
        contract["forbidden_shortcuts"].remove("opaque-full-body-png-as-shadow-puppet")
        errors, _ = validate_medium_contract(contract)
        self.assertTrue(any("opaque-full-body-png" in item for item in errors), errors)

    def test_production_requires_approved_benchmark(self) -> None:
        contract = example("medium-contract.example.json")
        contract["benchmark"]["status"] = "planned"
        errors, _ = validate_medium_contract(contract, phase="production")
        self.assertTrue(any("benchmark.status" in item for item in errors), errors)

    def test_all_route_examples_pass_release_shape(self) -> None:
        for name in (
            "medium-contract.example.json",
            "medium-contract.cutout-paper.example.json",
            "medium-contract.painterly-limited.example.json",
        ):
            errors, warnings = validate_medium_contract(example(name), phase="release")
            self.assertEqual(errors, [], (name, errors))
            self.assertEqual(warnings, [], (name, warnings))


class PerformanceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.medium = example("medium-contract.example.json")
        self.performance = example("performance-contract.example.json")

    def test_example_passes_planning(self) -> None:
        errors, warnings = validate_performance_contract(
            self.performance,
            medium=self.medium,
            phase="planning",
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_root_transform_only_cannot_prove_actor_action(self) -> None:
        contract = copy.deepcopy(self.performance)
        for phase in contract["actors"][0]["phases"]:
            phase["channel"] = "root-translation"
        errors, _ = validate_performance_contract(contract, medium=self.medium, phase="planning")
        self.assertTrue(any("presentation/root channels" in item for item in errors), errors)

    def test_whole_image_alias_cannot_evade_presentation_gate(self) -> None:
        contract = copy.deepcopy(self.performance)
        for phase in contract["actors"][0]["phases"]:
            phase["channel"] = "whole image camera wrapper"
        errors, _ = validate_performance_contract(contract, medium=self.medium, phase="planning")
        self.assertTrue(any("presentation/root channels" in item for item in errors), errors)

    def test_shadow_action_requires_sound_link(self) -> None:
        contract = copy.deepcopy(self.performance)
        contract["sound_cues"] = []
        errors, _ = validate_performance_contract(contract, medium=self.medium, phase="planning")
        self.assertTrue(any("sound-linked" in item for item in errors), errors)

    def test_unearned_stillness_is_rejected(self) -> None:
        contract = copy.deepcopy(self.performance)
        contract["motion_required"] = False
        contract["actors"] = []
        contract["earned_stillness"] = None
        errors, _ = validate_performance_contract(contract, medium=self.medium, phase="planning")
        self.assertTrue(any("earned_stillness" in item for item in errors), errors)

    def test_moving_poster_fixture_fails_closed(self) -> None:
        fixture = json.loads(
            (Path(__file__).with_name("fixtures") / "moving-poster.invalid.performance-contract.json").read_text(
                encoding="utf-8"
            )
        )
        errors, _ = validate_performance_contract(fixture, medium=self.medium, phase="planning")
        self.assertTrue(any("presentation/root channels" in item for item in errors), errors)
        self.assertTrue(any("sound-linked" in item for item in errors), errors)


class PoseReuseTests(unittest.TestCase):
    def write_contract(self, project: Path, shot_id: str, objective: str, state: str) -> None:
        shot = project / "shots" / shot_id
        shot.mkdir(parents=True)
        contract = example("performance-contract.example.json")
        contract["shot_id"] = shot_id
        contract["actors"] = [contract["actors"][0]]
        actor = contract["actors"][0]
        actor["objective"] = objective
        actor["production_asset"]["performance_state"] = state
        (shot / "performance-contract.json").write_text(json.dumps(contract), encoding="utf-8")

    def test_incompatible_unapproved_pose_reuse_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pose-reuse-") as directory:
            project = Path(directory)
            self.write_contract(project, "a", "threaten", "attack")
            self.write_contract(project, "b", "comfort", "protect")
            errors, _, _ = validate_pose_reuse(project)
            self.assertTrue(any("incompatible" in item for item in errors), errors)

    def test_same_intention_pose_reuse_passes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pose-reuse-") as directory:
            project = Path(directory)
            self.write_contract(project, "a", "protect", "guard")
            self.write_contract(project, "b", "protect", "guard")
            errors, warnings, _ = validate_pose_reuse(project)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])


class AudioContractTests(unittest.TestCase):
    def test_shadow_route_rejects_music_only(self) -> None:
        medium = example("medium-contract.example.json")
        audio = example("audio-contract.example.json")
        audio["mode"] = "music-and-effects"
        errors, _, _ = validate_audio_contract(audio, medium=medium, phase="planning")
        self.assertTrue(any("shadow-theatre" in item for item in errors), errors)

    def test_release_requires_real_video(self) -> None:
        medium = example("medium-contract.example.json")
        audio = example("audio-contract.example.json")
        with tempfile.TemporaryDirectory(prefix="audio-release-") as directory:
            project = Path(directory)
            errors, _, _ = validate_audio_contract(
                audio,
                medium=medium,
                phase="release",
                project=project,
                video=project / "missing.mp4",
            )
            self.assertTrue(any("video: file does not exist" in item for item in errors), errors)


class InitializerContractTests(unittest.TestCase):
    def test_every_route_scaffolds_valid_planning_contracts(self) -> None:
        scene = {
            "id": "benchmark",
            "duration": 6.0,
            "responsibility": "One performer changes the state of a prop.",
            "spatial_contract": {
                "actors": [
                    {
                        "id": "performer",
                        "support_surface": "stage",
                        "action": {"type": "lift", "target": "prop"},
                    }
                ]
            },
        }
        for route in ("shadow-theatre", "cutout-paper", "painterly-limited"):
            data = {
                "project": "route-test",
                "medium_route": route,
                "performance_benchmark_shot": "benchmark",
                "scenes": [scene],
            }
            medium = build_medium_contract(data)
            audio = build_audio_contract(data, route)
            performance = build_performance_contract(scene, route)
            medium_errors, _ = validate_medium_contract(medium, phase="planning")
            audio_errors, _, _ = validate_audio_contract(audio, medium=medium, phase="planning")
            performance_errors, _ = validate_performance_contract(
                performance,
                medium=medium,
                phase="planning",
            )
            self.assertEqual(medium_errors, [], (route, medium_errors))
            self.assertEqual(audio_errors, [], (route, audio_errors))
            self.assertEqual(performance_errors, [], (route, performance_errors))


if __name__ == "__main__":
    unittest.main()
