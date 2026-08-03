#!/usr/bin/env python3
"""Diagnose a routed paper-animation project without using the network."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


VERSION_RE = re.compile(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?")
ENGINE_PACKAGES = {
    "gsap-dom": ("gsap", "node_modules/gsap/dist/gsap.min.js"),
    "rive": (
        "@rive-app/canvas-advanced-single",
        "node_modules/@rive-app/canvas-advanced-single/canvas_advanced_single.mjs",
    ),
    "pixijs-webgpu": ("pixi.js", "node_modules/pixi.js/dist/pixi.mjs"),
    "three-webgpu": ("three", "node_modules/three/build/three.webgpu.js"),
    "blender": (None, None),
    "spine": (None, None),
}


def check(name: str, status: str, message: str, **details: Any) -> dict[str, Any]:
    return {"name": name, "status": status, "message": message, **details}


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} root must be an object")
    return data


def command_version(command: str, args: list[str] | None = None) -> tuple[bool, str]:
    path = shutil.which(command)
    if not path:
        return False, f"{command} not found"
    result = subprocess.run(
        [path, *(args or ["--version"])],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or result.stderr).splitlines()
    return result.returncode == 0, output[0].strip() if output else f"{command} exit {result.returncode}"


def major_version(value: str) -> int | None:
    match = VERSION_RE.search(value)
    return int(match.group(1)) if match else None


def audit_lock(project: Path) -> tuple[list[str], list[str], dict[str, str]]:
    errors: list[str] = []
    warnings: list[str] = []
    versions: dict[str, str] = {}
    package = read_json(project / "package.json", "package.json")
    lock = read_json(project / "package-lock.json", "package-lock.json")
    if lock.get("lockfileVersion") != 3:
        errors.append("package-lock.json: expected lockfileVersion 3")
    root = lock.get("packages", {}).get("") if isinstance(lock.get("packages"), dict) else None
    if not isinstance(root, dict):
        errors.append("package-lock.json: missing packages[''] root")
        return errors, warnings, versions
    for group in ("dependencies", "devDependencies"):
        declared = package.get(group, {})
        locked_root = root.get(group, {})
        if not isinstance(declared, dict):
            errors.append(f"package.json.{group}: expected an object")
            continue
        if not isinstance(locked_root, dict):
            errors.append(f"package-lock.json packages[''].{group}: expected an object")
            locked_root = {}
        for name, version in declared.items():
            if not isinstance(version, str) or version.startswith(("^", "~", ">", "<", "*")):
                errors.append(f"package.json {name}: exact version required, got {version!r}")
                continue
            if locked_root.get(name) != version:
                errors.append(
                    f"lock drift: {name} package.json={version!r}, lock root={locked_root.get(name)!r}"
                )
            node = lock.get("packages", {}).get(f"node_modules/{name}")
            if not isinstance(node, dict):
                errors.append(f"package-lock.json: missing node_modules/{name}")
                continue
            locked_version = node.get("version")
            versions[name] = str(locked_version)
            if locked_version != version:
                errors.append(
                    f"lock drift: {name} package.json={version!r}, locked package={locked_version!r}"
                )
    if package.get("name") != lock.get("name") or package.get("name") != root.get("name"):
        errors.append("package name differs between package.json and package-lock.json")
    return errors, warnings, versions


def selected_engines(project: Path) -> set[str]:
    selected: set[str] = set()
    for path in sorted((project / "shots").glob("*/engine-plan.json")):
        try:
            plan = read_json(path, "engine plan")
        except ValueError:
            continue
        engines = plan.get("engines")
        if isinstance(engines, list):
            selected.update(item for item in engines if isinstance(item, str))
    return selected


def local_project_path(project: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    if value.startswith(("http://", "https://", "//", "data:")):
        return None
    candidate = (project / value.removeprefix("./")).resolve()
    try:
        candidate.relative_to(project)
    except ValueError:
        return None
    return candidate


def audit_p2_sidecars(project: Path) -> tuple[list[str], list[str]]:
    """Check that schema-v2 routed shots carry all required P2 control files."""
    errors: list[str] = []
    warnings: list[str] = []
    for inputs_path in sorted((project / "shots").glob("*/engine-inputs.json")):
        try:
            inputs = read_json(inputs_path, "engine inputs")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if inputs.get("schema_version") != 2:
            continue
        shot_root = inputs_path.parent
        shot_id = shot_root.name
        budget = shot_root / "performance-budget.json"
        if not budget.is_file():
            errors.append(f"{shot_id}: performance-budget.json is missing")
        engines = inputs.get("engines")
        if not isinstance(engines, dict):
            errors.append(f"{shot_id}: schema-v2 engines must be an object")
            continue
        for engine, field in (
            ("rive", "rig_manifest"),
            ("three-webgpu", "scene_manifest"),
            ("blender", "action_library"),
        ):
            config = engines.get(engine)
            if not isinstance(config, dict):
                continue
            target = local_project_path(project, config.get(field))
            if target is None:
                errors.append(f"{shot_id}: {engine}.{field} must be a local project path")
            elif not target.is_file():
                errors.append(f"{shot_id}: {engine}.{field} not found: {target}")
        if "three-webgpu" in engines:
            capability = shot_root / "webgpu-capability.json"
            if not capability.is_file():
                errors.append(f"{shot_id}: webgpu-capability.json is missing")
            else:
                try:
                    policy = read_json(capability, "WebGPU capability policy")
                    release_policy = policy.get("release_policy")
                    if (
                        policy.get("schema_version") != 1
                        or not isinstance(release_policy, dict)
                        or release_policy.get("probe_report_required_when_three_selected") is not True
                    ):
                        errors.append(f"{shot_id}: WebGPU capability policy is incomplete")
                except ValueError as exc:
                    errors.append(str(exc))
    return errors, warnings


def run_hyperframes_doctor(binary: Path, project: Path) -> tuple[str, str, dict[str, Any] | None]:
    env = dict(os.environ)
    env["HYPERFRAMES_NO_UPDATE_CHECK"] = "1"
    result = subprocess.run(
        [str(binary), "doctor", "--json"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    payload: dict[str, Any] | None = None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return "fail", result.stderr.strip() or result.stdout.strip() or "invalid doctor JSON", None
    if payload.get("ok") is True:
        return "ok", "HyperFrames doctor reports ok", payload
    required = {"Version", "Node.js", "Disk", "Environment", "FFmpeg", "FFprobe", "Chrome"}
    failed_required = [
        item
        for item in payload.get("checks", [])
        if isinstance(item, dict) and item.get("name") in required and item.get("ok") is not True
    ]
    if failed_required:
        names = ", ".join(str(item.get("name")) for item in failed_required)
        return "fail", f"HyperFrames doctor failed required render checks: {names}", payload
    optional = [
        str(item.get("name"))
        for item in payload.get("checks", [])
        if isinstance(item, dict) and item.get("ok") is not True and item.get("name") not in required
    ]
    return (
        "warn",
        "required HyperFrames render checks pass; optional tools unavailable: "
        + (", ".join(optional) if optional else "unspecified"),
        payload,
    )


def diagnose(
    project: Path,
    *,
    phase: str,
    hyperframes_override: Path | None,
    run_hyperframes: bool,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    python_ok = sys.version_info >= (3, 9)
    checks.append(
        check(
            "python",
            "ok" if python_ok else "fail",
            f"Python {sys.version.split()[0]} (>= 3.9 required)",
        )
    )
    node_ok, node_version = command_version("node")
    node_major = major_version(node_version) if node_ok else None
    checks.append(
        check(
            "node",
            "ok" if node_ok and node_major is not None and node_major >= 22 else "fail",
            f"{node_version} (>= 22 required)",
        )
    )
    npm_ok, npm_version = command_version("npm")
    checks.append(check("npm", "ok" if npm_ok else "fail", npm_version))
    ffmpeg_ok, ffmpeg_version = command_version("ffmpeg", ["-version"])
    checks.append(check("ffmpeg", "ok" if ffmpeg_ok else "fail", ffmpeg_version))
    ffprobe_ok, ffprobe_version = command_version("ffprobe", ["-version"])
    checks.append(check("ffprobe", "ok" if ffprobe_ok else "fail", ffprobe_version))

    try:
        lock_errors, lock_warnings, versions = audit_lock(project)
    except ValueError as exc:
        lock_errors, lock_warnings, versions = [str(exc)], [], {}
    checks.append(
        check(
            "dependency-lock",
            "fail" if lock_errors else ("warn" if lock_warnings else "ok"),
            "; ".join(lock_errors or lock_warnings or ["package.json and package-lock.json agree"]),
            versions=versions,
        )
    )

    policy_path = project / "offline-dependency-policy.json"
    try:
        policy = read_json(policy_path, "offline dependency policy")
        policy_ok = (
            policy.get("policies", {}).get("runtime_network_forbidden") is True
            and policy.get("policies", {}).get("lock_drift_blocks_render") is True
        )
        checks.append(
            check(
                "offline-policy",
                "ok" if policy_ok else "fail",
                "offline install and no-runtime-network policy present"
                if policy_ok
                else "offline policy is missing required release guards",
            )
        )
    except ValueError as exc:
        policy = {}
        checks.append(check("offline-policy", "fail", str(exc)))

    engines = selected_engines(project)
    if not engines:
        checks.append(check("engine-plans", "warn", "no routed engine-plan.json files found"))
    else:
        checks.append(check("engine-plans", "ok", f"selected engines: {', '.join(sorted(engines))}"))

    p2_errors, p2_warnings = audit_p2_sidecars(project)
    checks.append(
        check(
            "p2-sidecars",
            "fail" if p2_errors else ("warn" if p2_warnings else "ok"),
            "; ".join(p2_errors or p2_warnings or ["schema-v2 engine sidecars are complete"]),
        )
    )

    require_installed = phase == "render"
    required_files = policy.get("required_runtime_files", {}) if isinstance(policy, dict) else {}
    for engine in sorted(engines):
        package_name, fallback_path = ENGINE_PACKAGES.get(engine, (None, None))
        relative = required_files.get(package_name) if package_name else fallback_path
        if engine == "blender":
            blender = Path("/Applications/Blender.app/Contents/MacOS/Blender")
            available = blender.is_file() or shutil.which("blender") is not None
            checks.append(
                check(
                    "engine:blender",
                    "ok" if available else "warn",
                    "Blender available"
                    if available
                    else "Blender not found locally; pre-render must be supplied from an authored build machine",
                )
            )
        elif engine == "spine":
            checks.append(
                check(
                    "engine:spine",
                    "warn",
                    "Spine has no bundled runtime; a declared local runtime or pre-render is required",
                )
            )
        elif relative:
            path = project / relative
            status = "ok" if path.is_file() else ("fail" if require_installed else "warn")
            checks.append(
                check(
                    f"engine:{engine}",
                    status,
                    f"local runtime {'found' if path.is_file() else 'missing'}: {relative}",
                )
            )

    binary = (
        hyperframes_override.expanduser().resolve()
        if hyperframes_override
        else project / "node_modules" / ".bin" / "hyperframes"
    )
    if run_hyperframes:
        if not binary.is_file():
            checks.append(
                check(
                    "hyperframes-doctor",
                    "fail" if require_installed else "warn",
                    f"local pinned HyperFrames binary missing: {binary}",
                )
            )
        else:
            status, message, payload = run_hyperframes_doctor(binary, project)
            checks.append(check("hyperframes-doctor", status, message, payload=payload))

    disk = shutil.disk_usage(project)
    free_gib = disk.free / (1024**3)
    checks.append(
        check(
            "disk",
            "ok" if free_gib >= 5 else "warn",
            f"{free_gib:.1f} GiB free",
        )
    )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--phase", choices=("setup", "render"), default="setup")
    parser.add_argument("--hyperframes", type=Path)
    parser.add_argument("--skip-hyperframes-doctor", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    project = args.project.expanduser().resolve()
    checks = diagnose(
        project,
        phase=args.phase,
        hyperframes_override=args.hyperframes,
        run_hyperframes=not args.skip_hyperframes_doctor,
    )
    failed = [item for item in checks if item["status"] == "fail"]
    warned = [item for item in checks if item["status"] == "warn"]
    result = {
        "project": str(project),
        "phase": args.phase,
        "ok": not failed,
        "errors": len(failed),
        "warnings": len(warned),
        "checks": checks,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        icons = {"ok": "PASS", "warn": "WARN", "fail": "FAIL"}
        for item in checks:
            print(f"{icons[item['status']]} {item['name']}: {item['message']}")
        print("PASS: environment is ready" if not failed else "FAIL: environment is not ready")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
