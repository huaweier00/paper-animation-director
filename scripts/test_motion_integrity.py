#!/usr/bin/env python3
"""Regression tests for asset-fact, facing, travel, compile, and rendered-evidence gates."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from audit_motion_contract import audit_contract
from audit_rendered_motion import validate as validate_rendered


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MotionIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="motion-integrity-")
        self.project = Path(self.temp.name)
        (self.project / "shots/scene-test/asset-facts").mkdir(parents=True)
        (self.project / "shots/scene-test/review/assets").mkdir(parents=True)
        (self.project / "compositions").mkdir()
        self.media = self.project / "shots/scene-test/actor.png"
        self.evidence = self.project / "shots/scene-test/review/assets/actor-orientation.png"
        Image.new("RGBA", (64, 64), (120, 80, 40, 255)).save(self.media)
        Image.new("RGB", (64, 64), (245, 240, 225)).save(self.evidence)
        self.facts_path = self.project / "shots/scene-test/asset-facts/actor.json"
        self.facts = {
            "schema_version": 1,
            "asset_id": "actor-right-v1",
            "identity_id": "actor",
            "file": "shots/scene-test/actor.png",
            "sha256": digest(self.media),
            "kind": "complete-character-pose",
            "intrinsic_facing": "right",
            "forward_axis": [1, 0],
            "mirror_policy": "forbidden",
            "orientation_review": {
                "status": "approved",
                "observed_head_side": "right",
                "observed_chest_side": "right",
                "observed_gaze": "right",
                "reviewer": "visual-artifact-review",
                "evidence": "shots/scene-test/review/assets/actor-orientation.png",
            },
        }
        self.facts_path.write_text(json.dumps(self.facts), encoding="utf-8")
        self.source = self.project / "compositions/scene-test.html"
        self.source.write_text(
            '<div id="actor"></div><script>fetch("compiled-motion-track.json"); applyGsapMotion({actorId:"actor"});</script>',
            encoding="utf-8",
        )
        self.contract_path = self.project / "shots/scene-test/motion-contract.json"
        self.contract = {
            "schema_version": 1,
            "shot_id": "scene-test",
            "duration": 4.0,
            "frame": {"width": 1920, "height": 1080},
            "actors": [
                {
                    "actor_id": "actor",
                    "expected_facing": "right",
                    "asset_status": "approved",
                    "asset_facts": "shots/scene-test/asset-facts/actor.json",
                    "implementation": {
                        "engine": "gsap-dom",
                        "selector": "#actor",
                        "source": "compositions/scene-test.html",
                    },
                    "active": [0.4, 3.0],
                    "start": [0.1, 0.7],
                    "end": [0.8, 0.7],
                    "locomotion": "forward-travel",
                    "exception_reason": "",
                    "instance_transform": {"scale_x": 1, "rotation_degrees": 0},
                    "mirror": {"applied": False, "policy": "forbidden"},
                    "support": {"mode": "grounded", "surface": "road", "baseline": 0.82},
                    "contact": {"required": False, "target": "", "time": None},
                    "proof_times": {
                        "entry": 0.4,
                        "early": 0.9,
                        "midpoint": 1.7,
                        "late": 2.5,
                        "exit": 3.0,
                    },
                }
            ],
        }
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def audit(self, data: dict, phase: str = "implementation") -> tuple[list[str], list[str], dict]:
        self.contract_path.write_text(json.dumps(data), encoding="utf-8")
        return audit_contract(data, contract_path=self.contract_path, project=self.project, phase=phase)

    def test_valid_forward_motion_passes(self) -> None:
        errors, warnings, derived = self.audit(self.contract)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(derived["actors"][0]["rendered_facing"], "right")
        self.assertEqual(derived["actors"][0]["travel_direction"], "right")

    def test_planning_allows_planned_missing_asset_facts(self) -> None:
        data = copy.deepcopy(self.contract)
        actor = data["actors"][0]
        actor["asset_status"] = "planned"
        actor["asset_facts"] = "shots/scene-test/asset-facts/not-generated.json"
        errors, _, _ = self.audit(data, phase="planning")
        self.assertEqual(errors, [])

    def test_rejects_wrong_visible_facing_for_forward_travel(self) -> None:
        data = copy.deepcopy(self.contract)
        data["actors"][0]["instance_transform"]["scale_x"] = -1
        data["actors"][0]["mirror"]["applied"] = True
        errors, _, _ = self.audit(data)
        self.assertTrue(any("not approved for mirroring" in item for item in errors))
        self.assertTrue(any("rendered facing conflicts" in item for item in errors))

    def test_rejects_asset_hash_drift(self) -> None:
        self.media.write_bytes(self.media.read_bytes() + b"changed")
        errors, _, _ = self.audit(self.contract)
        self.assertTrue(any("current media differs" in item for item in errors))

    def test_backward_travel_requires_reason(self) -> None:
        data = copy.deepcopy(self.contract)
        data["actors"][0]["locomotion"] = "backward-travel"
        errors, _, _ = self.audit(data)
        self.assertTrue(any("must visibly oppose" in item for item in errors))
        self.assertTrue(any("explain the visible retreat" in item for item in errors))

    def test_compiler_emits_duration_and_pixel_track(self) -> None:
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")
        output = self.project / "shots/scene-test/compiled-motion-track.json"
        script = Path(__file__).with_name("compile_motion_contract.py")
        result = subprocess.run(
            [
                "python3",
                str(script),
                str(self.contract_path),
                "--project",
                str(self.project),
                "--output",
                str(output),
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        compiled = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(compiled["duration"], 4.0)
        self.assertEqual(compiled["tracks"][0]["start_px"], [192.0, 756.0])
        self.assertEqual(compiled["tracks"][0]["end_px"], [1536.0, 756.0])
        self.assertEqual(compiled["tracks"][0]["rendered_facing"], "right")

    def test_rendered_review_binds_hashes_and_real_check_results(self) -> None:
        video = self.project / "renders/shot.mp4"
        sheet = self.project / "shots/scene-test/review/sheet.png"
        frame = self.project / "shots/scene-test/review/frame.png"
        video.parent.mkdir(parents=True)
        sheet.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"video")
        sheet.write_bytes(b"sheet")
        frame.write_bytes(b"frame")
        review = {
            "schema_version": 1,
            "shot_id": "scene-test",
            "motion_contract": "shots/scene-test/motion-contract.json",
            "motion_contract_sha256": digest(self.contract_path),
            "rendered_mp4": "renders/shot.mp4",
            "rendered_mp4_sha256": digest(video),
            "contact_sheet": "shots/scene-test/review/sheet.png",
            "contact_sheet_sha256": digest(sheet),
            "evidence_frames": [
                {"label": label, "time": time, "path": "shots/scene-test/review/frame.png", "sha256": digest(frame)}
                for label, time in (("entry", 0.4), ("midpoint", 1.7), ("exit", 3.0))
            ],
            "actors": [
                {
                    "actor_id": "actor",
                    "expected_rendered_facing": "right",
                    "expected_travel_direction": "right",
                    "required_checks": {"direction": True, "support": True, "contact": False, "identity": True, "result": True},
                    "observed": {"direction": "pass", "support": "pass", "contact": "not-required", "identity": "pass", "result": "pass"},
                    "decision": "approved",
                    "review_notes": "Rendered frames preserve right-facing forward travel and ground support.",
                }
            ],
            "decision": "approved",
            "review_notes": "Motion evidence is current and readable.",
        }
        errors, warnings = validate_rendered(review, project=self.project)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        review["actors"][0]["observed"]["direction"] = "pending"
        errors, _ = validate_rendered(review, project=self.project)
        self.assertTrue(any("observed.direction" in item for item in errors))
        review["actors"][0]["observed"]["direction"] = "pass"
        review["actors"][0]["expected_rendered_facing"] = "left"
        errors, _ = validate_rendered(review, project=self.project)
        self.assertTrue(any("expected_rendered_facing" in item for item in errors))

    @unittest.skipIf(shutil.which("ffmpeg") is None, "ffmpeg is required")
    def test_review_builder_extracts_hash_bound_pending_evidence(self) -> None:
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")
        video = self.project / "renders/shot.mp4"
        video.parent.mkdir(parents=True)
        make_video = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "color=c=tan:s=160x90:d=4:r=10",
                "-pix_fmt",
                "yuv420p",
                "-y",
                str(video),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(make_video.returncode, 0, make_video.stderr)
        review_path = self.project / "shots/scene-test/rendered-motion-review.json"
        script = Path(__file__).with_name("build_motion_review.py")
        result = subprocess.run(
            [
                "python3",
                str(script),
                "--contract",
                str(self.contract_path),
                "--project",
                str(self.project),
                "--video",
                "renders/shot.mp4",
                "--output",
                str(review_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        review = json.loads(review_path.read_text(encoding="utf-8"))
        self.assertEqual(review["decision"], "pending")
        self.assertGreaterEqual(len(review["evidence_frames"]), 5)
        self.assertTrue((self.project / review["contact_sheet"]).is_file())
        errors, _ = validate_rendered(review, project=self.project)
        self.assertTrue(any("expected pass" in item for item in errors), errors)


if __name__ == "__main__":
    unittest.main()
