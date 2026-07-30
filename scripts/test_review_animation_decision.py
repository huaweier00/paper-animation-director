#!/usr/bin/env python3
"""Regression tests for context-sensitive animation decision review."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("review_animation_decision.py")
SPEC = importlib.util.spec_from_file_location("review_animation_decision", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def base_decision() -> dict:
    return {
        "shot_id": "scene-test",
        "shot_function": "show one decisive departure",
        "narrative_responsibility": "the audience sees the horse leave the enclosure",
        "responsibility_requires_visible_action": True,
        "required_visible_changes": ["the horse crosses the gate threshold and exits"],
        "evidence_is_presentation_only": False,
        "intentional_ellipsis_or_offscreen_action": False,
        "ellipsis_rationale": "",
        "action_carried_elsewhere": [],
        "architecture_choice": "one connected horse layer over an integrated enclosure",
        "merged_elements": ["the enclosure remains perspective-locked"],
        "independent_elements": ["the horse changes position relative to the gate"],
        "camera_and_presentation_role": "a still camera preserves the threshold",
        "why_this_choice": "one local change makes the departure clear without decorative motion",
        "alternatives_considered": ["a full-scene replacement was unnecessary"],
        "risk_flags": ["hoof contact and gatepost occlusion"],
        "proof_plan": ["review before, during, and after the threshold crossing"],
    }


class AnimationDecisionReviewTests(unittest.TestCase):
    def test_one_decisive_local_change_is_valid_without_layer_or_state_quotas(self) -> None:
        data = base_decision()
        errors, _, summary = MODULE.review(
            data,
            phase="planning",
            base=Path.cwd(),
            check_paths=False,
        )
        self.assertEqual(errors, [])
        self.assertEqual(summary["declared_change_count"], 1)

    def test_deliberate_long_still_tableau_is_valid(self) -> None:
        data = base_decision()
        data.update(
            {
                "shot_function": "let the empty stable register",
                "narrative_responsibility": "the audience understands and feels the horse's absence",
                "responsibility_requires_visible_action": False,
                "required_visible_changes": [],
                "evidence_is_presentation_only": True,
                "intentional_ellipsis_or_offscreen_action": True,
                "ellipsis_rationale": "the previous shot shows release; this shot is the consequence and pause",
                "action_carried_elsewhere": [
                    "previous shot shows the rope release",
                    "receding hoofbeats carry the escape"
                ],
                "architecture_choice": "one integrated, deliberately still tableau",
                "merged_elements": ["stable, rope, trough, and light remain integrated"],
                "independent_elements": [],
                "camera_and_presentation_role": "an optional slow drift lets the absence register",
                "why_this_choice": "local motion would weaken the emptiness",
                "alternatives_considered": ["decorative dust was rejected"],
                "risk_flags": [],
                "proof_plan": ["review whether the empty stall reads without captions"],
                "rendered_review": {
                    "mp4": "renders/empty-stable.mp4",
                    "observed_visible_changes": [],
                    "observed_evidence_is_presentation_only": True,
                    "responsibility_fulfilled": True,
                    "review_notes": "Stillness is intentional and the consequence reads."
                },
            }
        )
        errors, _, _ = MODULE.review(
            data,
            phase="release",
            base=Path.cwd(),
            check_paths=False,
        )
        self.assertEqual(errors, [])

    def test_moving_poster_cannot_claim_to_show_physical_action(self) -> None:
        data = base_decision()
        data.update(
            {
                "required_visible_changes": ["camera slowly pushes into the frozen full frame"],
                "evidence_is_presentation_only": True,
                "architecture_choice": "one frozen full-scene plate with a push-in",
                "merged_elements": ["all story subjects are baked into the plate"],
                "independent_elements": [],
                "camera_and_presentation_role": "the push-in is claimed as the departure",
                "why_this_choice": "reuse the still image",
                "alternatives_considered": [],
                "risk_flags": [],
                "proof_plan": ["review the final frame"],
            }
        )
        errors, _, _ = MODULE.review(
            data,
            phase="planning",
            base=Path.cwd(),
            check_paths=False,
        )
        self.assertTrue(
            any("presentation-only evidence" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
