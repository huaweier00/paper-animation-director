#!/usr/bin/env python3
"""Unit tests for hybrid shot capability routing."""

from __future__ import annotations

import unittest

from route_shot_capabilities import DEFAULT_CONFIG, build_plan, validate_capabilities


def capabilities(**requirements):
    base_requirements = {
        "character_motion": "none",
        "contact": "none",
        "spatial_depth": "flat",
        "camera": "static",
        "particle_load": "none",
        "simulation": "none",
        "typography": "none",
        "reuse": "one-off",
        "environment_fx": [],
    }
    base_requirements.update(requirements)
    return {
        "schema_version": 1,
        "shot_id": "scene-test",
        "responsibility": "prove the routed visual capability",
        "requirements": base_requirements,
        "constraints": {
            "must_remain_2d": base_requirements["spatial_depth"] != "3d",
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
        "proof_requirements": ["the required change reads in the rendered shot"],
    }


class RouteTests(unittest.TestCase):
    def test_simple_tableau_uses_gsap(self):
        data = capabilities(typography="supporting")
        self.assertFalse([item for item in validate_capabilities(data) if item["severity"] == "error"])
        plan = build_plan(data, DEFAULT_CONFIG)
        self.assertEqual(plan["engines"], ["gsap-dom"])
        self.assertFalse(plan["benchmark_required"])

    def test_rigged_character_and_dust_uses_rive_pixijs(self):
        data = capabilities(
            character_motion="skeletal-2d",
            contact="continuous",
            spatial_depth="multiplane",
            camera="parallax",
            particle_load="light",
            environment_fx=["dust"],
            typography="supporting",
            reuse="recurring",
        )
        plan = build_plan(data, DEFAULT_CONFIG)
        self.assertEqual(set(plan["engines"]), {"rive", "pixijs-webgpu", "gsap-dom"})
        self.assertTrue(plan["benchmark_required"])

    def test_3d_space_reuses_three_for_heavy_particles(self):
        data = capabilities(
            spatial_depth="3d",
            camera="3d",
            particle_load="heavy",
            environment_fx=["snow"],
        )
        data["constraints"]["must_remain_2d"] = False
        plan = build_plan(data, DEFAULT_CONFIG)
        self.assertEqual(plan["engines"], ["three-webgpu"])
        roles = plan["layers"][0]["role"]
        self.assertIn("space", roles)
        self.assertIn("effects", roles)

    def test_simulated_contact_routes_blender(self):
        data = capabilities(
            character_motion="3d-rig",
            contact="simulated",
            spatial_depth="3d",
            camera="3d",
            simulation="baked-physics",
        )
        data["constraints"]["must_remain_2d"] = False
        plan = build_plan(data, DEFAULT_CONFIG)
        self.assertEqual(plan["engines"], ["blender"])
        self.assertEqual(plan["layers"][0]["integration"], "pre-render-alpha")

    def test_contradictory_3d_constraint_fails(self):
        data = capabilities(spatial_depth="3d")
        data["constraints"]["must_remain_2d"] = True
        errors = [item for item in validate_capabilities(data) if item["severity"] == "error"]
        self.assertTrue(any(item["path"] == "constraints.must_remain_2d" for item in errors))


if __name__ == "__main__":
    unittest.main()
