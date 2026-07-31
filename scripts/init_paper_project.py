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
    "audit_blender_action_library.py",
    "audit_engine_inputs.py",
    "audit_rive_rig.py",
    "audit_shot_release.py",
    "audit_three_scene.py",
    "blender_action_library.py",
    "build_blender_paper_impact.py",
    "build_routed_shot.py",
    "doctor_paper_pipeline.py",
    "inspect_rive_asset.mjs",
    "profile_multi_engine.mjs",
    "probe_webgpu_runtime.mjs",
    "render_blender_prerender.py",
    "review_animation_decision.py",
    "route_shot_capabilities.py",
    "scaffold_hybrid_shot.py",
    "verify_deterministic_seek.py",
)


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
