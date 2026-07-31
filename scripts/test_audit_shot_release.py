#!/usr/bin/env python3
"""Tests for the per-shot release gate."""

from __future__ import annotations

import importlib.util
import pathlib
import unittest


SCRIPT_PATH = pathlib.Path(__file__).with_name("audit_shot_release.py")
SPEC = importlib.util.spec_from_file_location("audit_shot_release", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def valid_release() -> dict:
    return {
        "schema_version": 2,
        "shot_id": "scene-01",
        "decision": "approved",
        "rendered_mp4": "shot.mp4",
        "animation_decision": "animation-decision.json",
        "shot_capabilities": "shot-capabilities.json",
        "engine_plan": "engine-plan.json",
        "engine_inputs": "engine-inputs.json",
        "contact_required": False,
        "audio_required": False,
        "checks": {name: "pass" for name in MODULE.REQUIRED_CHECKS},
        "proof_frames": {
            "first": "first.png",
            "midpoint": "midpoint.png",
            "proof": "proof.png",
            "final": "final.png",
        },
        "critical_props": [],
        "expected_lines": [],
        "review_notes": "Seek proof inspected at non-sequential frames.",
    }


class ShotReleaseAuditTests(unittest.TestCase):
    def test_valid_hybrid_release_passes_without_path_checks(self) -> None:
        errors, warnings = MODULE.validate(
            valid_release(),
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_deterministic_seek_proof_is_required(self) -> None:
        release = valid_release()
        release["checks"].pop("deterministic_seek")
        errors, _ = MODULE.validate(
            release,
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertTrue(
            any("deterministic_seek" in error for error in errors),
            errors,
        )

    def test_engine_plan_path_is_required(self) -> None:
        release = valid_release()
        release.pop("engine_plan")
        errors, _ = MODULE.validate(
            release,
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertTrue(any("engine_plan" in error for error in errors), errors)

    def test_legacy_release_does_not_break_on_missing_routing_fields(self) -> None:
        release = valid_release()
        release.pop("schema_version")
        release.pop("shot_capabilities")
        release.pop("engine_plan")
        release.pop("engine_inputs")
        release["checks"].pop("engine_plan_fulfilled")
        release["checks"].pop("deterministic_seek")
        errors, warnings = MODULE.validate(
            release,
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertEqual(errors, [])
        self.assertTrue(any("legacy v1" in warning for warning in warnings), warnings)


if __name__ == "__main__":
    unittest.main()
