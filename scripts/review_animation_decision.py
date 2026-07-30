#!/usr/bin/env python3
"""Review whether a shot's animation plan matches its declared responsibility.

This validator intentionally avoids universal duration, layer, pose, state, or cut
quotas. It rejects missing and contradictory directing logic, then leaves artistic
choices to rendered review.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_TEXT_FIELDS = (
    "shot_id",
    "shot_function",
    "narrative_responsibility",
    "architecture_choice",
    "why_this_choice",
    "camera_and_presentation_role",
)

REQUIRED_LIST_FIELDS = (
    "required_visible_changes",
    "action_carried_elsewhere",
    "merged_elements",
    "independent_elements",
    "alternatives_considered",
    "risk_flags",
    "proof_plan",
)

PRESENTATION_TERMS = (
    "camera",
    "zoom",
    "push",
    "pan",
    "crop",
    "frame",
    "parallax",
    "focus",
    "blur",
    "caption",
    "subtitle",
    "text",
    "label",
    "watermark",
    "grain",
    "vignette",
    "镜头",
    "推镜",
    "拉镜",
    "摇镜",
    "变焦",
    "缩放",
    "平移",
    "字幕",
    "文字",
    "水印",
    "颗粒",
)

def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def text_list(value: Any) -> bool:
    return isinstance(value, list) and all(nonempty_text(item) for item in value)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"decision file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(data, dict):
        raise ValueError("animation decision root must be an object")
    return data


def looks_presentation_only(changes: list[str]) -> bool:
    if not changes:
        return False
    normalized = [item.lower() for item in changes]
    return all(any(term in item for term in PRESENTATION_TERMS) for item in normalized)


def review(
    data: dict[str, Any],
    *,
    phase: str,
    base: Path,
    check_paths: bool,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_TEXT_FIELDS:
        if not nonempty_text(data.get(field)):
            errors.append(f"{field}: add a shot-specific explanation")

    for field in REQUIRED_LIST_FIELDS:
        value = data.get(field)
        if not text_list(value):
            errors.append(f"{field}: expected a list of non-empty strings")

    requires_action = data.get("responsibility_requires_visible_action")
    if not isinstance(requires_action, bool):
        errors.append(
            "responsibility_requires_visible_action: expected true or false"
        )
        requires_action = False

    intentional_ellipsis = data.get("intentional_ellipsis_or_offscreen_action")
    if not isinstance(intentional_ellipsis, bool):
        errors.append(
            "intentional_ellipsis_or_offscreen_action: expected true or false"
        )
        intentional_ellipsis = False

    changes = data.get("required_visible_changes")
    changes = changes if text_list(changes) else []
    evidence_is_presentation_only = data.get("evidence_is_presentation_only")
    if not isinstance(evidence_is_presentation_only, bool):
        errors.append("evidence_is_presentation_only: expected true or false")
        evidence_is_presentation_only = False
    carried_elsewhere = data.get("action_carried_elsewhere")
    carried_elsewhere = carried_elsewhere if text_list(carried_elsewhere) else []

    if requires_action and not changes and not intentional_ellipsis:
        errors.append(
            "The shot says it must show visible action but names no visible change "
            "and declares no intentional elliptical/off-screen treatment."
        )

    if requires_action and evidence_is_presentation_only and not intentional_ellipsis:
        errors.append(
            "The plan declares presentation-only evidence for a shot responsible for "
            "showing visible action. Name the story-state change, or document an intentional "
            "elliptical/off-screen treatment."
        )
    elif requires_action and looks_presentation_only(changes):
        warnings.append(
            "The visible-change wording appears presentation-focused. Confirm that it names "
            "the story-state evidence rather than only camera, text, or decoration."
        )

    if intentional_ellipsis:
        if not nonempty_text(data.get("ellipsis_rationale")):
            errors.append(
                "ellipsis_rationale: explain why stillness or off-screen action serves the shot"
            )
        if not carried_elsewhere:
            warnings.append(
                "Intentional ellipsis names no adjacent image, narration, or sound carrying "
                "the omitted action. Confirm that omission remains legible."
            )
    elif nonempty_text(data.get("ellipsis_rationale")):
        warnings.append(
            "ellipsis_rationale is present while intentional_ellipsis_or_offscreen_action is false"
        )

    if nonempty_text(data.get("architecture_choice")) and not (
        data.get("merged_elements") or data.get("independent_elements")
    ):
        warnings.append(
            "The architecture names neither merged nor independent elements. This can be "
            "valid for a deliberate still, but confirm that the description is specific."
        )

    proof_plan = data.get("proof_plan")
    if text_list(proof_plan) and not proof_plan:
        errors.append("proof_plan: add at least one way to judge the declared responsibility")

    alternatives = data.get("alternatives_considered")
    if text_list(alternatives) and not alternatives:
        warnings.append(
            "alternatives_considered is empty; record why a simpler or different construction "
            "was not preferable."
        )

    rendered = data.get("rendered_review")
    if phase == "release":
        if not isinstance(rendered, dict):
            errors.append("rendered_review: required for release")
        else:
            mp4_value = rendered.get("mp4")
            if not nonempty_text(mp4_value):
                errors.append("rendered_review.mp4: provide the reviewed render path")
            elif check_paths:
                mp4_path = Path(mp4_value)
                mp4_path = mp4_path if mp4_path.is_absolute() else base / mp4_path
                if not mp4_path.is_file():
                    errors.append(f"rendered_review.mp4: file does not exist: {mp4_path}")

            observed = rendered.get("observed_visible_changes")
            if not text_list(observed):
                errors.append(
                    "rendered_review.observed_visible_changes: expected a list of non-empty strings"
                )
                observed = []

            observed_presentation_only = rendered.get(
                "observed_evidence_is_presentation_only"
            )
            if not isinstance(observed_presentation_only, bool):
                errors.append(
                    "rendered_review.observed_evidence_is_presentation_only: expected true or false"
                )
                observed_presentation_only = False

            fulfilled = rendered.get("responsibility_fulfilled")
            if fulfilled is not True:
                errors.append(
                    "rendered_review.responsibility_fulfilled: must be true before release"
                )

            if not nonempty_text(rendered.get("review_notes")):
                errors.append(
                    "rendered_review.review_notes: explain why the rendered shot fulfils its responsibility"
                )

            if requires_action and not observed and not intentional_ellipsis:
                errors.append(
                    "The released shot is responsible for visible action but records no observed "
                    "visible change."
                )

            if (
                requires_action
                and observed_presentation_only
                and not intentional_ellipsis
            ):
                errors.append(
                    "The rendered review declares presentation-only evidence for a required "
                    "visible action."
                )
            elif requires_action and looks_presentation_only(observed):
                warnings.append(
                    "The observed-change wording appears presentation-focused. Re-check the "
                    "render for story-state evidence."
                )

    summary = {
        "shot_id": data.get("shot_id"),
        "phase": phase,
        "requires_visible_action": requires_action,
        "intentional_ellipsis": intentional_ellipsis,
        "declared_change_count": len(changes),
        "rule_profile": "contradiction-checks-without-artistic-quotas",
    }
    return errors, warnings, summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Review shot responsibility and animation rationale without imposing "
            "duration, layer, pose, state, or cut quotas."
        )
    )
    parser.add_argument("decision", type=Path)
    parser.add_argument(
        "--phase",
        choices=("planning", "release"),
        default="planning",
    )
    parser.add_argument(
        "--skip-path-checks",
        action="store_true",
        help="Validate the release record without checking the referenced MP4 path.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        data = load_json(args.decision)
        errors, warnings, summary = review(
            data,
            phase=args.phase,
            base=args.decision.resolve().parent,
            check_paths=not args.skip_path_checks,
        )
    except ValueError as exc:
        errors, warnings, summary = [str(exc)], [], {}

    result = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        if errors:
            print("FAIL: directing decision is incomplete or contradicts its claimed evidence")
        else:
            print("PASS: directing logic is reviewable; artistic choices remain context-dependent")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
