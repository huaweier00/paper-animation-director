#!/usr/bin/env python3
"""Tests for the per-shot release gate."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest


SCRIPT_PATH = pathlib.Path(__file__).with_name("audit_shot_release.py")
SPEC = importlib.util.spec_from_file_location("audit_shot_release", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def valid_release() -> dict:
    zero = "0" * 64
    return {
        "schema_version": 4,
        "shot_id": "scene-01",
        "decision": "approved",
        "rendered_mp4": "shot.mp4",
        "rendered_mp4_sha256": zero,
        "animation_decision": "animation-decision.json",
        "shot_capabilities": "shot-capabilities.json",
        "engine_plan": "engine-plan.json",
        "engine_inputs": "engine-inputs.json",
        "visual_direction_contract": "story-manifest.json",
        "motion_contract": "motion-contract.json",
        "rendered_motion_review": "rendered-motion-review.json",
        "motion_required": True,
        "record_sha256": {
            field: zero
            for field in (
                "animation_decision",
                "shot_capabilities",
                "engine_plan",
                "engine_inputs",
                "visual_direction_contract",
                "motion_contract",
                "rendered_motion_review",
            )
        },
        "contact_required": False,
        "audio_required": False,
        "checks": {name: "pass" for name in MODULE.REQUIRED_CHECKS},
        "proof_frames": {
            "first": "first.png",
            "midpoint": "midpoint.png",
            "proof": "proof.png",
            "final": "final.png",
        },
        "proof_frame_sha256": {field: zero for field in ("first", "midpoint", "proof", "final")},
        "critical_props": [],
        "expected_lines": [],
        "review_notes": "Seek proof inspected at non-sequential frames.",
    }


class ShotReleaseAuditTests(unittest.TestCase):
    def test_valid_motion_evidence_release_passes_without_path_checks(self) -> None:
        errors, warnings = MODULE.validate(
            valid_release(),
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_v4_static_shot_does_not_require_motion_evidence(self) -> None:
        release = valid_release()
        release["motion_required"] = False
        release.pop("motion_contract")
        release.pop("rendered_motion_review")
        release["checks"].pop("motion_integrity")
        errors, warnings = MODULE.validate(
            release,
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_v4_requires_explicit_motion_policy(self) -> None:
        release = valid_release()
        release.pop("motion_required")
        errors, _ = MODULE.validate(
            release,
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertTrue(any("motion_required" in error for error in errors), errors)

    def test_v4_rejects_unbound_render(self) -> None:
        release = valid_release()
        release.pop("rendered_mp4_sha256")
        errors, _ = MODULE.validate(
            release,
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertTrue(any("rendered_mp4_sha256" in error for error in errors), errors)

    def test_release_binder_hashes_static_shot_and_audit_detects_later_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="release-bind-") as directory:
            root = pathlib.Path(directory)
            release = valid_release()
            release["motion_required"] = False
            release.pop("motion_contract")
            release.pop("rendered_motion_review")
            release["checks"].pop("motion_integrity")
            release_path = root / "shot-release.json"
            for field in (
                "rendered_mp4",
                "animation_decision",
                "shot_capabilities",
                "engine_plan",
                "engine_inputs",
                "visual_direction_contract",
            ):
                (root / release[field]).write_bytes(field.encode("utf-8"))
            (root / release["engine_plan"]).write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "shot_id": "scene-01",
                        "orchestrator": "hyperframes",
                        "engines": ["gsap-dom"],
                    }
                ),
                encoding="utf-8",
            )
            (root / release["engine_inputs"]).write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "shot_id": "scene-01",
                        "clock": "hyperframes-absolute-seconds",
                        "engines": {"gsap-dom": {"ready": True}},
                    }
                ),
                encoding="utf-8",
            )
            for field in ("animation_decision", "shot_capabilities"):
                (root / release[field]).write_text(
                    json.dumps({"shot_id": "scene-01"}),
                    encoding="utf-8",
                )
            for value in release["proof_frames"].values():
                (root / value).write_bytes(value.encode("utf-8"))
            release_path.write_text(json.dumps(release), encoding="utf-8")
            binder = pathlib.Path(__file__).with_name("bind_release_evidence.py")
            result = subprocess.run(
                ["python3", str(binder), str(release_path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            bound = json.loads(release_path.read_text(encoding="utf-8"))
            errors, warnings = MODULE.validate(
                bound,
                root,
                strict=True,
                require_approved=True,
                check_paths=True,
            )
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])
            (root / bound["rendered_mp4"]).write_bytes(b"replacement")
            errors, _ = MODULE.validate(
                bound,
                root,
                strict=True,
                require_approved=True,
                check_paths=True,
            )
            self.assertTrue(any("rendered_mp4_sha256" in error for error in errors), errors)

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

    def test_visual_direction_path_is_required_for_v3(self) -> None:
        release = valid_release()
        release.pop("visual_direction_contract")
        errors, _ = MODULE.validate(
            release,
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertTrue(any("visual_direction_contract" in error for error in errors), errors)

    def test_phone_size_visual_check_is_required_for_v3(self) -> None:
        release = valid_release()
        release["checks"].pop("phone_size_readability")
        errors, _ = MODULE.validate(
            release,
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertTrue(any("phone_size_readability" in error for error in errors), errors)

    def test_v2_hybrid_release_remains_compatible(self) -> None:
        release = valid_release()
        release["schema_version"] = 2
        release.pop("motion_required")
        release.pop("visual_direction_contract")
        release.pop("motion_contract")
        release.pop("rendered_motion_review")
        for key in MODULE.VISUAL_REQUIRED_CHECKS:
            release["checks"].pop(key)
        for key in MODULE.MOTION_REQUIRED_CHECKS:
            release["checks"].pop(key)
        errors, warnings = MODULE.validate(
            release,
            pathlib.Path("."),
            strict=True,
            require_approved=True,
            check_paths=False,
        )
        self.assertEqual(errors, [])
        self.assertTrue(any("v2 hybrid" in warning for warning in warnings), warnings)

    def test_legacy_release_does_not_break_on_missing_routing_fields(self) -> None:
        release = valid_release()
        release.pop("schema_version")
        release.pop("motion_required")
        release.pop("shot_capabilities")
        release.pop("engine_plan")
        release.pop("engine_inputs")
        release.pop("visual_direction_contract")
        release.pop("motion_contract")
        release.pop("rendered_motion_review")
        release["checks"].pop("engine_plan_fulfilled")
        release["checks"].pop("deterministic_seek")
        for key in MODULE.VISUAL_REQUIRED_CHECKS:
            release["checks"].pop(key)
        for key in MODULE.MOTION_REQUIRED_CHECKS:
            release["checks"].pop(key)
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
