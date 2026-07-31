#!/usr/bin/env python3
"""Unit tests for routed engine-input release auditing."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from audit_engine_inputs import validate_engine_inputs


def plan(*engines: str) -> dict:
    return {
        "schema_version": 1,
        "shot_id": "scene-test",
        "orchestrator": "hyperframes",
        "engines": list(engines),
    }


class EngineInputAuditTests(unittest.TestCase):
    def test_valid_gsap_pixi_release_passes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="engine-input-audit-") as directory:
            root = Path(directory)
            data = {
                "schema_version": 1,
                "shot_id": "scene-test",
                "clock": "hyperframes-absolute-seconds",
                "engines": {
                    "gsap-dom": {"ready": True},
                    "pixijs-webgpu": {
                        "ready": True,
                        "renderer_preference": "webgl",
                        "pixel_ratio": 1,
                        "effects": [
                            {
                                "id": "dust",
                                "preset": "hoof-dust",
                                "seed": "scene-test:dust",
                                "origin": [0.5, 0.8],
                                "start": 1.0,
                                "duration": 1.2,
                                "count": 20,
                                "opacity": 0.5,
                            }
                        ],
                    },
                },
            }
            errors, warnings = validate_engine_inputs(
                data,
                plan("gsap-dom", "pixijs-webgpu"),
                project_root=root,
                phase="release",
                check_paths=True,
            )
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_missing_seed_is_rejected(self) -> None:
        data = {
            "schema_version": 1,
            "shot_id": "scene-test",
            "clock": "hyperframes-absolute-seconds",
            "engines": {
                "pixijs-webgpu": {
                    "ready": True,
                    "renderer_preference": "webgpu",
                    "pixel_ratio": 1,
                    "effects": [
                        {
                            "id": "dust",
                            "preset": "impact-dust",
                            "origin": [0.5, 0.5],
                            "start": 0,
                            "duration": 1,
                            "count": 4,
                            "opacity": 1,
                        }
                    ],
                }
            },
        }
        errors, _ = validate_engine_inputs(
            data,
            plan("pixijs-webgpu"),
            project_root=Path("."),
            phase="release",
            check_paths=False,
        )
        self.assertTrue(any(".seed" in error for error in errors), errors)

    def test_blender_placeholder_is_forbidden_at_release(self) -> None:
        data = {
            "schema_version": 1,
            "shot_id": "scene-test",
            "clock": "hyperframes-absolute-seconds",
            "engines": {
                "blender": {
                    "ready": True,
                    "asset": "./assets/runtime/placeholders/pending-blender.webm",
                    "source_blend": "./shots/scene-test/assets/prerender/scene-test.blend",
                    "prerender_manifest": "./shots/scene-test/assets/prerender/prerender-manifest.json",
                    "physics_baked": True,
                }
            },
        }
        errors, _ = validate_engine_inputs(
            data,
            plan("blender"),
            project_root=Path("."),
            phase="release",
            check_paths=False,
        )
        self.assertTrue(any("placeholder" in error.lower() for error in errors), errors)

    def test_ready_blender_requires_real_source_media_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="engine-input-blender-") as directory:
            root = Path(directory)
            prerender = root / "shots" / "scene-test" / "assets" / "prerender"
            prerender.mkdir(parents=True)
            (prerender / "scene-test-alpha.webm").write_bytes(b"webm")
            (prerender / "scene-test.blend").write_bytes(b"blend")
            (prerender / "prerender-manifest.json").write_text(
                json.dumps({"physics_baked": True}), encoding="utf-8"
            )
            data = {
                "schema_version": 1,
                "shot_id": "scene-test",
                "clock": "hyperframes-absolute-seconds",
                "engines": {
                    "blender": {
                        "ready": True,
                        "asset": "./shots/scene-test/assets/prerender/scene-test-alpha.webm",
                        "source_blend": "./shots/scene-test/assets/prerender/scene-test.blend",
                        "prerender_manifest": "./shots/scene-test/assets/prerender/prerender-manifest.json",
                        "physics_baked": True,
                    }
                },
            }
            errors, warnings = validate_engine_inputs(
                data,
                plan("blender"),
                project_root=root,
                phase="release",
                check_paths=True,
            )
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_plan_input_engine_mismatch_is_rejected(self) -> None:
        data = {
            "schema_version": 1,
            "shot_id": "scene-test",
            "clock": "hyperframes-absolute-seconds",
            "engines": {"gsap-dom": {"ready": True}},
        }
        errors, _ = validate_engine_inputs(
            data,
            plan("gsap-dom", "three-webgpu"),
            project_root=Path("."),
            phase="development",
            check_paths=False,
        )
        self.assertTrue(any("three-webgpu" in error and "missing" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
