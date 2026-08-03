#!/usr/bin/env python3
"""Validate a paper-animation story manifest and report actionable findings."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VALID_ASPECTS = {"16:9", "9:16", "1:1", "4:5"}
VALID_SUBTITLES = {"none", "zh", "en", "zh-en", "source", "bilingual"}
VALID_AUDIO = {"dialogue-only", "full-mix", "stems", "silent"}
VALID_PHASES = {"editorial", "production", "release"}
SOCIAL_DESTINATIONS = {"douyin", "reels", "shorts", "social-feed"}
VALID_DIRECTIONS = {"left-to-right", "right-to-left", "stationary"}
VALID_FACINGS = {"left", "right", "front"}
VALID_PRODUCTION_STATUS = {
    "draft",
    "semantic-approved",
    "space-approved",
    "assets-generated",
    "assets-approved",
    "animated",
    "reviewed",
}
IDENTITY_PURPOSE = "identity-consistency-reference-only"
MODEL_PACK_STATUS = "approved"
SHOT_ASSET_POLICY = "shot-just-in-time"
REQUIRED_PROTECTED_REGIONS = {"head", "face", "hands", "feet", "action-contact"}
REQUIRED_LOOKDEV_ROLES = {"opening-pressure", "central-choice", "consequence-save"}
REQUIRED_SELECTION_DIMENSIONS = {
    "semantics",
    "silhouette-pose",
    "identity-anatomy",
    "composition",
    "value-color",
    "light-depth",
    "finish",
    "distinctiveness",
}


def finding(severity: str, path: str, message: str) -> dict[str, str]:
    return {"severity": severity, "path": path, "message": message}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_zone(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value)
        and 0 <= value[0] < value[2] <= 1
        and 0 <= value[1] < value[3] <= 1
    )


def validate_social_contract(
    data: dict[str, Any],
    project_dir: Path | None,
    phase: str,
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    platform = data.get("platform")
    if not isinstance(platform, dict):
        return out
    destination = str(platform.get("destination", "")).strip().lower()
    if destination not in SOCIAL_DESTINATIONS:
        return out

    if not nonempty(platform.get("primary_audience")):
        out.append(finding("error", "platform.primary_audience", "name one primary audience for the social edit"))
    if platform.get("quality_posture") != "premium-quality-first":
        out.append(finding("error", "platform.quality_posture", "set premium-quality-first for the精品 social route"))
    if platform.get("distribution_mode") not in {"feed-native", "horizontal-longform", "cross-platform"}:
        out.append(finding("error", "platform.distribution_mode", "declare feed-native, horizontal-longform, or cross-platform"))

    aspect = data.get("aspect")
    aspect_decision = platform.get("aspect_decision")
    if not isinstance(aspect_decision, dict):
        out.append(finding("error", "platform.aspect_decision", "record the selected ratio, reason, and feed-preview requirement"))
    else:
        if aspect_decision.get("selected") != aspect:
            out.append(finding("error", "platform.aspect_decision.selected", "match the manifest aspect"))
        if not nonempty(aspect_decision.get("reason")):
            out.append(finding("error", "platform.aspect_decision.reason", "explain how the ratio serves the story in the feed"))
        if aspect_decision.get("feed_preview_required") is not True:
            out.append(finding("error", "platform.aspect_decision.feed_preview_required", "require a real-size vertical-feed preview"))
        if platform.get("distribution_mode") == "feed-native" and aspect != "9:16" and not nonempty(
            aspect_decision.get("non_native_ratio_justification")
        ):
            out.append(
                finding(
                    "error",
                    "platform.aspect_decision.non_native_ratio_justification",
                    "justify a non-9:16 feed-native composition and prove it in the feed preview",
                )
            )

    contract = data.get("social_contract")
    if not isinstance(contract, dict):
        return out + [finding("error", "social_contract", "add the social editorial, opening, value, packaging, and animatic contract")]
    for field, message in (
        ("editorial_promise", "state the concrete viewer payoff"),
        ("familiarity_gap", "state what this treatment adds beyond a familiar plot"),
    ):
        if not nonempty(contract.get(field)):
            out.append(finding("error", f"social_contract.{field}", message))

    opening = contract.get("opening")
    if not isinstance(opening, dict):
        out.append(finding("error", "social_contract.opening", "declare first frame, first line, and proof by three seconds"))
    else:
        for field in ("first_frame_event", "first_spoken_line", "cover_to_opening_match"):
            if not nonempty(opening.get(field)):
                out.append(finding("error", f"social_contract.opening.{field}", "required for the opening contract"))
        for field in ("promise_by", "visual_proof_by"):
            value = opening.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= float(value) <= 3.0:
                out.append(finding("error", f"social_contract.opening.{field}", "use a timestamp from 0.0 through 3.0 seconds"))
        if opening.get("logo_before_promise") is not False:
            out.append(finding("error", "social_contract.opening.logo_before_promise", "set false; prove the promise before branding"))

    value = contract.get("value")
    if not isinstance(value, dict):
        out.append(finding("error", "social_contract.value", "declare the transferable insight, modern connection, and save object"))
    else:
        for field in ("transferable_insight", "modern_connection"):
            if not nonempty(value.get(field)):
                out.append(finding("error", f"social_contract.value.{field}", "required for a useful social payoff"))
        save_object = value.get("save_object")
        if not isinstance(save_object, dict):
            out.append(finding("error", "social_contract.value.save_object", "declare a concrete reusable save object"))
        else:
            if not nonempty(save_object.get("type")):
                out.append(finding("error", "social_contract.value.save_object.type", "name the card, framework, quote, comparison, or sourced reference"))
            content = save_object.get("content")
            if not isinstance(content, list) or not content or any(not nonempty(item) for item in content):
                out.append(finding("error", "social_contract.value.save_object.content", "provide non-empty audience-facing content"))
            hold = save_object.get("on_screen_hold")
            if not isinstance(hold, (int, float)) or isinstance(hold, bool) or hold <= 0:
                out.append(finding("error", "social_contract.value.save_object.on_screen_hold", "record a positive readable hold measured in the animatic"))
            if phase in {"production", "release"} and save_object.get("readability_review") != "approved":
                out.append(finding("error", "social_contract.value.save_object.readability_review", "approve the save object at feed size before production"))

    packaging = contract.get("packaging")
    if not isinstance(packaging, dict):
        out.append(finding("error", "social_contract.packaging", "declare series label, episode-first cover, subjects, match, and thumbnail review"))
    else:
        for field in ("series_label", "episode_title", "cover_copy", "feed_to_opening_match", "pinned_question"):
            if not nonempty(packaging.get(field)):
                out.append(finding("error", f"social_contract.packaging.{field}", "required for the social publishing contract"))
        subjects = packaging.get("cover_subjects")
        if not isinstance(subjects, list) or not subjects or any(not nonempty(item) for item in subjects):
            out.append(finding("error", "social_contract.packaging.cover_subjects", "list the readable conflict subjects and critical objects"))
        if phase in {"production", "release"} and packaging.get("feed_to_opening_match") != "approved":
            out.append(finding("error", "social_contract.packaging.feed_to_opening_match", "approve that the cover promise is fulfilled by the opening"))
        if phase == "release" and packaging.get("thumbnail_review") != "approved":
            out.append(finding("error", "social_contract.packaging.thumbnail_review", "approve the cover at thumbnail size"))

    animatic = contract.get("animatic")
    if not isinstance(animatic, dict):
        out.append(finding("error", "social_contract.animatic", "record hook and full scratch animatics plus review decisions"))
    else:
        for field in ("hook_animatic", "full_scratch_animatic", "review_notes"):
            if not nonempty(animatic.get(field)):
                out.append(finding("error", f"social_contract.animatic.{field}", "required for auditable editorial proof"))
        for field in ("hook_review", "full_edit_review"):
            status = animatic.get(field)
            if status not in {"pending", "approved", "rejected", "needs-fix"}:
                out.append(finding("error", f"social_contract.animatic.{field}", "expected pending, approved, rejected, or needs-fix"))
            elif phase in {"production", "release"} and status != "approved":
                out.append(finding("error", f"social_contract.animatic.{field}", "premium production remains locked until approved"))
        if project_dir and phase in {"production", "release"}:
            for field in ("hook_animatic", "full_scratch_animatic"):
                value_path = animatic.get(field)
                if nonempty(value_path) and not (project_dir / value_path).is_file():
                    out.append(finding("warning", f"social_contract.animatic.{field}", "approved animatic file does not exist at the declared project path"))

    if phase == "release":
        delivery = data.get("delivery")
        if not isinstance(delivery, dict):
            out.append(finding("error", "delivery", "social release requires feed and cover proof"))
        else:
            for field in ("feed_simulation", "cover_full", "cover_thumbnail", "save_object_frame"):
                if not nonempty(delivery.get(field)):
                    out.append(finding("error", f"delivery.{field}", "required for social release proof"))
                elif project_dir and not (project_dir / str(delivery[field])).is_file():
                    out.append(finding("warning", f"delivery.{field}", "declared social release proof does not exist at the project path"))
            for field in ("feed_simulation_review", "cover_review"):
                if delivery.get(field) != "approved":
                    out.append(finding("error", f"delivery.{field}", "expected approved before social release"))
    return out


def validate_visual_direction(
    data: dict[str, Any],
    project_dir: Path | None,
    phase: str,
    *,
    required: bool,
) -> list[dict[str, str]]:
    """Validate premium look-development and asset-curation gates."""
    out: list[dict[str, str]] = []
    visual = data.get("visual_direction")
    if not isinstance(visual, dict):
        if required and phase in {"production", "release"}:
            out.append(
                finding(
                    "error",
                    "visual_direction",
                    "add and approve the V0-V4 visual-direction contract before premium identity or shot assets",
                )
            )
        return out

    audience = visual.get("audience_layers")
    if not isinstance(audience, dict):
        out.append(finding("error", "visual_direction.audience_layers", "declare immediate and adult/repeat-viewer reads"))
    else:
        for field in ("immediate_read", "adult_reward"):
            if not nonempty(audience.get(field)):
                out.append(finding("error", f"visual_direction.audience_layers.{field}", "required for two-layer audience design"))

    for field, message in (
        ("emotional_promise", "state the visual feeling arc"),
        ("collectible_frame_goal", "state which frame earns pause, rewatch, or collection"),
        ("undesirable_impression", "name the cheap, generic, or off-tone impression to reject"),
        ("art_route", "name the selected visual world"),
        ("signature", "declare one memorable authored visual idea"),
    ):
        if not nonempty(visual.get(field)):
            out.append(finding("error", f"visual_direction.{field}", message))

    required_text_blocks = {
        "shape_language": ("heroes", "threat", "environment", "critical_props"),
        "lighting_and_depth": ("key_light", "depth_plan", "contact_shadow_policy"),
        "composition": ("big_medium_small", "negative_space", "phone_focal_point", "subtitle_integration"),
    }
    for block_name, fields in required_text_blocks.items():
        block = visual.get(block_name)
        if not isinstance(block, dict):
            out.append(finding("error", f"visual_direction.{block_name}", "add the complete visual-system block"))
            continue
        for field in fields:
            if not nonempty(block.get(field)):
                out.append(finding("error", f"visual_direction.{block_name}.{field}", "required for the selected visual system"))

    value_design = visual.get("value_design")
    if not isinstance(value_design, dict):
        out.append(finding("error", "visual_direction.value_design", "declare focal and dark/light mass hierarchy"))
    else:
        for field in ("focal_subject", "subject_background_separation", "mass_policy"):
            if not nonempty(value_design.get(field)):
                out.append(finding("error", f"visual_direction.value_design.{field}", "required for value hierarchy"))
        focal_order = value_design.get("focal_order")
        if not isinstance(focal_order, list) or not focal_order or any(not nonempty(item) for item in focal_order):
            out.append(finding("error", "visual_direction.value_design.focal_order", "list the intended first, second, and later reads"))

    color_script = visual.get("color_script")
    if not isinstance(color_script, dict):
        out.append(finding("error", "visual_direction.color_script", "declare a restrained palette and emotional color behavior"))
    else:
        palette = color_script.get("base_palette")
        if not isinstance(palette, list) or not palette or any(not nonempty(item) for item in palette):
            out.append(finding("error", "visual_direction.color_script.base_palette", "list the approved base color families"))
        for field in ("accent_policy", "emotional_arc"):
            if not nonempty(color_script.get(field)):
                out.append(finding("error", f"visual_direction.color_script.{field}", "required for consistent color behavior"))

    line_texture = visual.get("line_and_texture")
    if not isinstance(line_texture, dict):
        out.append(finding("error", "visual_direction.line_and_texture", "declare line, texture, and forbidden surface rules"))
    else:
        for field in ("line_rule", "texture_rule"):
            if not nonempty(line_texture.get(field)):
                out.append(finding("error", f"visual_direction.line_and_texture.{field}", "required for medium consistency"))
        forbidden = line_texture.get("surface_forbidden")
        if not isinstance(forbidden, list) or not forbidden or any(not nonempty(item) for item in forbidden):
            out.append(finding("error", "visual_direction.line_and_texture.surface_forbidden", "list rejected surface traits"))

    anti_generic = visual.get("anti_generic")
    forbidden_traits = anti_generic.get("forbidden_traits") if isinstance(anti_generic, dict) else None
    if not isinstance(forbidden_traits, list) or not forbidden_traits or any(not nonempty(item) for item in forbidden_traits):
        out.append(finding("error", "visual_direction.anti_generic.forbidden_traits", "add project-specific generic-AI failure traits"))

    lookdev = visual.get("lookdev")
    if not isinstance(lookdev, dict):
        out.append(finding("error", "visual_direction.lookdev", "record route comparison, hero frames, integration benchmark, and style lock"))
    else:
        routes = lookdev.get("route_candidates")
        route_ids: set[str] = set()
        if not isinstance(routes, list) or len(routes) < 3:
            out.append(finding("error", "visual_direction.lookdev.route_candidates", "compare at least three materially different art routes"))
            routes = []
        for index, route in enumerate(routes):
            base = f"visual_direction.lookdev.route_candidates[{index}]"
            if not isinstance(route, dict):
                out.append(finding("error", base, "route candidate must be an object"))
                continue
            route_id = route.get("id")
            if not nonempty(route_id) or route_id in route_ids:
                out.append(finding("error", f"{base}.id", "use a unique non-empty route id"))
            else:
                route_ids.add(route_id)
            for field in ("differentiator", "strengths", "risks", "audience_impression"):
                if not nonempty(route.get(field)):
                    out.append(finding("error", f"{base}.{field}", "required for a meaningful route comparison"))
        selected_route = lookdev.get("selected_route")
        if selected_route not in route_ids:
            out.append(finding("error", "visual_direction.lookdev.selected_route", "select one declared route candidate"))
        if not nonempty(lookdev.get("selection_rationale")):
            out.append(finding("error", "visual_direction.lookdev.selection_rationale", "explain why the route won and what risks remain"))

        hero_frames = lookdev.get("hero_frames")
        seen_roles: set[str] = set()
        if not isinstance(hero_frames, list):
            out.append(finding("error", "visual_direction.lookdev.hero_frames", "add reference-only opening, choice, and consequence frames"))
            hero_frames = []
        for index, frame in enumerate(hero_frames):
            base = f"visual_direction.lookdev.hero_frames[{index}]"
            if not isinstance(frame, dict):
                out.append(finding("error", base, "hero frame must be an object"))
                continue
            role = frame.get("role")
            if role not in REQUIRED_LOOKDEV_ROLES or role in seen_roles:
                out.append(finding("error", f"{base}.role", f"use each role exactly once: {sorted(REQUIRED_LOOKDEV_ROLES)}"))
            else:
                seen_roles.add(role)
            frame_path = frame.get("path")
            if not nonempty(frame_path):
                out.append(finding("error", f"{base}.path", "record the look-development frame path"))
            elif project_dir and phase in {"production", "release"} and not (project_dir / frame_path).is_file():
                out.append(finding("warning", f"{base}.path", "declared look-development frame does not exist at the project path"))
            if frame.get("reference_only") is not True:
                out.append(finding("error", f"{base}.reference_only", "set true; look-development frames are not production assets"))
        missing_roles = sorted(REQUIRED_LOOKDEV_ROLES - seen_roles)
        if missing_roles:
            out.append(finding("error", "visual_direction.lookdev.hero_frames", f"missing roles: {', '.join(missing_roles)}"))

        integration = lookdev.get("integration_benchmark")
        if not isinstance(integration, dict):
            out.append(finding("error", "visual_direction.lookdev.integration_benchmark", "prove character, prop, and environment in one reference composite"))
        else:
            integration_path = integration.get("path")
            if not nonempty(integration_path):
                out.append(finding("error", "visual_direction.lookdev.integration_benchmark.path", "record the integration benchmark path"))
            elif project_dir and phase in {"production", "release"} and not (project_dir / integration_path).is_file():
                out.append(finding("warning", "visual_direction.lookdev.integration_benchmark.path", "declared integration benchmark does not exist at the project path"))
            if integration.get("reference_only") is not True:
                out.append(finding("error", "visual_direction.lookdev.integration_benchmark.reference_only", "set true; benchmark art is not a shot asset"))
            if phase in {"production", "release"} and integration.get("review") != "approved":
                out.append(finding("error", "visual_direction.lookdev.integration_benchmark.review", "approve character/environment integration before production"))

        for field in ("phone_size_review", "grayscale_review", "blur_focal_review", "anti_generic_review", "style_lock"):
            status = lookdev.get(field)
            if status not in {"pending", "approved", "rejected", "needs-fix"}:
                out.append(finding("error", f"visual_direction.lookdev.{field}", "expected pending, approved, rejected, or needs-fix"))
            elif phase in {"production", "release"} and status != "approved":
                out.append(finding("error", f"visual_direction.lookdev.{field}", "premium production remains locked until approved"))

    policy = visual.get("asset_policy")
    if not isinstance(policy, dict):
        out.append(finding("error", "visual_direction.asset_policy", "declare candidate, rejection, composite, display-scale, and upscale rules"))
    else:
        for field in ("candidate_comparison_required", "rejection_log_required", "composite_test_required", "intended_display_scale_required", "upscale_after_composition_approval"):
            if policy.get(field) is not True:
                out.append(finding("error", f"visual_direction.asset_policy.{field}", "set true for premium asset curation"))
        if policy.get("first_plausible_auto_accept") is not False:
            out.append(finding("error", "visual_direction.asset_policy.first_plausible_auto_accept", "set false; compare candidates instead of auto-approving the first plausible result"))
        dimensions = policy.get("selection_dimensions")
        dimension_set = {item for item in dimensions if isinstance(item, str)} if isinstance(dimensions, list) else set()
        missing_dimensions = sorted(REQUIRED_SELECTION_DIMENSIONS - dimension_set)
        if missing_dimensions:
            out.append(finding("error", "visual_direction.asset_policy.selection_dimensions", f"include: {', '.join(missing_dimensions)}"))
    return out


def zone_center(zone: list[float]) -> tuple[float, float]:
    return ((float(zone[0]) + float(zone[2])) / 2, (float(zone[1]) + float(zone[3])) / 2)


def zone_contains(container: list[float], inner: list[float], tolerance: float = 1e-6) -> bool:
    return (
        float(container[0]) <= float(inner[0]) + tolerance
        and float(container[1]) <= float(inner[1]) + tolerance
        and float(container[2]) + tolerance >= float(inner[2])
        and float(container[3]) + tolerance >= float(inner[3])
    )


def zones_overlap(first: list[float], second: list[float]) -> bool:
    return not (
        float(first[2]) <= float(second[0])
        or float(second[2]) <= float(first[0])
        or float(first[3]) <= float(second[1])
        or float(second[3]) <= float(first[1])
    )


def validate_manifest(
    data: Any,
    project_dir: Path | None = None,
    phase: str = "production",
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [finding("error", "$", "manifest root must be a JSON object")]
    if phase not in VALID_PHASES:
        return [finding("error", "$phase", f"expected one of {sorted(VALID_PHASES)}")]

    project = data.get("project")
    if not nonempty(project):
        out.append(finding("error", "project", "project is required"))
    elif not ID_RE.match(project):
        out.append(finding("error", "project", "use lowercase letters, digits, and hyphens only"))

    if not nonempty(data.get("story")):
        out.append(finding("error", "story", "story is required"))
    if not nonempty(data.get("message")):
        out.append(finding("warning", "message", "record the intended takeaway or emotional destination"))

    aspect = data.get("aspect", "16:9")
    if aspect not in VALID_ASPECTS:
        out.append(finding("error", "aspect", f"expected one of {sorted(VALID_ASPECTS)}"))
    fps = data.get("fps", 30)
    if fps not in {24, 30, 60}:
        out.append(finding("error", "fps", "fps must be 24, 30, or 60"))
    if data.get("subtitle_mode", "zh") not in VALID_SUBTITLES:
        out.append(finding("error", "subtitle_mode", f"expected one of {sorted(VALID_SUBTITLES)}"))
    if data.get("audio_mode", "dialogue-only") not in VALID_AUDIO:
        out.append(finding("error", "audio_mode", f"expected one of {sorted(VALID_AUDIO)}"))

    platform = data.get("platform")
    social_route = isinstance(platform, dict) and str(platform.get("destination", "")).strip().lower() in SOCIAL_DESTINATIONS
    premium_route = isinstance(platform, dict) and platform.get("quality_posture") == "premium-quality-first"
    out.extend(validate_social_contract(data, project_dir, phase))
    out.extend(validate_visual_direction(data, project_dir, phase, required=social_route or premium_route))

    characters = data.get("characters")
    character_ids: set[str] = set()
    if not isinstance(characters, list) or not characters:
        out.append(finding("error", "characters", "add at least one recurring character"))
        characters = []
    for index, char in enumerate(characters):
        base = f"characters[{index}]"
        if not isinstance(char, dict):
            out.append(finding("error", base, "character must be an object"))
            continue
        char_id = char.get("id")
        if not nonempty(char_id) or not ID_RE.match(char_id):
            out.append(finding("error", f"{base}.id", "use a non-empty kebab-case id"))
        elif char_id in character_ids:
            out.append(finding("error", f"{base}.id", f"duplicate character id {char_id!r}"))
        else:
            character_ids.add(char_id)
        if not nonempty(char.get("description")):
            out.append(finding("error", f"{base}.description", "describe stable identity and silhouette"))
        identity = char.get("identity_reference")
        if not isinstance(identity, dict):
            out.append(
                finding(
                    "error",
                    f"{base}.identity_reference",
                    "use a reference-only identity object, not a path string or animation asset",
                )
            )
        else:
            identity_path = identity.get("path")
            if not nonempty(identity_path):
                out.append(finding("error", f"{base}.identity_reference.path", "add the approved frontal identity path"))
            elif project_dir and not (project_dir / identity_path).exists():
                out.append(finding("warning", f"{base}.identity_reference.path", "referenced identity image does not exist yet"))
            if identity.get("view") != "front":
                out.append(finding("error", f"{base}.identity_reference.view", "identity lock requires exactly one frontal view"))
            if identity.get("framing") != "full-body":
                out.append(finding("error", f"{base}.identity_reference.framing", "use a full-body frontal identity reference"))
            if identity.get("pose") != "neutral":
                out.append(finding("error", f"{base}.identity_reference.pose", "identity reference must use a neutral non-story pose"))
            if identity.get("purpose") != IDENTITY_PURPOSE:
                out.append(
                    finding(
                        "error",
                        f"{base}.identity_reference.purpose",
                        f"set purpose to {IDENTITY_PURPOSE!r}",
                    )
                )
            if identity.get("animation_use") is not False:
                out.append(
                    finding(
                        "error",
                        f"{base}.identity_reference.animation_use",
                        "set false; the frontal identity image must never enter the animation",
                    )
                )
            if identity.get("approved") is not True:
                out.append(finding("error", f"{base}.identity_reference.approved", "approve identity before shot asset generation"))
        model_pack = char.get("identity_model_pack")
        model_pack_required = (social_route or premium_route) and phase in {"production", "release"}
        if not isinstance(model_pack, dict):
            if model_pack_required:
                out.append(
                    finding(
                        "error",
                        f"{base}.identity_model_pack",
                        "add an approved reference-only model pack after animatic/style lock",
                    )
                )
        else:
            if model_pack.get("status") != MODEL_PACK_STATUS and model_pack_required:
                out.append(finding("error", f"{base}.identity_model_pack.status", "approve the model pack before shot asset generation"))
            if model_pack.get("reference_only") is not True:
                out.append(finding("error", f"{base}.identity_model_pack.reference_only", "model-pack images guide production but never enter a shot"))
            if model_pack.get("animation_use") is not False:
                out.append(finding("error", f"{base}.identity_model_pack.animation_use", "set false; generate separate shot production assets"))
            views = model_pack.get("views")
            view_names: set[str] = set()
            if not isinstance(views, list) or not views:
                out.append(finding("error", f"{base}.identity_model_pack.views", "provide the controlled views required by the approved sequence layout"))
            else:
                for view_index, view in enumerate(views):
                    view_base = f"{base}.identity_model_pack.views[{view_index}]"
                    if not isinstance(view, dict):
                        out.append(finding("error", view_base, "view must be an object"))
                        continue
                    view_name = view.get("view")
                    if not nonempty(view_name):
                        out.append(finding("error", f"{view_base}.view", "name the controlled camera-facing view"))
                    else:
                        view_names.add(str(view_name))
                    view_path = view.get("path")
                    if not nonempty(view_path):
                        out.append(finding("error", f"{view_base}.path", "provide the approved reference path"))
                    elif project_dir and not (project_dir / str(view_path)).exists():
                        out.append(finding("warning", f"{view_base}.path", "referenced model-pack image does not exist yet"))
            if model_pack_required and not {"left-profile", "right-profile"}.issubset(view_names):
                out.append(finding("error", f"{base}.identity_model_pack.views", "premium recurring characters require both left-profile and right-profile evidence"))
            for field in ("scale_reference", "asymmetry_notes", "expression_range", "attachment_rules", "forbidden_variations"):
                value = model_pack.get(field)
                if field == "forbidden_variations":
                    if not isinstance(value, list) or not value or any(not nonempty(item) for item in value):
                        out.append(finding("error", f"{base}.identity_model_pack.{field}", "provide non-empty forbidden variations"))
                elif not nonempty(value):
                    out.append(finding("error", f"{base}.identity_model_pack.{field}", "required for repeatable identity and rig decisions"))
        if "required_poses" in char:
            out.append(
                finding(
                    "error",
                    f"{base}.required_poses",
                    "remove global pose inventory; derive concrete poses inside each approved shot asset plan",
                )
            )

    scenes = data.get("scenes")
    scene_ids: set[str] = set()
    if not isinstance(scenes, list) or not scenes:
        out.append(finding("error", "scenes", "add at least one scene"))
        scenes = []
    total_duration = 0.0
    for index, scene in enumerate(scenes):
        base = f"scenes[{index}]"
        if not isinstance(scene, dict):
            out.append(finding("error", base, "scene must be an object"))
            continue
        scene_id = scene.get("id")
        if not nonempty(scene_id) or not ID_RE.match(scene_id):
            out.append(finding("error", f"{base}.id", "use a non-empty kebab-case id"))
        elif scene_id in scene_ids:
            out.append(finding("error", f"{base}.id", f"duplicate scene id {scene_id!r}"))
        else:
            scene_ids.add(scene_id)
        if not nonempty(scene.get("narrative_goal")):
            out.append(finding("error", f"{base}.narrative_goal", "state what the audience must understand"))
        if not isinstance(scene.get("narration", ""), str):
            out.append(finding("error", f"{base}.narration", "narration must be a string"))
        production_status = scene.get("production_status")
        if production_status not in VALID_PRODUCTION_STATUS:
            out.append(
                finding(
                    "error",
                    f"{base}.production_status",
                    f"expected one of {sorted(VALID_PRODUCTION_STATUS)}",
                )
            )
        duration = scene.get("duration")
        if not isinstance(duration, (int, float)) or duration <= 0:
            out.append(finding("error", f"{base}.duration", "provide a positive measured/planned duration"))
            duration_value = 0.0
        else:
            duration_value = float(duration)
            total_duration += duration_value

        spatial = scene.get("spatial_contract")
        actor_contracts: dict[str, dict[str, Any]] = {}
        target_contracts: dict[str, dict[str, Any]] = {}
        reserved_contracts: dict[str, dict[str, Any]] = {}
        occluder_contracts: dict[str, dict[str, Any]] = {}
        if not isinstance(spatial, dict):
            out.append(finding("error", f"{base}.spatial_contract", "approve a shot spatial contract before asset generation"))
            spatial = {}
        if spatial.get("coordinate_system") != "normalized-screen":
            out.append(
                finding(
                    "error",
                    f"{base}.spatial_contract.coordinate_system",
                    "use normalized-screen coordinates with zones in [left, top, right, bottom] form",
                )
            )

        camera = spatial.get("camera")
        if not isinstance(camera, dict):
            out.append(finding("error", f"{base}.spatial_contract.camera", "declare camera view, axis, floor line, and light direction"))
        else:
            if not nonempty(camera.get("view")):
                out.append(finding("error", f"{base}.spatial_contract.camera.view", "camera view is required"))
            if camera.get("axis") not in {"locked", "re-established"}:
                out.append(finding("error", f"{base}.spatial_contract.camera.axis", "lock or visibly re-establish the continuity axis"))
            floor_line = camera.get("floor_line")
            if not isinstance(floor_line, (int, float)) or isinstance(floor_line, bool) or not 0 <= floor_line <= 1:
                out.append(finding("error", f"{base}.spatial_contract.camera.floor_line", "use a normalized floor line from 0 to 1"))
            if not nonempty(camera.get("light_direction")):
                out.append(finding("error", f"{base}.spatial_contract.camera.light_direction", "light direction is required"))

        for collection_name in ("surfaces", "props"):
            collection = spatial.get(collection_name, [])
            if not isinstance(collection, list):
                out.append(finding("error", f"{base}.spatial_contract.{collection_name}", "expected a list"))
                collection = []
            for target_index, target in enumerate(collection):
                target_base = f"{base}.spatial_contract.{collection_name}[{target_index}]"
                if not isinstance(target, dict):
                    out.append(finding("error", target_base, "target must be an object"))
                    continue
                target_id = target.get("id")
                if not nonempty(target_id) or not ID_RE.match(target_id):
                    out.append(finding("error", f"{target_base}.id", "use a non-empty kebab-case target id"))
                elif target_id in target_contracts:
                    out.append(finding("error", f"{target_base}.id", f"duplicate spatial target id {target_id!r}"))
                else:
                    target_contracts[target_id] = target
                if not nonempty(target.get("type")):
                    out.append(finding("error", f"{target_base}.type", "declare the target's semantic type"))
                if not valid_zone(target.get("zone")):
                    out.append(finding("error", f"{target_base}.zone", "use a normalized [left, top, right, bottom] zone"))
                if not isinstance(target.get("supports_actions"), list):
                    out.append(finding("error", f"{target_base}.supports_actions", "declare the actions this target supports"))

        reserved = spatial.get("reserved_zones")
        if not isinstance(reserved, list) or not reserved:
            out.append(finding("error", f"{base}.spatial_contract.reserved_zones", "reserve at least one clear actor or ensemble corridor"))
            reserved = []
        for zone_index, reserved_zone in enumerate(reserved):
            zone_base = f"{base}.spatial_contract.reserved_zones[{zone_index}]"
            if not isinstance(reserved_zone, dict):
                out.append(finding("error", zone_base, "reserved zone must be an object"))
                continue
            zone_id = reserved_zone.get("id")
            if not nonempty(zone_id) or not ID_RE.match(zone_id):
                out.append(finding("error", f"{zone_base}.id", "use a non-empty kebab-case zone id"))
            elif zone_id in reserved_contracts:
                out.append(finding("error", f"{zone_base}.id", f"duplicate reserved-zone id {zone_id!r}"))
            else:
                reserved_contracts[zone_id] = reserved_zone
            if not valid_zone(reserved_zone.get("zone")):
                out.append(finding("error", f"{zone_base}.zone", "use a normalized [left, top, right, bottom] zone"))
            if reserved_zone.get("must_remain_clear") is not True:
                out.append(finding("error", f"{zone_base}.must_remain_clear", "set true for motion and contact corridors"))

        obstacles = spatial.get("obstacles", [])
        if not isinstance(obstacles, list):
            out.append(finding("error", f"{base}.spatial_contract.obstacles", "expected a list"))
            obstacles = []
        for obstacle_index, obstacle in enumerate(obstacles):
            obstacle_base = f"{base}.spatial_contract.obstacles[{obstacle_index}]"
            if not isinstance(obstacle, dict):
                out.append(finding("error", obstacle_base, "obstacle must be an object"))
                continue
            if not nonempty(obstacle.get("id")):
                out.append(finding("error", f"{obstacle_base}.id", "obstacle id is required"))
            obstacle_zone = obstacle.get("zone")
            if not valid_zone(obstacle_zone):
                out.append(finding("error", f"{obstacle_base}.zone", "use a normalized [left, top, right, bottom] zone"))
                continue
            if obstacle.get("passable") is False:
                for corridor_id, corridor in reserved_contracts.items():
                    corridor_zone = corridor.get("zone")
                    if valid_zone(corridor_zone) and zones_overlap(obstacle_zone, corridor_zone):
                        out.append(
                            finding(
                                "error",
                                obstacle_base,
                                f"non-passable obstacle intersects clear corridor {corridor_id!r}; redesign the shot",
                            )
                        )

        occluders = spatial.get("occluders")
        if not isinstance(occluders, list):
            out.append(
                finding(
                    "error",
                    f"{base}.spatial_contract.occluders",
                    "declare an occluder list, even when the shot has none",
                )
            )
            occluders = []
        for occluder_index, occluder in enumerate(occluders):
            occluder_base = f"{base}.spatial_contract.occluders[{occluder_index}]"
            if not isinstance(occluder, dict):
                out.append(finding("error", occluder_base, "occluder must be an object"))
                continue
            occluder_id = occluder.get("id")
            if not nonempty(occluder_id) or not ID_RE.match(occluder_id):
                out.append(finding("error", f"{occluder_base}.id", "use a non-empty kebab-case occluder id"))
            elif occluder_id in occluder_contracts:
                out.append(finding("error", f"{occluder_base}.id", f"duplicate occluder id {occluder_id!r}"))
            else:
                occluder_contracts[occluder_id] = occluder
            if not valid_zone(occluder.get("zone")):
                out.append(finding("error", f"{occluder_base}.zone", "use a normalized occluder zone"))
            if not nonempty(occluder.get("depth")):
                out.append(finding("error", f"{occluder_base}.depth", "declare foreground/midground depth order"))
            if not isinstance(occluder.get("may_cover_characters"), bool):
                out.append(
                    finding(
                        "error",
                        f"{occluder_base}.may_cover_characters",
                        "declare whether this layer may cover a character",
                    )
                )

        actors = spatial.get("actors")
        if not isinstance(actors, list) or not actors:
            out.append(finding("error", f"{base}.spatial_contract.actors", "add at least one actor placement and action contract"))
            actors = []
        for actor_index, actor in enumerate(actors):
            actor_base = f"{base}.spatial_contract.actors[{actor_index}]"
            if not isinstance(actor, dict):
                out.append(finding("error", actor_base, "actor contract must be an object"))
                continue
            actor_id = actor.get("id")
            if actor_id not in character_ids:
                out.append(finding("error", f"{actor_base}.id", f"unknown character id {actor_id!r}"))
            elif actor_id in actor_contracts:
                out.append(finding("error", f"{actor_base}.id", f"duplicate actor contract for {actor_id!r}"))
            else:
                actor_contracts[actor_id] = actor
            start_zone = actor.get("start_zone")
            end_zone = actor.get("end_zone")
            if not valid_zone(start_zone):
                out.append(finding("error", f"{actor_base}.start_zone", "use a normalized start zone"))
            if not valid_zone(end_zone):
                out.append(finding("error", f"{actor_base}.end_zone", "use a normalized end zone"))

            travel = actor.get("travel")
            if not isinstance(travel, dict):
                out.append(finding("error", f"{actor_base}.travel", "declare direction, facing, locomotion, path, and clearance"))
                travel = {}
            direction = travel.get("direction")
            facing = travel.get("facing")
            if direction not in VALID_DIRECTIONS:
                out.append(finding("error", f"{actor_base}.travel.direction", f"expected one of {sorted(VALID_DIRECTIONS)}"))
            if facing not in VALID_FACINGS:
                out.append(finding("error", f"{actor_base}.travel.facing", f"expected one of {sorted(VALID_FACINGS)}"))

            locomotion = travel.get("locomotion")
            if not nonempty(locomotion):
                out.append(finding("error", f"{actor_base}.travel.locomotion", "locomotion mode is required"))
            backward = locomotion == "backward-walk"
            if backward and not nonempty(travel.get("exception_reason")):
                out.append(finding("error", f"{actor_base}.travel.exception_reason", "explain why the actor visibly travels backward"))

            if valid_zone(start_zone) and valid_zone(end_zone):
                start_x, _ = zone_center(start_zone)
                end_x, _ = zone_center(end_zone)
                if direction == "left-to-right" and end_x <= start_x:
                    out.append(finding("error", f"{actor_base}.travel.direction", "left-to-right requires an end zone right of the start zone"))
                if direction == "right-to-left" and end_x >= start_x:
                    out.append(finding("error", f"{actor_base}.travel.direction", "right-to-left requires an end zone left of the start zone"))
                if direction == "stationary" and abs(end_x - start_x) > 0.02:
                    out.append(finding("error", f"{actor_base}.travel.direction", "stationary actor start/end centers must materially match"))
                expected_facing = {"left-to-right": "right", "right-to-left": "left"}.get(direction)
                if expected_facing and facing != expected_facing and not backward:
                    out.append(
                        finding(
                            "error",
                            f"{actor_base}.travel.facing",
                            f"{direction} forward travel requires facing {expected_facing!r}; regenerate instead of force-fitting",
                        )
                    )

            path_zone_id = travel.get("path_zone")
            corridor = reserved_contracts.get(path_zone_id)
            if not nonempty(path_zone_id) or corridor is None:
                out.append(finding("error", f"{actor_base}.travel.path_zone", "reference a named clear reserved zone"))
            elif valid_zone(corridor.get("zone")):
                if valid_zone(start_zone) and not zone_contains(corridor["zone"], start_zone):
                    out.append(finding("error", f"{actor_base}.start_zone", f"start zone falls outside corridor {path_zone_id!r}"))
                if valid_zone(end_zone) and not zone_contains(corridor["zone"], end_zone):
                    out.append(finding("error", f"{actor_base}.end_zone", f"end zone falls outside corridor {path_zone_id!r}"))

            clearance = travel.get("minimum_clearance_actor_widths")
            if not isinstance(clearance, (int, float)) or isinstance(clearance, bool) or clearance < 1:
                out.append(finding("error", f"{actor_base}.travel.minimum_clearance_actor_widths", "reserve at least one actor width"))

            action = actor.get("action")
            if not isinstance(action, dict):
                out.append(finding("error", f"{actor_base}.action", "declare an observable action and semantic target"))
                continue
            action_type = action.get("type")
            target_id = action.get("target")
            if not nonempty(action_type):
                out.append(finding("error", f"{actor_base}.action.type", "action type is required"))
            if target_id not in target_contracts:
                out.append(finding("error", f"{actor_base}.action.target", f"unknown semantic target {target_id!r}"))
            elif action_type not in target_contracts[target_id].get("supports_actions", []):
                out.append(
                    finding(
                        "error",
                        f"{actor_base}.action.target",
                        f"target {target_id!r} does not support action {action_type!r}",
                    )
                )
            if not nonempty(action.get("contact")):
                out.append(finding("error", f"{actor_base}.action.contact", "declare the visible body/prop contact point"))
            if not nonempty(action.get("proof")):
                out.append(finding("error", f"{actor_base}.action.proof", "declare the muted visual proof"))

        asset_plan = scene.get("asset_plan")
        if not isinstance(asset_plan, dict):
            out.append(finding("error", f"{base}.asset_plan", "add a shot-specific asset plan after spatial approval"))
            asset_plan = {}
        if asset_plan.get("generation_policy") != SHOT_ASSET_POLICY:
            out.append(
                finding(
                    "error",
                    f"{base}.asset_plan.generation_policy",
                    f"set generation policy to {SHOT_ASSET_POLICY!r}",
                )
            )
        if asset_plan.get("space_approved") is not True:
            out.append(
                finding(
                    "error",
                    f"{base}.asset_plan.space_approved",
                    "approve the shot space before listing or generating concrete assets",
                )
            )
        assets = asset_plan.get("assets")
        if not isinstance(assets, list) or not assets:
            out.append(finding("error", f"{base}.asset_plan.assets", "list the minimum assets required by this shot"))
            assets = []
        for asset_index, asset in enumerate(assets):
            asset_base = f"{base}.asset_plan.assets[{asset_index}]"
            if not isinstance(asset, dict):
                out.append(finding("error", asset_base, "asset must be an object"))
                continue
            if not nonempty(asset.get("id")):
                out.append(finding("error", f"{asset_base}.id", "asset id is required"))
            if not nonempty(asset.get("kind")):
                out.append(finding("error", f"{asset_base}.kind", "asset kind is required"))
            if asset.get("status") not in {"planned", "generated", "approved", "rejected"}:
                out.append(finding("error", f"{asset_base}.status", "expected planned, generated, approved, or rejected"))

            if social_route or premium_route:
                dominant = asset.get("dominant")
                if not isinstance(dominant, bool):
                    out.append(finding("error", f"{asset_base}.dominant", "classify whether this asset is visually dominant"))
                if dominant is True:
                    display_fraction = asset.get("intended_max_frame_fraction")
                    if (
                        not isinstance(display_fraction, (int, float))
                        or isinstance(display_fraction, bool)
                        or not 0 < float(display_fraction) <= 1
                    ):
                        out.append(finding("error", f"{asset_base}.intended_max_frame_fraction", "record the intended maximum fraction of the frame from 0 to 1"))
                    if asset.get("status") == "approved":
                        quality = asset.get("quality_review")
                        if not isinstance(quality, dict):
                            out.append(finding("error", f"{asset_base}.quality_review", "approved dominant assets require candidate and composite evidence"))
                        else:
                            candidates = quality.get("candidates_compared")
                            if not isinstance(candidates, int) or isinstance(candidates, bool) or candidates < 2:
                                out.append(finding("error", f"{asset_base}.quality_review.candidates_compared", "compare at least two materially useful candidates"))
                            if not nonempty(quality.get("selected_candidate")):
                                out.append(finding("error", f"{asset_base}.quality_review.selected_candidate", "record the selected candidate id"))
                            rejection_notes = quality.get("rejection_notes")
                            if not isinstance(rejection_notes, list) or not rejection_notes or any(not nonempty(item) for item in rejection_notes):
                                out.append(finding("error", f"{asset_base}.quality_review.rejection_notes", "record concise reasons the alternatives lost"))
                            source_dimensions = quality.get("source_dimensions")
                            if (
                                not isinstance(source_dimensions, list)
                                or len(source_dimensions) != 2
                                or any(not isinstance(item, int) or isinstance(item, bool) or item <= 0 for item in source_dimensions)
                            ):
                                out.append(finding("error", f"{asset_base}.quality_review.source_dimensions", "record positive [width, height] source pixels"))
                            for field in ("art_direction_match", "composite_test", "phone_size_readability", "finish"):
                                if quality.get(field) != "pass":
                                    out.append(finding("error", f"{asset_base}.quality_review.{field}", "expected pass before asset approval"))

            actor_id = asset.get("actor_id")
            if actor_id is not None:
                actor_contract = actor_contracts.get(actor_id)
                if actor_contract is None:
                    out.append(finding("error", f"{asset_base}.actor_id", f"unknown shot actor {actor_id!r}"))
                if asset.get("identity_reference") != actor_id:
                    out.append(
                        finding(
                            "error",
                            f"{asset_base}.identity_reference",
                            "reference the approved character identity ID; never use the frontal image as the asset itself",
                        )
                    )
                if actor_contract:
                    travel = actor_contract.get("travel", {})
                    if asset.get("screen_direction") != travel.get("direction"):
                        out.append(finding("error", f"{asset_base}.screen_direction", "asset direction must match the shot travel contract"))
                    if asset.get("facing") != travel.get("facing"):
                        out.append(finding("error", f"{asset_base}.facing", "asset facing must match the shot travel contract"))

            actor_ids = asset.get("actor_ids")
            if actor_ids is not None:
                if not isinstance(actor_ids, list) or len(actor_ids) < 2 or any(item not in actor_contracts for item in actor_ids):
                    out.append(finding("error", f"{asset_base}.actor_ids", "ensemble assets require at least two known shot actors"))
                identity_references = asset.get("identity_references")
                if not isinstance(identity_references, list) or set(identity_references) != set(actor_ids):
                    out.append(finding("error", f"{asset_base}.identity_references", "reference every ensemble participant identity exactly once"))
                directions = {actor_contracts[item].get("travel", {}).get("direction") for item in actor_ids if item in actor_contracts}
                facings = {actor_contracts[item].get("travel", {}).get("facing") for item in actor_ids if item in actor_contracts}
                if len(directions) != 1 or asset.get("screen_direction") not in directions:
                    out.append(finding("error", f"{asset_base}.screen_direction", "ensemble direction must match all participant contracts"))
                if len(facings) != 1 or asset.get("facing") not in facings:
                    out.append(finding("error", f"{asset_base}.facing", "ensemble facing must match all participant contracts"))

            asset_target = asset.get("target")
            asset_action = asset.get("action")
            if asset_target is not None:
                if asset_target not in target_contracts:
                    out.append(finding("error", f"{asset_base}.target", f"unknown asset target {asset_target!r}"))
                elif asset_action not in target_contracts[asset_target].get("supports_actions", []):
                    out.append(finding("error", f"{asset_base}.target", f"target does not support asset action {asset_action!r}"))

        review_contract = scene.get("review_contract")
        if not isinstance(review_contract, dict):
            out.append(
                finding(
                    "error",
                    f"{base}.review_contract",
                    "protect head/face and declare occlusion review times before animation approval",
                )
            )
            review_contract = {}
        protected_regions = review_contract.get("protected_regions")
        if not isinstance(protected_regions, list):
            out.append(finding("error", f"{base}.review_contract.protected_regions", "expected a list"))
            protected_set: set[str] = set()
        else:
            protected_set = {item for item in protected_regions if isinstance(item, str)}
        missing_regions = sorted(REQUIRED_PROTECTED_REGIONS - protected_set)
        if missing_regions:
            out.append(
                finding(
                    "error",
                    f"{base}.review_contract.protected_regions",
                    f"protect required regions: {', '.join(missing_regions)}",
                )
            )
        if review_contract.get("edge_clipping") != "reject":
            out.append(
                finding(
                    "error",
                    f"{base}.review_contract.edge_clipping",
                    "set reject; frame, crop, overflow, mask, or matte may not slice head or face",
                )
            )
        if review_contract.get("unplanned_occlusion") != "reject":
            out.append(
                finding(
                    "error",
                    f"{base}.review_contract.unplanned_occlusion",
                    "set reject; every head/face occlusion needs a visible declared occluder",
                )
            )

        review_times = review_contract.get("review_times")
        numeric_review_times: list[float] = []
        if not isinstance(review_times, list) or len(review_times) < 3:
            out.append(
                finding(
                    "error",
                    f"{base}.review_contract.review_times",
                    "add at least first, midpoint/pose-change, and final/proof review times",
                )
            )
        else:
            for review_index, review_time in enumerate(review_times):
                if (
                    not isinstance(review_time, (int, float))
                    or isinstance(review_time, bool)
                    or review_time < 0
                    or (duration_value and review_time > duration_value)
                ):
                    out.append(
                        finding(
                            "error",
                            f"{base}.review_contract.review_times[{review_index}]",
                            "review time must fall inside the shot",
                        )
                    )
                else:
                    numeric_review_times.append(float(review_time))
        for event_index, event in enumerate(scene.get("events", [])):
            proof_time = event.get("proof_time") if isinstance(event, dict) else None
            if isinstance(proof_time, (int, float)) and not any(abs(float(proof_time) - value) <= 0.02 for value in numeric_review_times):
                out.append(
                    finding(
                        "error",
                        f"{base}.review_contract.review_times",
                        f"include events[{event_index}].proof_time {float(proof_time):.3f}s",
                    )
                )

        intentional_occlusions = review_contract.get("intentional_occlusions")
        if not isinstance(intentional_occlusions, list):
            out.append(
                finding(
                    "error",
                    f"{base}.review_contract.intentional_occlusions",
                    "declare a list, even when no head/face occlusion is planned",
                )
            )
            intentional_occlusions = []
        declared_occluders: set[str] = set()
        for occlusion_index, occlusion in enumerate(intentional_occlusions):
            occlusion_base = f"{base}.review_contract.intentional_occlusions[{occlusion_index}]"
            if not isinstance(occlusion, dict):
                out.append(finding("error", occlusion_base, "intentional occlusion must be an object"))
                continue
            actor_id = occlusion.get("actor_id")
            occluder_id = occlusion.get("occluder_id")
            if actor_id not in actor_contracts:
                out.append(finding("error", f"{occlusion_base}.actor_id", f"unknown shot actor {actor_id!r}"))
            occluder = occluder_contracts.get(occluder_id)
            if occluder is None:
                out.append(finding("error", f"{occlusion_base}.occluder_id", f"unknown occluder {occluder_id!r}"))
            else:
                declared_occluders.add(occluder_id)
                if occluder.get("may_cover_characters") is not True:
                    out.append(
                        finding(
                            "error",
                            f"{occlusion_base}.occluder_id",
                            f"occluder {occluder_id!r} is not allowed to cover characters",
                        )
                    )
            start = occlusion.get("start")
            end = occlusion.get("end")
            maximum = occlusion.get("maximum_time")
            if not isinstance(start, (int, float)) or isinstance(start, bool) or start < 0:
                out.append(finding("error", f"{occlusion_base}.start", "use a non-negative shot-relative start"))
            if not isinstance(end, (int, float)) or isinstance(end, bool) or end <= 0:
                out.append(finding("error", f"{occlusion_base}.end", "use a positive shot-relative end"))
            if isinstance(start, (int, float)) and isinstance(end, (int, float)):
                if end <= start or (duration_value and end > duration_value):
                    out.append(finding("error", occlusion_base, "occlusion interval must fall inside the shot"))
                if not isinstance(maximum, (int, float)) or not start <= maximum <= end:
                    out.append(finding("error", f"{occlusion_base}.maximum_time", "place maximum coverage inside the interval"))
            if not nonempty(occlusion.get("reason")):
                out.append(finding("error", f"{occlusion_base}.reason", "explain the physical and narrative reason"))
            identity_proof_time = occlusion.get("identity_proof_time")
            if (
                not isinstance(identity_proof_time, (int, float))
                or isinstance(identity_proof_time, bool)
                or identity_proof_time < 0
                or (duration_value and identity_proof_time > duration_value)
            ):
                out.append(
                    finding(
                        "error",
                        f"{occlusion_base}.identity_proof_time",
                        "provide an unobstructed identity-proof time inside the shot",
                    )
                )
            elif isinstance(start, (int, float)) and isinstance(end, (int, float)) and start <= identity_proof_time <= end:
                out.append(
                    finding(
                        "error",
                        f"{occlusion_base}.identity_proof_time",
                        "identity-proof time must be outside the occlusion interval",
                    )
                )
        for occluder_id, occluder in occluder_contracts.items():
            if occluder.get("may_cover_characters") is True and occluder_id not in declared_occluders:
                out.append(
                    finding(
                        "error",
                        f"{base}.spatial_contract.occluders",
                        f"occluder {occluder_id!r} may cover characters but has no intentional-occlusion declaration",
                    )
                )

        layers = scene.get("layers")
        if not isinstance(layers, list) or any(
            not isinstance(layer, str) or not layer.strip() for layer in layers
        ):
            out.append(
                finding(
                    "error",
                    f"{base}.layers",
                    "declare the integrated scene and/or independent layers chosen for this shot; no universal layer count applies",
                )
            )

        events = scene.get("events")
        if not isinstance(events, list) or not events:
            out.append(
                finding(
                    "error",
                    f"{base}.events",
                    "describe at least one action, reaction, condition, reveal, transition, or intentional pause with a proof",
                )
            )
            events = []
        for event_index, event in enumerate(events):
            event_base = f"{base}.events[{event_index}]"
            if not isinstance(event, dict):
                out.append(finding("error", event_base, "event must be an object"))
                continue
            if not nonempty(event.get("proof")):
                out.append(
                    finding(
                        "error",
                        f"{event_base}.proof",
                        "state how the audience will perceive this event or intentional stillness",
                    )
                )
            event_content = (
                event.get("cause"),
                event.get("action"),
                event.get("propagation"),
                event.get("result"),
                event.get("condition"),
                event.get("reaction"),
                event.get("transition"),
                event.get("pause"),
            )
            if not any(nonempty(value) for value in event_content):
                out.append(
                    finding(
                        "error",
                        event_base,
                        "describe the applicable action, reaction, condition, reveal, transition, or pause; do not invent missing causal stages",
                    )
                )
            start = event.get("start")
            end = event.get("end")
            proof_time = event.get("proof_time")
            if start is not None and (not isinstance(start, (int, float)) or start < 0):
                out.append(finding("error", f"{event_base}.start", "start must be a non-negative scene-relative time"))
            if end is not None and (not isinstance(end, (int, float)) or end <= 0):
                out.append(finding("error", f"{event_base}.end", "end must be a positive scene-relative time"))
            if isinstance(start, (int, float)) and isinstance(end, (int, float)) and end <= start:
                out.append(finding("error", event_base, "event end must be after start"))
            if isinstance(end, (int, float)) and duration_value and end > duration_value + 1e-6:
                out.append(finding("error", f"{event_base}.end", "event exceeds scene duration"))
            if proof_time is None:
                out.append(finding("warning", f"{event_base}.proof_time", "add a review timestamp for the observable proof"))
            elif not isinstance(proof_time, (int, float)) or proof_time < 0 or (duration_value and proof_time > duration_value):
                out.append(finding("error", f"{event_base}.proof_time", "proof_time must fall inside the scene"))

        if social_route:
            visual_beats = scene.get("visual_beats")
            if not isinstance(visual_beats, list) or not visual_beats:
                out.append(
                    finding(
                        "error",
                        f"{base}.visual_beats",
                        "declare what new audience information arrives during this social shot",
                    )
                )
                visual_beats = []
            previous_time = -1.0
            for beat_index, beat in enumerate(visual_beats):
                beat_base = f"{base}.visual_beats[{beat_index}]"
                if not isinstance(beat, dict):
                    out.append(finding("error", beat_base, "visual beat must be an object"))
                    continue
                beat_time = beat.get("time")
                if (
                    not isinstance(beat_time, (int, float))
                    or isinstance(beat_time, bool)
                    or beat_time < 0
                    or (duration_value and beat_time > duration_value)
                ):
                    out.append(finding("error", f"{beat_base}.time", "use a scene-relative timestamp inside the shot"))
                elif float(beat_time) < previous_time:
                    out.append(finding("error", f"{beat_base}.time", "list visual beats in chronological order"))
                else:
                    previous_time = float(beat_time)
                if not nonempty(beat.get("change")):
                    out.append(finding("error", f"{beat_base}.change", "state the visible or audible change the audience receives"))
                if not nonempty(beat.get("function")):
                    out.append(finding("error", f"{beat_base}.function", "state the editorial function of this beat"))
            if index == 0 and visual_beats:
                first_time = visual_beats[0].get("time") if isinstance(visual_beats[0], dict) else None
                if not isinstance(first_time, (int, float)) or float(first_time) > 0.1:
                    out.append(finding("error", f"{base}.visual_beats[0].time", "the feed-native first frame must already carry the opening event"))
                proof_limit = data.get("social_contract", {}).get("opening", {}).get("visual_proof_by", 3.0)
                promise_proofs = [
                    beat.get("time")
                    for beat in visual_beats
                    if isinstance(beat, dict) and beat.get("function") == "promise-proof"
                ]
                if not any(isinstance(time, (int, float)) and float(time) <= float(proof_limit) for time in promise_proofs):
                    out.append(
                        finding(
                            "error",
                            f"{base}.visual_beats",
                            "add a promise-proof beat no later than social_contract.opening.visual_proof_by",
                        )
                    )

        for ensemble_index, ensemble in enumerate(scene.get("ensemble_actions", [])):
            ens_base = f"{base}.ensemble_actions[{ensemble_index}]"
            if not isinstance(ensemble, dict):
                out.append(finding("error", ens_base, "ensemble action must be an object"))
                continue
            participants = ensemble.get("participants")
            if not isinstance(participants, list) or len(participants) < 2:
                out.append(finding("error", f"{ens_base}.participants", "connected ensemble actions require at least two participants"))
            else:
                for participant in participants:
                    if participant not in character_ids:
                        out.append(finding("error", f"{ens_base}.participants", f"unknown character id {participant!r}"))
            if ensemble.get("ensemble_required") is not True:
                out.append(finding("warning", f"{ens_base}.ensemble_required", "set true when actors share contact or load"))
            if not nonempty(ensemble.get("proof")):
                out.append(finding("error", f"{ens_base}.proof", "describe visible contact/load proof"))

    target = data.get("target_duration")
    if isinstance(target, (int, float)) and scenes and abs(total_duration - float(target)) > 0.05:
        out.append(finding("warning", "target_duration", f"scene durations total {total_duration:.3f}s, not {float(target):.3f}s"))

    delivery = data.get("delivery")
    if not isinstance(delivery, dict):
        out.append(finding("warning", "delivery", "declare master/social delivery requirements"))
    elif delivery.get("social_1080p") and float(delivery.get("social_vmaf_floor", 95)) < 93:
        out.append(finding("warning", "delivery.social_vmaf_floor", "use 95 or higher for a near-transparent social encode"))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument(
        "--phase",
        choices=sorted(VALID_PHASES),
        default="production",
        help="editorial allows pending animatics; production/release require approved social gates",
    )
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read manifest: {exc}", file=sys.stderr)
        raise SystemExit(2)

    findings = validate_manifest(
        data,
        args.project_dir.resolve() if args.project_dir else None,
        phase=args.phase,
    )
    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    payload = {"ok": errors == 0 and (warnings == 0 or not args.strict), "errors": errors, "warnings": warnings, "findings": findings}
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"[{item['severity'].upper()}] {item['path']}: {item['message']}")
        print(f"Manifest validation: {errors} error(s), {warnings} warning(s)")
    raise SystemExit(1 if errors or (args.strict and warnings) else 0)


if __name__ == "__main__":
    main()
