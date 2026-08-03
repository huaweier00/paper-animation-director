#!/usr/bin/env python3
"""Initialize a paper-animation HyperFrames project from a story manifest."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from validate_story_manifest import validate_manifest


PORTABLE_PIPELINE_SCRIPTS = (
    "audit_motion_contract.py",
    "audit_rendered_motion.py",
    "audit_blender_action_library.py",
    "audit_engine_inputs.py",
    "audit_rive_rig.py",
    "audit_shot_release.py",
    "audit_three_scene.py",
    "blender_action_library.py",
    "bind_release_evidence.py",
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
    args = parser.parse_args()

    manifest = args.manifest.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {output}")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    errors = [item for item in validate_manifest(data) if item["severity"] == "error"]
    if errors:
        details = "\n".join(f"{item['path']}: {item['message']}" for item in errors)
        raise SystemExit(f"Manifest has blocking errors:\n{details}")

    skill_root = Path(__file__).resolve().parent.parent
    template = skill_root / "assets" / "project-template"
    output.mkdir(parents=True, exist_ok=True)
    for source in template.iterdir():
        if source.name in {"manifests", "runtime"}:
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
    width, height = ASPECT_SIZES.get(data.get("aspect", "16:9"), (1920, 1080))
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

    build_script = Path(__file__).with_name("build_hyperframes_timeline.py")
    subprocess.run(
        [sys.executable, str(build_script), "--manifest", str(output / "story-manifest.json"), "--project", str(output)],
        check=True,
    )
    print(f"Initialized {output}")
    print(
        "Next: approve identities and the hardest shot's spatial/animation decisions, "
        "then route shot-capabilities.json into engine-plan.json before generating engine-shaped assets."
    )


if __name__ == "__main__":
    main()
