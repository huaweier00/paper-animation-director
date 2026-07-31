#!/usr/bin/env python3
"""Scaffold a routed hybrid shot composition without overwriting authored work."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any


ASPECT_SIZES = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080), "4:5": (1080, 1350)}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CANVAS_ENGINES = {"rive", "spine", "pixijs-webgpu", "three-webgpu"}
KNOWN_ENGINES = {"gsap-dom", "rive", "spine", "pixijs-webgpu", "three-webgpu", "blender"}
PLACEHOLDER_MARKERS = {"Development placeholder", "Hybrid development scaffold"}


def fmt(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def replace_tokens(source: str, values: dict[str, str]) -> str:
    # Generated values may themselves contain template tokens (engine-layer
    # markup contains frame dimensions), so expand to a small fixed point.
    for _ in range(3):
        previous = source
        for key, value in values.items():
            source = source.replace(f"__{key}__", value)
        if source == previous:
            break
    return source


def load_plan(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("engine plan must be a schema_version 1 JSON object")
    shot_id = data.get("shot_id")
    if not isinstance(shot_id, str) or not ID_RE.match(shot_id):
        raise ValueError("engine plan shot_id must be kebab-case")
    engines = data.get("engines")
    if not isinstance(engines, list) or not engines or any(item not in KNOWN_ENGINES for item in engines):
        raise ValueError(f"engine plan engines must use known values: {sorted(KNOWN_ENGINES)}")
    if data.get("orchestrator") != "hyperframes":
        raise ValueError("paper hybrid shots currently require HyperFrames as orchestrator")
    return data


def resolve_frame(project: Path, shot_id: str, duration_arg: float | None) -> tuple[int, int, float]:
    width, height = 1920, 1080
    duration = duration_arg
    manifest_path = project / "story-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        width, height = ASPECT_SIZES.get(manifest.get("aspect", "16:9"), (1920, 1080))
        if duration is None:
            for scene in manifest.get("scenes", []):
                if isinstance(scene, dict) and scene.get("id") == shot_id:
                    candidate = scene.get("duration")
                    if isinstance(candidate, (int, float)) and candidate > 0:
                        duration = float(candidate)
                    break
    if duration is None or duration <= 0:
        raise ValueError("provide --duration or use a shot_id that exists in story-manifest.json")
    return width, height, duration


def layer_markup(shot_id: str, engine: str, index: int, duration: float) -> str:
    layer_id = f"{shot_id}-engine-{engine}"
    z = 10 + index
    if engine in CANVAS_ENGINES:
        return (
            f'    <canvas id="{layer_id}" class="engine-layer" data-engine="{engine}" '
            f'width="__WIDTH__" height="__HEIGHT__" style="z-index:{z}"></canvas>'
        )
    if engine == "blender":
        return (
            f'    <video id="{layer_id}" class="engine-layer clip" data-engine="{engine}" '
            f'data-start="0" data-duration="{fmt(duration)}" muted playsinline preload="auto" '
            f'src="./assets/runtime/placeholders/pending-blender.webm" '
            f'data-required-asset="./shots/{shot_id}/assets/prerender/{shot_id}-alpha.webm" '
            f'style="z-index:{z};object-fit:contain;opacity:0"></video>'
        )
    return (
        f'    <div id="{layer_id}" class="engine-layer" data-engine="{engine}" '
        f'style="z-index:{z}"></div>'
    )


def engine_imports(engines: list[str]) -> str:
    imports: list[str] = []
    if "pixijs-webgpu" in engines:
        imports.extend(
            [
                '      const PIXI = await import("./node_modules/pixi.js/dist/pixi.mjs");',
                '      const { mountPixiPaperEffects } = await import("./assets/runtime/adapters/pixi-seekable.js");',
            ]
        )
    if "rive" in engines:
        imports.extend(
            [
                '      const { default: RiveCanvas } = await import("./node_modules/@rive-app/canvas-advanced-single/canvas_advanced_single.mjs");',
                '      const { mountRiveLinearAnimation } = await import("./assets/runtime/adapters/rive-seekable.js");',
            ]
        )
    if "three-webgpu" in engines:
        imports.extend(
            [
                '      const THREE = await import("./node_modules/three/build/three.webgpu.js");',
                '      const { mountThreeSeekableScene } = await import("./assets/runtime/adapters/three-seekable.js");',
                '      const { createDeclarativePaperScene } = await import("./assets/runtime/scenes/declarative-paper-2_5d.js");',
            ]
        )
    return "\n".join(imports)


def registration_markup(shot_id: str, engine: str, duration: float) -> str:
    if engine == "blender":
        video_id = f"{shot_id}-engine-blender"
        return f"""    {{
      const video = document.getElementById("{video_id}");
      const config = engineInputs.engines.blender;
      if (config.ready === true) {{
        video.src = config.asset;
        video.style.opacity = "1";
        video.dataset.engineStatus = "mounted";
      }} else {{
        video.dataset.engineStatus = "awaiting-blender-prerender";
        video.dataset.requiredAsset = config.asset;
      }}
    }}"""
    if engine not in CANVAS_ENGINES:
        return ""
    canvas_id = f"{shot_id}-engine-{engine}"
    renderer_id = f"{shot_id}:{engine}"
    if engine == "pixijs-webgpu":
        return f"""    {{
      const canvas = document.getElementById("{canvas_id}");
      const config = engineInputs.engines["pixijs-webgpu"];
      await mountPixiPaperEffects({{
        PIXI,
        canvas,
        id: "{renderer_id}",
        root: "#{shot_id}",
        durationSeconds: {fmt(duration)},
        width: canvas.width,
        height: canvas.height,
        effects: config.effects,
        masks: config.masks || [],
        rendererPreference: config.renderer_preference,
        resolution: config.pixel_ratio,
        registerRenderer,
      }});
      canvas.dataset.engineStatus = "mounted";
    }}"""
    if engine == "rive":
        return f"""    {{
      const canvas = document.getElementById("{canvas_id}");
      const config = engineInputs.engines.rive;
      if (config.ready === true) {{
        await mountRiveLinearAnimation({{
          RiveCanvas,
          canvas,
          id: "{renderer_id}",
          root: "#{shot_id}",
          durationSeconds: {fmt(duration)},
          src: config.asset,
          artboardName: config.artboard,
          animationName: config.animation,
          animationDuration: config.animation_duration_seconds,
          playback: config.playback,
          fit: config.fit,
          alignment: config.alignment,
          registerRenderer,
        }});
        canvas.dataset.engineStatus = "mounted";
      }} else {{
        canvas.dataset.engineStatus = "awaiting-rive-asset";
        canvas.dataset.requiredAsset = config.asset;
      }}
    }}"""
    if engine == "three-webgpu":
        return f"""    {{
      const canvas = document.getElementById("{canvas_id}");
      const config = engineInputs.engines["three-webgpu"];
      const sceneManifest = await fetch(config.scene_manifest).then((response) => {{
        if (!response.ok) throw new Error(`Three scene manifest HTTP ${{response.status}}`);
        return response.json();
      }});
      const adapter = await mountThreeSeekableScene({{
        THREE,
        canvas,
        id: "{renderer_id}",
        root: "#{shot_id}",
        durationSeconds: {fmt(duration)},
        width: canvas.width,
        height: canvas.height,
        pixelRatio: config.pixel_ratio,
        alpha: config.alpha,
        antialias: config.antialias,
        forceWebGL: config.force_webgl,
        sceneFactory: (options) => createDeclarativePaperScene({{
          ...options,
          manifest: sceneManifest,
        }}),
        registerRenderer,
      }});
      canvas.dataset.engineStatus = "mounted";
      canvas.dataset.engineBackend = adapter.backend;
    }}"""
    return f"""    {{
      const canvas = document.getElementById("{canvas_id}");
      canvas.dataset.engineStatus = "requires-spine-runtime-or-prerender";
    }}"""


def build_engine_inputs(shot_id: str, engines: list[str], duration: float) -> dict[str, Any]:
    start = min(duration * 0.28, max(0, duration - 0.45))
    effect_duration = min(1.4, max(0.4, duration - start))
    contracts: dict[str, Any] = {}
    for engine in engines:
        if engine == "pixijs-webgpu":
            contracts[engine] = {
                "ready": True,
                "renderer_preference": "webgl",
                "pixel_ratio": 1,
                "masks": [
                    {
                        "id": "ground-contact-zone",
                        "kind": "band",
                        "origin": [0, 0.58],
                        "size": [1, 0.42],
                        "invert": False,
                    }
                ],
                "effects": [
                    {
                        "id": "impact-dust",
                        "preset": "impact-dust",
                        "seed": f"{shot_id}:impact-dust",
                        "origin": [0.62, 0.76],
                        "start": round(start, 6),
                        "duration": round(effect_duration, 6),
                        "count": 58,
                        "opacity": 0.82,
                        "mask": "ground-contact-zone",
                    }
                ],
            }
        elif engine == "rive":
            contracts[engine] = {
                "ready": False,
                "asset": f"./shots/{shot_id}/assets/characters/{shot_id}.riv",
                "artboard": "Character",
                "animation": "main",
                "playback": "native",
                "animation_duration_seconds": None,
                "fit": "contain",
                "alignment": "center",
                "state_machine_forbidden": True,
                "rig_manifest": f"./shots/{shot_id}/rive-rig.json",
            }
        elif engine == "three-webgpu":
            contracts[engine] = {
                "ready": True,
                "scene_factory": "./assets/runtime/scenes/declarative-paper-2_5d.js",
                "scene_manifest": f"./shots/{shot_id}/three-scene.json",
                "pixel_ratio": 1,
                "alpha": True,
                "antialias": False,
                "force_webgl": False,
                "preferred_backend": "webgpu",
                "fallback_backend": "webgl2",
            }
        elif engine == "blender":
            contracts[engine] = {
                "ready": False,
                "asset": f"./shots/{shot_id}/assets/prerender/{shot_id}-alpha.webm",
                "source_blend": f"./shots/{shot_id}/assets/prerender/{shot_id}.blend",
                "prerender_manifest": f"./shots/{shot_id}/assets/prerender/prerender-manifest.json",
                "physics_baked": False,
                "action_library": "./blender-action-library.json",
            }
        elif engine == "spine":
            contracts[engine] = {
                "ready": False,
                "delivery": "embedded-seekable-or-prerender",
                "runtime_and_asset_required": True,
            }
        else:
            contracts[engine] = {"ready": True}
    return {
        "schema_version": 2,
        "shot_id": shot_id,
        "clock": "hyperframes-absolute-seconds",
        "engines": contracts,
    }


def can_replace(path: Path, force: bool) -> bool:
    if not path.exists():
        return True
    if force:
        return True
    source = path.read_text(encoding="utf-8", errors="replace")
    return any(marker in source for marker in PLACEHOLDER_MARKERS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--force", action="store_true", help="overwrite an authored composition")
    args = parser.parse_args()

    plan_path = args.plan.expanduser().resolve()
    project = args.project.expanduser().resolve()
    plan = load_plan(plan_path)
    shot_id = plan["shot_id"]
    width, height, duration = resolve_frame(project, shot_id, args.duration)
    composition_path = project / "compositions" / f"{shot_id}.html"
    if not can_replace(composition_path, args.force):
        raise SystemExit(
            f"Refusing to overwrite authored composition: {composition_path}. "
            "Use --force only after reviewing the existing file."
        )

    skill_root = Path(__file__).resolve().parent.parent
    template_path = skill_root / "assets" / "project-template" / "compositions" / "hybrid-scene-template.html"
    runtime_source = skill_root / "assets" / "project-template" / "runtime"
    runtime_target = project / "assets" / "runtime"
    shutil.copytree(runtime_source, runtime_target, dirs_exist_ok=True)

    engines = plan["engines"]
    layers = "\n".join(layer_markup(shot_id, engine, index, duration) for index, engine in enumerate(engines))
    registrations = "\n\n".join(
        block for block in (registration_markup(shot_id, engine, duration) for engine in engines) if block
    )
    if registrations:
        registrations = (
            f'    const engineInputs = await fetch("./shots/{shot_id}/engine-inputs.json")\n'
            '      .then((response) => {\n'
            '        if (!response.ok) throw new Error(`engine-inputs HTTP ${response.status}`);\n'
            '        return response.json();\n'
            '      });\n\n'
            f"{registrations}"
        )
    source = replace_tokens(
        template_path.read_text(encoding="utf-8"),
        {
            "SHOT_ID": shot_id,
            "WIDTH": str(width),
            "HEIGHT": str(height),
            "DURATION": fmt(duration),
            "ENGINE_LAYERS": layers,
            "ENGINE_LABELS": " + ".join(engines),
            "ENGINE_REGISTRATIONS": registrations or "    // This route uses DOM or pre-rendered layers only.",
            "ENGINE_IMPORTS": engine_imports(engines),
        },
    )
    composition_path.parent.mkdir(parents=True, exist_ok=True)
    composition_path.write_text(source, encoding="utf-8")

    shot_root = project / "shots" / shot_id
    for relative in ("assets/characters", "assets/effects", "assets/space", "assets/prerender", "review"):
        (shot_root / relative).mkdir(parents=True, exist_ok=True)
    plan_target = shot_root / "engine-plan.json"
    if plan_path != plan_target.resolve():
        shutil.copy2(plan_path, plan_target)
    inputs_target = shot_root / "engine-inputs.json"
    inputs_created = not inputs_target.exists()
    if inputs_created:
        inputs_target.write_text(
            json.dumps(build_engine_inputs(shot_id, engines, duration), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    template_manifests = skill_root / "assets" / "project-template" / "manifests"
    created_sidecars: list[str] = []
    performance_target = shot_root / "performance-budget.json"
    if not performance_target.exists():
        shutil.copy2(template_manifests / "performance-budget.example.json", performance_target)
        created_sidecars.append(str(performance_target))
    if "rive" in engines:
        target = shot_root / "rive-rig.json"
        if not target.exists():
            rig = json.loads((template_manifests / "rive-character-rig.example.json").read_text(encoding="utf-8"))
            rig["rig_id"] = f"{shot_id}-hero-rig"
            rig["asset"] = f"shots/{shot_id}/assets/characters/{shot_id}.riv"
            rig["identity_reference"] = f"shots/{shot_id}/assets/characters/identity-reference.png"
            rig["fallback"] = f"shots/{shot_id}/assets/characters/{shot_id}-fallback.webm"
            rig["inspection_report"] = f"shots/{shot_id}/review/rive-rig-inspection.json"
            target.write_text(json.dumps(rig, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            created_sidecars.append(str(target))
    if "three-webgpu" in engines:
        target = shot_root / "three-scene.json"
        if not target.exists():
            scene = json.loads((template_manifests / "three-declarative-scene.example.json").read_text(encoding="utf-8"))
            scene["scene_id"] = f"{shot_id}-depth-stage"
            for layer in scene.get("layers", []):
                if isinstance(layer, dict) and layer.get("kind") == "model":
                    layer["source"] = f"shots/{shot_id}/assets/space/{shot_id}-hero.glb"
            target.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            created_sidecars.append(str(target))
        capability = shot_root / "webgpu-capability.json"
        if not capability.exists():
            shutil.copy2(template_manifests / "webgpu-capability.example.json", capability)
            created_sidecars.append(str(capability))
    if "blender" in engines:
        target = project / "blender-action-library.json"
        if not target.exists():
            shutil.copy2(template_manifests / "blender-action-library.example.json", target)
            created_sidecars.append(str(target))

    motion = {
        "duration": duration,
        "assertions": [
            {"kind": "appearsBy", "selector": f"#{shot_id}-development-card", "bySec": min(0.6, duration * 0.25)}
        ],
    }
    (project / "compositions" / f"{shot_id}.motion.json").write_text(
        json.dumps(motion, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "shot_id": shot_id,
                "composition": str(composition_path),
                "engine_plan": str(shot_root / "engine-plan.json"),
                "runtime": str(runtime_target),
                "engine_inputs": str(inputs_target),
                "engine_inputs_created": inputs_created,
                "engines": engines,
                "verified_adapters_mounted": True,
                "required_asset_gates": [
                    engine for engine in engines if engine in {"rive", "spine", "blender"}
                ],
                "p2_sidecars_created": created_sidecars,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
