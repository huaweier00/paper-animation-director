#!/usr/bin/env python3
"""Initialize a creative paper-animation project; opt into production gates explicitly."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from validate_story_manifest import validate_manifest
from build_hyperframes_timeline import validate_creative_manifest


PORTABLE_PIPELINE_SCRIPTS = (
    "audit_audio_mode.py",
    "audit_medium_contract.py",
    "audit_motion_contract.py",
    "audit_performance_contract.py",
    "audit_pose_reuse.py",
    "audit_release_index.py",
    "audit_rendered_motion.py",
    "audit_blender_action_library.py",
    "audit_engine_inputs.py",
    "audit_rive_rig.py",
    "audit_shot_release.py",
    "audit_three_scene.py",
    "blender_action_library.py",
    "bind_release_evidence.py",
    "bind_release_index.py",
    "build_blender_paper_impact.py",
    "build_motion_review.py",
    "build_routed_shot.py",
    "compile_motion_contract.py",
    "doctor_paper_pipeline.py",
    "inspect_rive_asset.mjs",
    "profile_multi_engine.mjs",
    "probe_webgpu_runtime.mjs",
    "render_blender_prerender.py",
    "review_animation_decision.py",
    "route_shot_capabilities.py",
    "scaffold_hybrid_shot.py",
    "verify_deterministic_seek.py",
    "validate_story_manifest.py",
)

ASPECT_SIZES = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
}

MEDIUM_ROUTES = {"shadow-theatre", "cutout-paper", "painterly-limited"}

PRODUCTION_SCRIPTS = {
    "doctor": "python3 tools/paper-pipeline/doctor_paper_pipeline.py --project . --phase render",
    "shot:build": "python3 tools/paper-pipeline/build_routed_shot.py --project .",
    "shot:profile": "node tools/paper-pipeline/profile_multi_engine.mjs --project .",
    "webgpu:probe": "node tools/paper-pipeline/probe_webgpu_runtime.mjs --project . --required-backend any",
}

PRODUCTION_DEPENDENCIES = {
    "@rive-app/canvas-advanced-single": "2.39.1",
    "pixi.js": "8.19.0",
    "three": "0.185.1",
}


def build_medium_contract(data: dict) -> dict:
    route = data.get("medium_route", "painterly-limited")
    if route not in MEDIUM_ROUTES:
        raise ValueError(f"medium_route must be one of {sorted(MEDIUM_ROUTES)}")
    scenes = [item for item in data.get("scenes", []) if isinstance(item, dict)]
    benchmark_id = data.get("performance_benchmark_shot") or (scenes[0].get("id") if scenes else "benchmark-shot")
    modes = {
        "shadow-theatre": ["articulated-rig", "pose-replacement", "connected-ensemble", "full-scene-state", "deliberate-still"],
        "cutout-paper": ["articulated-rig", "pose-replacement", "connected-ensemble", "full-scene-state", "deliberate-still"],
        "painterly-limited": ["pose-replacement", "articulated-rig", "full-scene-state", "selective-local-motion", "deliberate-still"],
    }[route]
    truth = {
        "shadow-theatre": {
            "material": "translucent carved leather-like performer with authored openwork and transmitted color",
            "performer": "articulated screen-plane puppet with declared central and local controls",
            "space": "rear-lit translucent screen with entry, exit, support, overlap, and occlusion rules",
            "light": "rear light whose distance changes edge softness, scale, and color transmission",
            "sound": "voice or singing, percussion, music, effects, ambience, and silence cue manipulation",
        },
        "cutout-paper": {
            "material": "opaque cut paper with authored edge, thickness, fold, hinge, and contact behavior",
            "performer": "constructed cutout performer using joints, replacement poses, or connected ensembles",
            "space": "layered paper stage with declared support, overlap, occlusion, and depth ordering",
            "light": "directional stage light reveals paper thickness and contact without fake shadow physics",
            "sound": "voice, foley, music, effects, ambience, and silence support each action phrase",
        },
        "painterly-limited": {
            "material": "painted image states with authored brush, edge, wash, and compositing behavior",
            "performer": "pose states, selective local controls, or full-scene states preserve painterly integrity",
            "space": "painted depth planes with declared support, overlap, atmosphere, and focal hierarchy",
            "light": "painted light logic remains coherent across state changes and compositing",
            "sound": "voice, music, effects, ambience, and silence carry rhythm without replacing visible acting",
        },
    }[route]
    contract = {
        "schema_version": 1,
        "project_id": data["project"],
        "route": route,
        "status": "draft",
        "medium_truth": truth,
        "performance_policy": {
            "actor_internal_change_required": True,
            "allowed_modes": modes,
            "presentation_only_not_action_proof": True,
            "earned_stillness_required": True,
            "pose_reuse_requires_compatible_intent": True,
        },
        "forbidden_shortcuts": [
            "root-transform-as-hero-acting",
            "camera-motion-as-action-proof",
            "surface-texture-as-material-proof",
            "same-pose-across-incompatible-intentions",
        ],
        "benchmark": {
            "shot_id": benchmark_id,
            "rendered_mp4": "",
            "status": "planned",
            "proves": [
                "intention-to-result performance phrase",
                "affected-character or environment reaction",
                "static-camera readability without presentation motion",
            ],
        },
        "approval": {"reviewer": "", "notes": ""},
    }
    if route == "shadow-theatre":
        contract["forbidden_shortcuts"].extend(
            ["opaque-full-body-png-as-shadow-puppet", "silent-shadow-theatre-master"]
        )
        contract["shadow_theatre"] = {
            "screen": {
                "type": "rear-lit-translucent",
                "transmitted_light": True,
                "screen_plane_required": True,
                "performer_distance_affects_projection": True,
            },
            "articulation": {
                "required": True,
                "puppet_model_required": True,
                "control_logic": "central-control-plus-local-hand-or-prop-controls",
            },
            "audio": {
                "allowed_modes": ["full-performance", "dialogue-and-sound-design"],
                "silent_allowed": False,
                "music_only_allowed": False,
            },
        }
    elif route == "cutout-paper":
        contract["cutout_paper"] = {
            "construction": "separate authored pieces, joints, replacement states, and complete object silhouettes",
            "material_behavior": "edge, thickness, fold, hinge, contact, and stepped deformation remain visible",
            "depth_model": "declared paper layers, support planes, occlusion order, and contact shadows",
            "performer_model_required": True,
        }
    else:
        contract["painterly_limited"] = {
            "paint_system": "authored painterly states with consistent line, wash, texture scale, and edge hierarchy",
            "integration_model": "performers and environments share value, light, atmosphere, and contact logic",
            "state_change_model": "pose replacement, local motion, or full-scene states carry observable change",
            "claims_shadow_physics": False,
        }
    return contract


def build_audio_contract(data: dict, route: str) -> dict:
    requested = data.get("audio_performance_mode")
    mode = requested or ("full-performance" if route == "shadow-theatre" else "dialogue-and-sound-design")
    return {
        "schema_version": 1,
        "project_id": data["project"],
        "medium_route": route,
        "mode": mode,
        "status": "draft",
        "expected_spoken_or_sung_lines": max(1, len(data.get("scenes", []))),
        "cue_ledger": "audio/cue-ledger.json",
        "dry_stems": [],
        "music_and_effect_stems": [],
        "expected_in_master": ["dialogue-or-singing", "music", "effects", "ambience"],
        "intentional_silence_rationale": "",
        "approval": {"reviewer": "", "notes": ""},
    }


def build_performance_contract(scene: dict, route: str) -> dict:
    shot_id = scene["id"]
    duration = float(scene["duration"])
    spatial = scene.get("spatial_contract", {})
    actors = []
    for actor in spatial.get("actors", []) if isinstance(spatial, dict) else []:
        if not isinstance(actor, dict) or not isinstance(actor.get("id"), str):
            continue
        actor_id = actor["id"]
        action = actor.get("action", {}) if isinstance(actor.get("action"), dict) else {}
        start = round(duration * 0.12, 3)
        action_time = round(duration * 0.46, 3)
        result = round(duration * 0.76, 3)
        actors.append(
            {
                "actor_id": actor_id,
                "objective": f"perform {action.get('type', 'the declared action')} on {action.get('target', 'the declared target')}",
                "initial_attention": action.get("target", "declared-target"),
                "final_attention": action.get("target", "declared-target"),
                "performance_mode": "pose-replacement",
                "lead_control": "author-before-production",
                "support": actor.get("support_surface", "declared-support-surface"),
                "production_asset": {
                    "asset_id": f"{actor_id}-{shot_id}-performance",
                    "status": "planned",
                    "sha256": "",
                    "performance_state": "planned-shot-specific-state",
                    "reuse_authorization": {"approved": False, "reason": "shot-specific by default"},
                },
                "phases": [
                    {"name": "preparation", "time": start, "visible_change": "body prepares before the declared action", "channel": "complete-pose-replacement"},
                    {"name": "primary-action", "time": action_time, "visible_change": "lead body part completes the declared action", "channel": "complete-pose-replacement"},
                    {"name": "result", "time": result, "visible_change": "body and attention register the result", "channel": "complete-pose-replacement"},
                ],
            }
        )
    motion_required = bool(actors)
    sound_cues = []
    if route == "shadow-theatre" and motion_required:
        sound_cues = [
            {
                "id": f"cue-{actor['actor_id']}-action",
                "time": actor["phases"][1]["time"],
                "type": "author-before-production",
                "binds_to": f"{actor['actor_id']}.primary-action",
            }
            for actor in actors
        ]
    return {
        "schema_version": 1,
        "shot_id": shot_id,
        "medium_route": route,
        "responsibility": scene.get("responsibility", "Author the shot's causal action and visible result."),
        "motion_required": motion_required,
        "presentation_motion_is_not_proof": True,
        "actors": actors,
        "sound_cues": sound_cues,
        "earned_stillness": None if motion_required else {
            "prior_cause": "Declare the event that earns the hold.",
            "present_read": "Declare what remains readable in the held frame.",
            "tension_support": "Declare composition, sound, or duration support.",
            "why_motion_weakens": "Declare why added motion would weaken the beat.",
            "exit_condition": "Declare what ends the hold.",
        },
        "rendered_review": {
            "status": "pending",
            "video": f"renders/{shot_id}.mp4",
            "video_sha256": "",
            "observed_performance": [],
            "reviewer": "",
            "notes": "",
        },
    }


def zone_center(zone: object) -> list[float]:
    if (
        isinstance(zone, list)
        and len(zone) == 4
        and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in zone)
    ):
        return [round((float(zone[0]) + float(zone[2])) / 2, 6), round((float(zone[1]) + float(zone[3])) / 2, 6)]
    return [0.5, 0.8]


def build_motion_contract(scene: dict, width: int, height: int) -> dict:
    shot_id = scene["id"]
    duration = float(scene["duration"])
    spatial = scene.get("spatial_contract", {})
    actors = []
    for actor in spatial.get("actors", []) if isinstance(spatial, dict) else []:
        if not isinstance(actor, dict) or not isinstance(actor.get("id"), str):
            continue
        actor_id = actor["id"]
        travel = actor.get("travel", {}) if isinstance(actor.get("travel"), dict) else {}
        direction = travel.get("direction")
        facing = travel.get("facing", "front")
        stationary = direction == "stationary"
        action = actor.get("action", {}) if isinstance(actor.get("action"), dict) else {}
        contact_required = bool(action.get("contact")) and not stationary
        active_start = round(duration * 0.08, 3)
        active_end = round(duration * 0.72, 3)
        if active_end <= active_start:
            active_end = round(duration * 0.9, 3)
        proof_times = {
            "entry": active_start,
            "midpoint": round((active_start + active_end) / 2, 3),
            "exit": active_end,
        }
        if not stationary:
            proof_times.update(
                {
                    "early": round(active_start + (active_end - active_start) * 0.25, 3),
                    "late": round(active_start + (active_end - active_start) * 0.75, 3),
                }
            )
        if contact_required:
            contact_time = round(active_start + (active_end - active_start) * 0.88, 3)
            proof_times["contact"] = contact_time
            proof_times["settle"] = min(round(duration * 0.9, 3), round(contact_time + max(0.12, duration * 0.04), 3))
        actors.append(
            {
                "actor_id": actor_id,
                "expected_facing": facing,
                "asset_status": "planned",
                "asset_facts": f"shots/{shot_id}/asset-facts/{actor_id}.json",
                "implementation": {
                    "engine": "pending-route",
                    "selector": f"#{shot_id}-{actor_id}",
                    "source": f"compositions/{shot_id}.html",
                },
                "active": [active_start, active_end],
                "start": zone_center(actor.get("start_zone")),
                "end": zone_center(actor.get("end_zone")),
                "locomotion": "stationary" if stationary else "forward-travel",
                "exception_reason": "",
                "instance_transform": {"scale_x": 1, "rotation_degrees": 0},
                "mirror": {"applied": False, "policy": "forbidden"},
                "support": {
                    "mode": "grounded",
                    "surface": actor.get("support_surface", "declare-support-surface"),
                    "baseline": spatial.get("camera", {}).get("floor_line", 0.82) if isinstance(spatial.get("camera"), dict) else 0.82,
                },
                "contact": {
                    "required": contact_required,
                    "target": action.get("target", "") if contact_required else "",
                    "time": proof_times.get("contact"),
                },
                "proof_times": proof_times,
            }
        )
    return {
        "schema_version": 1,
        "shot_id": shot_id,
        "duration": duration,
        "frame": {"width": width, "height": height},
        "actors": actors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--production",
        action="store_true",
        help="Install advanced contracts, engine adapters, release tools, and production dependencies.",
    )
    args = parser.parse_args()

    manifest = args.manifest.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {output}")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    errors = [item for item in validate_manifest(data) if item["severity"] == "error"] if args.production else []
    creative_errors = validate_creative_manifest(data) if not args.production else []
    if errors:
        details = "\n".join(f"{item['path']}: {item['message']}" for item in errors)
        raise SystemExit(f"Manifest has blocking errors:\n{details}")
    if creative_errors:
        raise SystemExit("Manifest has blocking errors:\n" + "\n".join(creative_errors))

    skill_root = Path(__file__).resolve().parent.parent
    template = skill_root / "assets" / "project-template"
    output.mkdir(parents=True, exist_ok=True)
    production_only = {"manifests", "runtime"}
    if not args.production:
        production_only.update({
            "README-flow.svg",
            "hybrid-pipeline.json",
            "offline-dependency-policy.json",
            "package-lock.json",
        })
    for source in template.iterdir():
        if source.name in production_only:
            continue
        target = output / source.name
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)

    package_path = output / "package.json"
    package_path.write_text(package_path.read_text(encoding="utf-8").replace("__PROJECT_ID__", data["project"]), encoding="utf-8")
    lock_path = output / "package-lock.json"
    if lock_path.is_file():
        lock_path.write_text(
            lock_path.read_text(encoding="utf-8").replace("__PROJECT_ID__", data["project"]),
            encoding="utf-8",
        )
    (output / "compositions" / "scene-template.html").unlink(missing_ok=True)
    (output / "compositions" / "hybrid-scene-template.html").unlink(missing_ok=True)
    shutil.copy2(manifest, output / "story-manifest.json")

    width, height = ASPECT_SIZES.get(data.get("aspect", "16:9"), (1920, 1080))
    build_script = Path(__file__).with_name("build_hyperframes_timeline.py")

    if not args.production:
        lock_path.unlink(missing_ok=True)
        for relative in (
            "assets/references/characters",
            "assets/source-atlases",
            "assets/characters",
            "assets/backgrounds",
            "assets/props",
            "assets/effects",
            "assets/audio",
            "shots",
            "snapshots",
            "renders",
        ):
            (output / relative).mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(build_script), "--manifest", str(output / "story-manifest.json"), "--project", str(output), "--creative"],
            check=True,
        )
        print(f"Initialized creative project {output}")
        print(
            "Next: make three distinct look studies, build a timed scratch animatic, "
            "and prove the hardest 8–15 seconds before adding production gates."
        )
        print(
            "When the benchmark is approved, rerun with --production into a new directory "
            "or add only the production tools required by the chosen implementation."
        )
        return

    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["scripts"].update(PRODUCTION_SCRIPTS)
    package["dependencies"].update(PRODUCTION_DEPENDENCIES)
    package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    medium_contract = build_medium_contract(data)
    (output / "medium-contract.json").write_text(
        json.dumps(medium_contract, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "audio-contract.json").write_text(
        json.dumps(build_audio_contract(data, medium_contract["route"]), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for relative in (
        "assets/references/characters",
        "assets/source-atlases",
        "assets/characters",
        "assets/backgrounds",
        "assets/props",
        "assets/effects",
        "assets/runtime",
        "assets/audio",
        "engine-plans",
        "shots",
        "snapshots",
        "renders",
    ):
        (output / relative).mkdir(parents=True, exist_ok=True)
    for scene in data.get("scenes", []):
        if not isinstance(scene, dict) or not isinstance(scene.get("id"), str):
            continue
        shot_root = output / "shots" / scene["id"]
        shot_root.mkdir(parents=True, exist_ok=True)
        spatial_sidecar = {
            "schema_version": 1,
            "shot_id": scene["id"],
            "spatial_contract": scene.get("spatial_contract", {}),
            "asset_plan": scene.get("asset_plan", {}),
            "review_contract": scene.get("review_contract", {}),
        }
        (shot_root / "spatial-contract.json").write_text(
            json.dumps(spatial_sidecar, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (shot_root / "performance-contract.json").write_text(
            json.dumps(
                build_performance_contract(scene, medium_contract["route"]),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        motion = build_motion_contract(scene, width, height)
        if motion["actors"]:
            (shot_root / "motion-contract.json").write_text(
                json.dumps(motion, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (shot_root / "asset-facts").mkdir(exist_ok=True)
            (shot_root / "review" / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        template / "runtime",
        output / "assets" / "runtime",
        dirs_exist_ok=True,
    )
    portable_tools = output / "tools" / "paper-pipeline"
    portable_tools.mkdir(parents=True, exist_ok=True)
    scripts_root = Path(__file__).resolve().parent
    for script_name in PORTABLE_PIPELINE_SCRIPTS:
        source = scripts_root / script_name
        if not source.is_file():
            raise SystemExit(f"Skill installation is incomplete; missing pipeline script: {source}")
        shutil.copy2(source, portable_tools / script_name)
    portable_template = portable_tools.parent / "assets" / "project-template"
    shutil.copytree(
        template / "compositions",
        portable_template / "compositions",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        template / "runtime",
        portable_template / "runtime",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        template / "manifests",
        portable_template / "manifests",
        dirs_exist_ok=True,
    )
    shutil.copy2(template / "hybrid-pipeline.json", portable_template / "hybrid-pipeline.json")

    subprocess.run(
        [sys.executable, str(build_script), "--manifest", str(output / "story-manifest.json"), "--project", str(output)],
        check=True,
    )
    print(f"Initialized production project {output}")
    print(
        "Next: approve identities and the hardest shot's spatial/animation decisions, "
        "then route shot-capabilities.json into engine-plan.json before generating engine-shaped assets."
    )


if __name__ == "__main__":
    main()
