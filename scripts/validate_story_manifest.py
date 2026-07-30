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
SHOT_ASSET_POLICY = "shot-just-in-time"
REQUIRED_PROTECTED_REGIONS = {"head", "face", "hands", "feet", "action-contact"}


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


def validate_manifest(data: Any, project_dir: Path | None = None) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [finding("error", "$", "manifest root must be a JSON object")]

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
        if not isinstance(layers, list) or len(layers) < 4:
            out.append(finding("warning", f"{base}.layers", "declare useful depth and physical layers; four is the minimum baseline"))

        events = scene.get("events")
        if not isinstance(events, list) or not events:
            out.append(finding("error", f"{base}.events", "add at least one cause/action/result/proof event"))
            events = []
        for event_index, event in enumerate(events):
            event_base = f"{base}.events[{event_index}]"
            if not isinstance(event, dict):
                out.append(finding("error", event_base, "event must be an object"))
                continue
            for key in ("cause", "action", "result", "proof"):
                if not nonempty(event.get(key)):
                    out.append(finding("error", f"{event_base}.{key}", f"{key} is required"))
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
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read manifest: {exc}", file=sys.stderr)
        raise SystemExit(2)

    findings = validate_manifest(data, args.project_dir.resolve() if args.project_dir else None)
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
