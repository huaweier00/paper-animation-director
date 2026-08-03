#!/usr/bin/env python3
"""Validate shot capability requirements and emit a deterministic hybrid engine plan."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VALID_CHARACTER = {"none", "rigid-2d", "pose-replacement", "skeletal-2d", "mesh-deform-2d", "3d-rig"}
VALID_CONTACT = {"none", "staged", "continuous", "simulated"}
VALID_DEPTH = {"flat", "multiplane", "2.5d", "3d"}
VALID_CAMERA = {"static", "2d", "parallax", "3d"}
VALID_PARTICLES = {"none", "light", "heavy"}
VALID_SIMULATION = {"none", "deterministic-runtime", "baked-physics"}
VALID_TYPOGRAPHY = {"none", "supporting", "primary"}
VALID_REUSE = {"one-off", "recurring"}
VALID_CHARACTER_ENGINES = {"auto", "rive", "spine"}
VALID_EFFECT_ENGINES = {"auto", "pixijs-webgpu", "three-webgpu"}
VALID_SPATIAL_ENGINES = {"auto", "gsap-dom", "three-webgpu", "blender"}
VALID_DELIVERY = {"auto", "embedded-seekable", "pre-render-alpha", "pre-render-opaque"}
KNOWN_ENGINES = {"gsap-dom", "rive", "spine", "pixijs-webgpu", "three-webgpu", "blender"}

DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": 1,
    "orchestrator": "hyperframes",
    "defaults": {
        "simple_2d": "gsap-dom",
        "character_2d": "rive",
        "character_2d_alternative": "spine",
        "effects_2d": "pixijs-webgpu",
        "spatial_2_5d": "three-webgpu",
        "hero_offline": "blender",
        "runtime_delivery": "embedded-seekable",
        "offline_delivery": "pre-render-alpha",
    },
    "policies": {
        "allow_runtime_network": False,
        "require_local_assets": True,
        "require_absolute_time": True,
        "require_seeded_randomness": True,
        "require_engine_plan": True,
        "require_engine_benchmark": True,
        "stateful_simulation_delivery": "pre-render",
        "state_machine_delivery": "pre-render",
    },
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def finding(severity: str, path: str, message: str) -> dict[str, str]:
    return {"severity": severity, "path": path, "message": message}


def validate_capabilities(data: Any) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [finding("error", "$", "root must be a JSON object")]
    if data.get("schema_version") != 1:
        out.append(finding("error", "schema_version", "expected schema_version 1"))
    shot_id = data.get("shot_id")
    if not nonempty(shot_id) or not ID_RE.match(shot_id):
        out.append(finding("error", "shot_id", "use a non-empty kebab-case shot id"))
    if not nonempty(data.get("responsibility")):
        out.append(finding("error", "responsibility", "state what the audience must perceive"))

    requirements = data.get("requirements")
    if not isinstance(requirements, dict):
        out.append(finding("error", "requirements", "requirements must be an object"))
        requirements = {}
    enum_fields = {
        "character_motion": VALID_CHARACTER,
        "contact": VALID_CONTACT,
        "spatial_depth": VALID_DEPTH,
        "camera": VALID_CAMERA,
        "particle_load": VALID_PARTICLES,
        "simulation": VALID_SIMULATION,
        "typography": VALID_TYPOGRAPHY,
        "reuse": VALID_REUSE,
    }
    for key, allowed in enum_fields.items():
        if requirements.get(key) not in allowed:
            out.append(finding("error", f"requirements.{key}", f"expected one of {sorted(allowed)}"))
    effects = requirements.get("environment_fx")
    if not isinstance(effects, list) or any(not nonempty(item) for item in effects):
        out.append(finding("error", "requirements.environment_fx", "use a list of named effects, or an empty list"))

    constraints = data.get("constraints")
    if not isinstance(constraints, dict):
        out.append(finding("error", "constraints", "constraints must be an object"))
        constraints = {}
    for key in ("must_remain_2d", "offline_render_allowed", "alpha_required", "manual_authoring_allowed"):
        if not isinstance(constraints.get(key), bool):
            out.append(finding("error", f"constraints.{key}", "declare true or false explicitly"))

    preferences = data.get("preferences", {})
    if not isinstance(preferences, dict):
        out.append(finding("error", "preferences", "preferences must be an object"))
        preferences = {}
    preference_enums = {
        "character_engine": VALID_CHARACTER_ENGINES,
        "effects_engine": VALID_EFFECT_ENGINES,
        "spatial_engine": VALID_SPATIAL_ENGINES,
        "delivery": VALID_DELIVERY,
    }
    for key, allowed in preference_enums.items():
        value = preferences.get(key, "auto")
        if value not in allowed:
            out.append(finding("error", f"preferences.{key}", f"expected one of {sorted(allowed)}"))
    forbidden = preferences.get("forbid_engines", [])
    if not isinstance(forbidden, list) or any(item not in KNOWN_ENGINES for item in forbidden):
        out.append(finding("error", "preferences.forbid_engines", f"use only known engines: {sorted(KNOWN_ENGINES)}"))

    proofs = data.get("proof_requirements")
    if not isinstance(proofs, list) or not proofs or any(not nonempty(item) for item in proofs):
        out.append(finding("error", "proof_requirements", "add at least one rendered, observable proof requirement"))

    if requirements.get("spatial_depth") == "3d" and constraints.get("must_remain_2d") is True:
        out.append(finding("error", "constraints.must_remain_2d", "cannot require both 3D spatial depth and a strictly 2D result"))
    if (
        requirements.get("simulation") == "baked-physics"
        or requirements.get("contact") == "simulated"
        or requirements.get("character_motion") == "3d-rig"
    ) and constraints.get("offline_render_allowed") is False:
        out.append(
            finding(
                "error",
                "constraints.offline_render_allowed",
                "the declared simulation or 3D rig requires an offline render path",
            )
        )
    if requirements.get("character_motion") in {"skeletal-2d", "mesh-deform-2d", "3d-rig"} and constraints.get(
        "manual_authoring_allowed"
    ) is False:
        out.append(
            finding(
                "warning",
                "constraints.manual_authoring_allowed",
                "high-quality rigging requires authored bones, meshes, weights, or a prepared 3D rig",
            )
        )
    return out


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return DEFAULT_CONFIG
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("pipeline config must be a schema_version 1 JSON object")
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    merged.update({key: value for key, value in data.items() if key not in {"defaults", "policies"}})
    merged["defaults"].update(data.get("defaults", {}))
    merged["policies"].update(data.get("policies", {}))
    return merged


def risk_score(requirements: dict[str, Any]) -> int:
    score = 0
    score += {"none": 0, "rigid-2d": 0, "pose-replacement": 1, "skeletal-2d": 2, "mesh-deform-2d": 3, "3d-rig": 4}[
        requirements["character_motion"]
    ]
    score += {"none": 0, "staged": 1, "continuous": 2, "simulated": 4}[requirements["contact"]]
    score += {"flat": 0, "multiplane": 1, "2.5d": 2, "3d": 3}[requirements["spatial_depth"]]
    score += {"none": 0, "light": 1, "heavy": 2}[requirements["particle_load"]]
    score += {"none": 0, "deterministic-runtime": 1, "baked-physics": 4}[requirements["simulation"]]
    return score


def build_plan(data: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    requirements = data["requirements"]
    constraints = data["constraints"]
    preferences = data.get("preferences", {})
    forbidden = set(preferences.get("forbid_engines", []))
    defaults = config["defaults"]
    layers: dict[str, dict[str, Any]] = {}

    def add(engine: str, role: str, integration: str, reason: str) -> None:
        if engine in forbidden:
            raise ValueError(f"required engine {engine!r} is forbidden by preferences")
        layer = layers.setdefault(
            engine,
            {"engine": engine, "role": [], "integration": integration, "reason": []},
        )
        if role not in layer["role"]:
            layer["role"].append(role)
        if reason not in layer["reason"]:
            layer["reason"].append(reason)

    needs_offline = (
        requirements["simulation"] == "baked-physics"
        or requirements["contact"] == "simulated"
        or requirements["character_motion"] == "3d-rig"
    )

    if needs_offline:
        add(
            defaults["hero_offline"],
            "hero-action",
            preferences.get("delivery", "auto")
            if preferences.get("delivery", "auto") in {"pre-render-alpha", "pre-render-opaque"}
            else defaults["offline_delivery"],
            "stateful physics, simulated contact, or a 3D rig must be baked before HyperFrames assembly",
        )
    else:
        character_motion = requirements["character_motion"]
        if character_motion in {"skeletal-2d", "mesh-deform-2d"}:
            character_engine = preferences.get("character_engine", "auto")
            if character_engine == "auto":
                character_engine = defaults["character_2d"]
            integration = preferences.get("delivery", "auto")
            if integration == "auto":
                integration = defaults["runtime_delivery"]
            add(
                character_engine,
                "character",
                integration,
                f"{character_motion.replace('-', ' ')} character motion requires continuous articulation",
            )
            if requirements["contact"] == "continuous":
                add(
                    character_engine,
                    "contact",
                    integration,
                    "continuous contact benefits from a rigged 2D character system",
                )
        elif character_motion in {"rigid-2d", "pose-replacement"}:
            add(
                defaults["simple_2d"],
                "character",
                "native",
                "rigid or stepped pose motion can remain on a seek-safe DOM timeline",
            )

        spatial_engine = preferences.get("spatial_engine", "auto")
        if requirements["spatial_depth"] in {"2.5d", "3d"} or requirements["camera"] == "3d":
            if spatial_engine == "auto":
                spatial_engine = defaults["spatial_2_5d"]
            add(
                spatial_engine,
                "space",
                defaults["runtime_delivery"] if spatial_engine != "blender" else defaults["offline_delivery"],
                "2.5D/3D depth or a 3D camera needs a real scene and camera transform",
            )
        elif requirements["spatial_depth"] == "multiplane" or requirements["camera"] == "parallax":
            add(
                defaults["simple_2d"],
                "space",
                "native",
                "multiplane parallax can remain deterministic on the DOM timeline",
            )

        has_fx = requirements["particle_load"] != "none" or bool(requirements["environment_fx"])
        if has_fx:
            if "three-webgpu" in layers and (
                requirements["particle_load"] == "heavy" or requirements["spatial_depth"] in {"2.5d", "3d"}
            ):
                add(
                    "three-webgpu",
                    "effects",
                    defaults["runtime_delivery"],
                    "spatial particles and effects should share the 3D renderer",
                )
            else:
                effects_engine = preferences.get("effects_engine", "auto")
                if effects_engine == "auto":
                    effects_engine = defaults["effects_2d"]
                add(
                    effects_engine,
                    "effects",
                    defaults["runtime_delivery"],
                    "2D environmental effects need deterministic GPU particles, masks, or displacement",
                )

    if requirements["typography"] != "none":
        add(
            defaults["simple_2d"],
            "typography",
            "native",
            "typography and editorial overlays remain on the HyperFrames DOM timeline",
        )
    if not layers:
        add(
            defaults["simple_2d"],
            "tableau",
            "native",
            "the shot has no capability requirement that justifies a specialized engine",
        )

    fallbacks: list[dict[str, str]] = []
    asset_requirements: list[str] = []
    for engine in layers:
        if engine in {"rive", "spine"}:
            fallbacks.append(
                {
                    "engine": engine,
                    "fallback": "pre-render-alpha",
                    "condition": "the animation cannot be reconstructed from absolute time",
                }
            )
            asset_requirements.append("a separated or mesh-ready character source plus an approved bone/mesh rig")
        elif engine == "pixijs-webgpu":
            fallbacks.append(
                {
                    "engine": engine,
                    "fallback": "baked-alpha-or-gsap-svg",
                    "condition": "the render environment cannot provide the required GPU path",
                }
            )
            asset_requirements.append("local effect textures, deterministic emitters, and fixed particle seeds")
        elif engine == "three-webgpu":
            fallbacks.append(
                {
                    "engine": engine,
                    "fallback": "baked-video-or-multiplane-gsap",
                    "condition": "WebGPU/WebGL capture is unavailable or the scene depends on frame history",
                }
            )
            asset_requirements.append("local depth plates, textures, GLTF assets, shaders, and fixed camera units")
        elif engine == "blender":
            asset_requirements.append("the editable .blend source, baked caches, render settings, and an alpha/opaque master")

    score = risk_score(requirements)
    specialized = any(engine != "gsap-dom" for engine in layers)
    return {
        "schema_version": 1,
        "shot_id": data["shot_id"],
        "orchestrator": config.get("orchestrator", "hyperframes"),
        "engines": list(layers),
        "layers": list(layers.values()),
        "benchmark_required": bool(config["policies"].get("require_engine_benchmark", True) and (specialized or score >= 3)),
        "risk_score": score,
        "seek_contract": {
            "clock": "hyperframes-absolute-seconds",
            "event": "hf-seek",
            "wall_clock_forbidden": True,
            "unseeded_random_forbidden": True,
            "stateful_runtime_simulation_forbidden": True,
        },
        "fallbacks": fallbacks,
        "asset_requirements": list(dict.fromkeys(asset_requirements)),
        "proof_requirements": data["proof_requirements"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capabilities", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit findings and plan in one JSON envelope")
    args = parser.parse_args()

    try:
        data = json.loads(args.capabilities.read_text(encoding="utf-8"))
        config = load_config(args.config)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Could not load routing inputs: {exc}", file=sys.stderr)
        raise SystemExit(2)

    findings = validate_capabilities(data)
    errors = [item for item in findings if item["severity"] == "error"]
    warnings = [item for item in findings if item["severity"] == "warning"]
    plan: dict[str, Any] | None = None
    if not errors:
        try:
            plan = build_plan(data, config)
        except ValueError as exc:
            errors.append(finding("error", "preferences", str(exc)))
            findings = [*findings, errors[-1]]

    ok = not errors and (not warnings or not args.strict)
    if plan is not None and args.output and ok:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.as_json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "errors": len(errors),
                    "warnings": len(warnings),
                    "findings": findings,
                    "plan": plan,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif plan is not None and not args.output:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"[{item['severity'].upper()}] {item['path']}: {item['message']}")
        if plan is not None and args.output and ok:
            print(f"Wrote engine plan: {args.output}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
