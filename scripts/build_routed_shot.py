#!/usr/bin/env python3
"""Run the guarded prepare, verify, or release pipeline for one routed shot."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any


SCRIPT_ROOT = Path(__file__).resolve().parent


class StepFailure(RuntimeError):
    def __init__(self, step: str, command: list[str], result: subprocess.CompletedProcess[str]):
        self.step = step
        self.command = command
        self.result = result
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        super().__init__(f"{step} failed: {detail}")


def run_step(
    name: str,
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    record = {
        "name": name,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "ok": result.returncode == 0,
    }
    if result.returncode != 0:
        raise StepFailure(name, command, result)
    return record


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {path}")
    return path


def load_json(path: Path, label: str) -> dict[str, Any]:
    require_file(path, label)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} root must be an object")
    return data


def shot_duration(project: Path, shot_id: str, explicit: float | None) -> float:
    if explicit is not None:
        if explicit <= 0:
            raise ValueError("--duration must be positive")
        return explicit
    manifest = load_json(project / "story-manifest.json", "story manifest")
    for scene in manifest.get("scenes", []):
        if isinstance(scene, dict) and scene.get("id") == shot_id:
            duration = scene.get("duration")
            if isinstance(duration, (int, float)) and not isinstance(duration, bool) and duration > 0:
                return float(duration)
    raise ValueError(f"shot {shot_id!r} has no positive duration in story-manifest.json")


def previous_shot_ids(project: Path, shot_id: str) -> list[str]:
    manifest = load_json(project / "story-manifest.json", "story manifest")
    ordered = [
        item.get("id")
        for item in manifest.get("scenes", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    if shot_id not in ordered:
        raise ValueError(f"shot {shot_id!r} does not exist in story-manifest.json")
    return ordered[: ordered.index(shot_id)]


def require_current_spatial_sidecar(project: Path, shot_id: str, sidecar: Path) -> None:
    manifest = load_json(project / "story-manifest.json", "story manifest")
    scene = next(
        (item for item in manifest.get("scenes", []) if isinstance(item, dict) and item.get("id") == shot_id),
        None,
    )
    if scene is None:
        raise ValueError(f"shot {shot_id!r} does not exist in story-manifest.json")
    spatial = load_json(sidecar, "spatial contract sidecar")
    if spatial.get("shot_id") != shot_id:
        raise ValueError("spatial-contract.json shot_id does not match the requested shot")
    for field in ("spatial_contract", "asset_plan", "review_contract"):
        if spatial.get(field) != scene.get(field):
            raise ValueError(
                f"spatial-contract.json {field} has drifted from story-manifest.json; "
                "update and re-approve the shot sidecar"
            )


def needs_motion_contract(capabilities: dict[str, Any]) -> bool:
    requirements = capabilities.get("requirements")
    if not isinstance(requirements, dict):
        return True
    return any(
        (
            requirements.get("character_motion") != "none",
            requirements.get("contact") != "none",
            requirements.get("simulation") != "none",
        )
    )


def default_review_times(project: Path, shot_id: str, duration: float) -> list[float]:
    spatial_path = project / "shots" / shot_id / "spatial-contract.json"
    if spatial_path.is_file():
        spatial = load_json(spatial_path, "spatial contract")
        review_times = spatial.get("review_contract", {}).get("review_times")
        if (
            isinstance(review_times, list)
            and len(review_times) >= 2
            and all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and 0 <= float(value) <= duration
                for value in review_times
            )
        ):
            return [float(value) for value in review_times]
    return [0.0, round(duration * 0.25, 3), round(duration * 0.5, 3), round(duration * 0.75, 3), round(max(0, duration - 0.2), 3)]


def parse_review_times(value: str | None, defaults: list[float], duration: float) -> list[float]:
    values = defaults if value is None else [float(item.strip()) for item in value.split(",") if item.strip()]
    if len(values) < 2:
        raise ValueError("at least two review times are required")
    if len(set(values)) != len(values):
        raise ValueError("review times must be unique")
    if any(item < 0 or item > duration for item in values):
        raise ValueError(f"review times must stay inside 0…{duration:g}s")
    return values


def format_times(times: list[float]) -> str:
    out: list[str] = []
    for value in times:
        decimal = Decimal(str(value)).normalize()
        rendered = format(decimal, "f").rstrip("0").rstrip(".") if "." in format(decimal, "f") else format(decimal, "f")
        out.append(rendered or "0")
    return ",".join(out)


def caption_zone(project: Path, shot_id: str) -> str | None:
    spatial_path = project / "shots" / shot_id / "spatial-contract.json"
    if not spatial_path.is_file():
        return None
    spatial = load_json(spatial_path, "spatial contract")
    zones = spatial.get("spatial_contract", {}).get("reserved_zones", [])
    for zone in zones if isinstance(zones, list) else []:
        if not isinstance(zone, dict) or "subtitle" not in str(zone.get("id", "")).lower():
            continue
        geometry = zone.get("zone")
        if (
            isinstance(geometry, list)
            and len(geometry) == 4
            and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in geometry)
        ):
            _, y0, _, _ = geometry
            # HyperFrames' caption audit requires a sufficiently tall bottom
            # band. Preserve a stricter project contract, but never shrink the
            # audit band below the CLI's supported 14% reference band.
            y0 = min(float(y0), 0.86)
            def zone_number(value: float) -> str:
                rendered = f"{float(value):.6f}".rstrip("0").rstrip(".")
                if rendered.startswith("0."):
                    return rendered[1:]
                if rendered.startswith("-0."):
                    return "-" + rendered[2:]
                return rendered

            return (
                f"x0=0;y0={zone_number(y0)};x1=1;y1=1;"
                "severity=error;seek=.18,.45,.7,.95"
            )
    return None


def resolve_hyperframes(project: Path, explicit: str | None) -> Path:
    path = (
        Path(explicit).expanduser().absolute()
        if explicit
        else project / "node_modules" / ".bin" / "hyperframes"
    )
    if not path.is_file():
        raise ValueError(
            f"pinned local HyperFrames binary not found: {path}. "
            "Run npm ci from package-lock.json or pass --hyperframes to an already installed pinned binary."
        )
    return path


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def project_path(project: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty local project path")
    if value.startswith(("http://", "https://", "//", "data:")):
        raise ValueError(f"{label} must not use a runtime-network URL")
    candidate = (project / value.removeprefix("./")).resolve()
    try:
        candidate.relative_to(project)
    except ValueError as exc:
        raise ValueError(f"{label} escapes the project root: {value}") from exc
    return candidate


def append_p2_contract_audits(
    steps: list[dict[str, Any]],
    *,
    project: Path,
    inputs: dict[str, Any],
    phase: str,
) -> None:
    """Run engine-specific P2 sidecar audits for schema-version 2 inputs."""
    if inputs.get("schema_version") != 2:
        return
    engines = inputs.get("engines")
    if not isinstance(engines, dict):
        return

    rive = engines.get("rive")
    if isinstance(rive, dict) and rive.get("ready") is True:
        manifest = project_path(project, rive.get("rig_manifest"), "engines.rive.rig_manifest")
        steps.append(
            run_step(
                f"audit-rive-rig-{phase}",
                [
                    sys.executable,
                    str(SCRIPT_ROOT / "audit_rive_rig.py"),
                    str(manifest),
                    "--project",
                    str(project),
                    "--phase",
                    phase,
                    "--json",
                ],
                cwd=project,
            )
        )

    three = engines.get("three-webgpu")
    if isinstance(three, dict) and three.get("ready") is True:
        manifest = project_path(
            project,
            three.get("scene_manifest"),
            "engines.three-webgpu.scene_manifest",
        )
        steps.append(
            run_step(
                f"audit-three-scene-{phase}",
                [
                    sys.executable,
                    str(SCRIPT_ROOT / "audit_three_scene.py"),
                    str(manifest),
                    "--project",
                    str(project),
                    "--phase",
                    phase,
                    "--json",
                ],
                cwd=project,
            )
        )

    blender = engines.get("blender")
    if isinstance(blender, dict) and blender.get("ready") is True:
        manifest = project_path(
            project,
            blender.get("action_library"),
            "engines.blender.action_library",
        )
        steps.append(
            run_step(
                f"audit-blender-action-library-{phase}",
                [
                    sys.executable,
                    str(SCRIPT_ROOT / "audit_blender_action_library.py"),
                    str(manifest),
                    "--json",
                ],
                cwd=project,
            )
        )


def append_webgpu_probe(
    steps: list[dict[str, Any]],
    *,
    project: Path,
    shot_root: Path,
    inputs: dict[str, Any],
) -> None:
    if inputs.get("schema_version") != 2:
        return
    three = inputs.get("engines", {}).get("three-webgpu")
    if not isinstance(three, dict) or three.get("ready") is not True:
        return
    capability_path = shot_root / "webgpu-capability.json"
    capability = load_json(capability_path, "WebGPU capability policy")
    if capability.get("schema_version") != 1:
        raise ValueError("WebGPU capability policy schema_version must be 1")
    policy = capability.get("release_policy")
    if not isinstance(policy, dict):
        raise ValueError("WebGPU capability policy release_policy must be an object")
    if policy.get("probe_report_required_when_three_selected") is not True:
        raise ValueError(
            "WebGPU capability policy must require a probe report when Three.js is selected"
        )
    required_backend = "webgpu" if policy.get("webgpu_required") is True else "any"
    steps.append(
        run_step(
            "probe-webgpu-runtime",
            [
                "node",
                str(SCRIPT_ROOT / "probe_webgpu_runtime.mjs"),
                "--project",
                str(project),
                "--required-backend",
                required_backend,
                "--capability",
                str(capability_path),
                "--output",
                str(shot_root / "review" / "webgpu-capability-report.json"),
            ],
            cwd=project,
        )
    )


def append_performance_profile(
    steps: list[dict[str, Any]],
    *,
    project: Path,
    shot_root: Path,
    shot_id: str,
    inputs: dict[str, Any],
    times_arg: str,
) -> None:
    if inputs.get("schema_version") != 2:
        return
    selected = set(inputs.get("engines", {}))
    if not selected.intersection({"rive", "pixijs-webgpu", "three-webgpu"}):
        return
    budget = require_file(shot_root / "performance-budget.json", "performance budget")
    steps.append(
        run_step(
            "profile-multi-engine",
            [
                "node",
                str(SCRIPT_ROOT / "profile_multi_engine.mjs"),
                "--project",
                str(project),
                "--shot-id",
                shot_id,
                "--at",
                times_arg,
                "--budget",
                str(budget),
            ],
            cwd=project,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--phase", choices=("prepare", "verify", "release"), default="prepare")
    parser.add_argument("--duration", type=float)
    parser.add_argument("--at", help="comma-separated absolute review times")
    parser.add_argument("--hyperframes", help="path to the pinned local HyperFrames binary")
    parser.add_argument("--force-scaffold", action="store_true")
    parser.add_argument("--skip-scaffold", action="store_true", help="prepare contracts without replacing a composition")
    parser.add_argument("--skip-doctor", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    project = args.project.expanduser().resolve()
    shot_root = project / "shots" / args.shot_id
    report_path = shot_root / "review" / f"pipeline-{args.phase}-report.json"
    steps: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "schema_version": 1,
        "shot_id": args.shot_id,
        "phase": args.phase,
        "project": str(project),
        "steps": steps,
        "ok": False,
    }
    try:
        if not project.is_dir():
            raise ValueError(f"project does not exist: {project}")
        duration = shot_duration(project, args.shot_id, args.duration)
        review_times = parse_review_times(
            args.at,
            default_review_times(project, args.shot_id, duration),
            duration,
        )
        times_arg = format_times(review_times)
        decision = shot_root / "animation-decision.json"
        spatial = shot_root / "spatial-contract.json"
        motion = shot_root / "motion-contract.json"
        compiled_motion = shot_root / "compiled-motion-track.json"
        rendered_motion = shot_root / "rendered-motion-review.json"
        capabilities = shot_root / "shot-capabilities.json"
        plan = shot_root / "engine-plan.json"
        inputs = shot_root / "engine-inputs.json"
        release = shot_root / "shot-release.json"
        pipeline_config = project / "hybrid-pipeline.json"
        if not pipeline_config.is_file():
            pipeline_config = SCRIPT_ROOT.parent / "assets" / "project-template" / "hybrid-pipeline.json"

        if args.phase == "prepare":
            require_file(decision, "animation decision")
            require_file(spatial, "spatial contract sidecar")
            require_file(capabilities, "shot capabilities")
            require_current_spatial_sidecar(project, args.shot_id, spatial)
            capabilities_data = load_json(capabilities, "shot capabilities")
            motion_required = needs_motion_contract(capabilities_data)
            steps.append(
                run_step(
                    "story-manifest-production",
                    [
                        sys.executable,
                        str(SCRIPT_ROOT / "validate_story_manifest.py"),
                        str(project / "story-manifest.json"),
                        "--project-dir",
                        str(project),
                        "--phase",
                        "production",
                        "--json",
                    ],
                    cwd=project,
                )
            )
            steps.append(
                run_step(
                    "animation-decision-planning",
                    [
                        sys.executable,
                        str(SCRIPT_ROOT / "review_animation_decision.py"),
                        str(decision),
                        "--phase",
                        "planning",
                        "--json",
                    ],
                    cwd=project,
                )
            )
            if motion_required:
                require_file(motion, "motion contract")
                steps.append(
                    run_step(
                        "motion-contract-planning",
                        [
                            sys.executable,
                            str(SCRIPT_ROOT / "audit_motion_contract.py"),
                            str(motion),
                            "--project",
                            str(project),
                            "--phase",
                            "planning",
                            "--json",
                        ],
                        cwd=project,
                    )
                )
            steps.append(
                run_step(
                    "route-capabilities",
                    [
                        sys.executable,
                        str(SCRIPT_ROOT / "route_shot_capabilities.py"),
                        str(capabilities),
                        "--config",
                        str(pipeline_config),
                        "--output",
                        str(plan),
                        "--strict",
                        "--json",
                    ],
                    cwd=project,
                )
            )
            if not args.skip_scaffold:
                scaffold_command = [
                    sys.executable,
                    str(SCRIPT_ROOT / "scaffold_hybrid_shot.py"),
                    "--plan",
                    str(plan),
                    "--project",
                    str(project),
                    "--duration",
                    str(duration),
                ]
                if args.force_scaffold:
                    scaffold_command.append("--force")
                steps.append(run_step("scaffold-shot", scaffold_command, cwd=project))
            require_file(inputs, "engine inputs")
            steps.append(
                run_step(
                    "audit-engine-inputs-development",
                    [
                        sys.executable,
                        str(SCRIPT_ROOT / "audit_engine_inputs.py"),
                        str(inputs),
                        "--plan",
                        str(plan),
                        "--project",
                        str(project),
                        "--phase",
                        "development",
                        "--json",
                    ],
                    cwd=project,
                )
            )
            append_p2_contract_audits(
                steps,
                project=project,
                inputs=load_json(inputs, "engine inputs"),
                phase="development",
            )
            if not args.skip_doctor:
                steps.append(
                    run_step(
                        "doctor-setup",
                        [
                            sys.executable,
                            str(SCRIPT_ROOT / "doctor_paper_pipeline.py"),
                            "--project",
                            str(project),
                            "--phase",
                            "setup",
                            "--skip-hyperframes-doctor",
                            "--json",
                        ],
                        cwd=project,
                    )
                )
        else:
            require_file(plan, "engine plan")
            require_file(inputs, "engine inputs")
            require_file(decision, "animation decision")
            require_file(spatial, "spatial contract sidecar")
            require_file(capabilities, "shot capabilities")
            require_current_spatial_sidecar(project, args.shot_id, spatial)
            capabilities_data = load_json(capabilities, "shot capabilities")
            motion_required = needs_motion_contract(capabilities_data)
            steps.append(
                run_step(
                    f"story-manifest-{'release' if args.phase == 'release' else 'production'}",
                    [
                        sys.executable,
                        str(SCRIPT_ROOT / "validate_story_manifest.py"),
                        str(project / "story-manifest.json"),
                        "--project-dir",
                        str(project),
                        "--phase",
                        "release" if args.phase == "release" else "production",
                        "--json",
                    ],
                    cwd=project,
                )
            )
            steps.append(
                run_step(
                    "animation-decision-planning",
                    [
                        sys.executable,
                        str(SCRIPT_ROOT / "review_animation_decision.py"),
                        str(decision),
                        "--phase",
                        "planning",
                        "--json",
                    ],
                    cwd=project,
                )
            )
            if motion_required:
                require_file(motion, "motion contract")
                steps.append(
                    run_step(
                        f"motion-contract-{'release' if args.phase == 'release' else 'implementation'}",
                        [
                            sys.executable,
                            str(SCRIPT_ROOT / "audit_motion_contract.py"),
                            str(motion),
                            "--project",
                            str(project),
                            "--phase",
                            "release" if args.phase == "release" else "implementation",
                            "--strict",
                            "--json",
                        ],
                        cwd=project,
                    )
                )
                steps.append(
                    run_step(
                        "compile-motion-track",
                        [
                            sys.executable,
                            str(SCRIPT_ROOT / "compile_motion_contract.py"),
                            str(motion),
                            "--project",
                            str(project),
                            "--output",
                            str(compiled_motion),
                            "--json",
                        ],
                        cwd=project,
                    )
                )
            route_record = run_step(
                "route-plan-current",
                [
                    sys.executable,
                    str(SCRIPT_ROOT / "route_shot_capabilities.py"),
                    str(capabilities),
                    "--config",
                    str(pipeline_config),
                    "--strict",
                    "--json",
                ],
                cwd=project,
            )
            steps.append(route_record)
            generated_plan = json.loads(route_record["stdout"]).get("plan")
            current_plan = load_json(plan, "engine plan")
            if generated_plan != current_plan:
                raise ValueError(
                    "engine-plan.json has drifted from shot-capabilities.json; "
                    "rerun the prepare phase and review the changed route"
                )
            steps.append(
                run_step(
                    "audit-engine-inputs-release",
                    [
                        sys.executable,
                        str(SCRIPT_ROOT / "audit_engine_inputs.py"),
                        str(inputs),
                        "--plan",
                        str(plan),
                        "--project",
                        str(project),
                        "--phase",
                        "release",
                        "--json",
                    ],
                    cwd=project,
                )
            )
            input_contract = load_json(inputs, "engine inputs")
            append_p2_contract_audits(
                steps,
                project=project,
                inputs=input_contract,
                phase="release",
            )
            hyperframes = resolve_hyperframes(project, args.hyperframes)
            if not args.skip_doctor:
                steps.append(
                    run_step(
                        "doctor-render",
                        [
                            sys.executable,
                            str(SCRIPT_ROOT / "doctor_paper_pipeline.py"),
                            "--project",
                            str(project),
                            "--phase",
                            "render",
                            "--hyperframes",
                            str(hyperframes),
                            "--json",
                        ],
                        cwd=project,
                    )
                )
            env = dict(os.environ)
            env["HYPERFRAMES_NO_UPDATE_CHECK"] = "1"
            check_command = [
                str(hyperframes),
                "check",
                str(project),
                "--samples",
                "15",
                "--at",
                times_arg,
            ]
            zone = caption_zone(project, args.shot_id)
            if zone:
                check_command.append(f"--caption-zone={zone}")
            check_command.append("--frame-check")
            steps.append(run_step("hyperframes-check", check_command, cwd=project, env=env))
            steps.append(
                run_step(
                    "deterministic-seek",
                    [
                        sys.executable,
                        str(SCRIPT_ROOT / "verify_deterministic_seek.py"),
                        "--project",
                        str(project),
                        "--shot-id",
                        args.shot_id,
                        "--at",
                        times_arg,
                        "--hyperframes",
                        str(hyperframes),
                        "--json",
                    ],
                    cwd=project,
                    env=env,
                )
            )
            append_webgpu_probe(
                steps,
                project=project,
                shot_root=shot_root,
                inputs=input_contract,
            )
            append_performance_profile(
                steps,
                project=project,
                shot_root=shot_root,
                shot_id=args.shot_id,
                inputs=input_contract,
                times_arg=times_arg,
            )
            if args.phase == "release":
                require_file(release, "shot release")
                release_data = load_json(release, "shot release")
                if release_data.get("schema_version") == 4 and release_data.get("motion_required") is not motion_required:
                    raise ValueError(
                        "shot-release.json motion_required must match the capability-derived motion policy "
                        f"({motion_required})"
                    )
                for previous_id in previous_shot_ids(project, args.shot_id):
                    previous_release = require_file(
                        project / "shots" / previous_id / "shot-release.json",
                        f"previous ordered shot {previous_id} release",
                    )
                    steps.append(
                        run_step(
                            f"previous-shot-release-{previous_id}",
                            [
                                sys.executable,
                                str(SCRIPT_ROOT / "audit_shot_release.py"),
                                str(previous_release),
                                "--strict",
                                "--json",
                            ],
                            cwd=project,
                        )
                    )
                if motion_required:
                    require_file(rendered_motion, "rendered motion review")
                    steps.append(
                        run_step(
                            "rendered-motion-release",
                            [
                                sys.executable,
                                str(SCRIPT_ROOT / "audit_rendered_motion.py"),
                                str(rendered_motion),
                                "--project",
                                str(project),
                                "--strict",
                                "--json",
                            ],
                            cwd=project,
                        )
                    )
                steps.append(
                    run_step(
                        "animation-decision-release",
                        [
                            sys.executable,
                            str(SCRIPT_ROOT / "review_animation_decision.py"),
                            str(decision),
                            "--phase",
                            "release",
                            "--json",
                        ],
                        cwd=project,
                    )
                )
                steps.append(
                    run_step(
                        "shot-release",
                        [
                            sys.executable,
                            str(SCRIPT_ROOT / "audit_shot_release.py"),
                            str(release),
                            "--strict",
                            "--json",
                        ],
                        cwd=project,
                    )
                )
        report.update(
            {
                "duration": duration,
                "review_times": review_times,
                "ok": True,
                "result": "pass",
            }
        )
    except (OSError, ValueError, StepFailure) as exc:
        if isinstance(exc, StepFailure):
            steps.append(
                {
                    "name": exc.step,
                    "command": exc.command,
                    "returncode": exc.result.returncode,
                    "stdout": exc.result.stdout.strip(),
                    "stderr": exc.result.stderr.strip(),
                    "ok": False,
                }
            )
        report.update({"ok": False, "result": "fail", "error": str(exc)})

    write_report(report_path, report)
    report["report"] = str(report_path)
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for step in steps:
            print(f"{'PASS' if step['ok'] else 'FAIL'} {step['name']}")
        if report["ok"]:
            print(f"PASS: routed shot {args.shot_id} {args.phase} completed")
        else:
            print(f"FAIL: {report.get('error')}")
        print(f"Report: {report_path}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
