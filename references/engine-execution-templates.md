# Engine execution templates

Use this reference after an approved `engine-plan.json` has selected one or
more specialized engines. The templates here are executable starting points,
not engine-selection advice; routing policy remains in
`references/hybrid-shot-pipeline.md`.

## 1. What the Skill now automates

| Stage | Automated output | What remains shot-specific |
| --- | --- | --- |
| Route | capability validation and `engine-plan.json` | the truthful capability profile |
| Scaffold | engine canvases/media layers, local runtime tree, imports, adapters, `engine-inputs.json` | approved art, rig names, contact timing, camera/art direction |
| PixiJS | mounted deterministic emitters plus declared paper masks | emitter origin, preset, count, mask, colors, causal timing |
| Rive | strict linear adapter, standard rig manifest, and real WASM asset inspection | production `.riv` rig, weights, identity/contact review, fallback |
| Three.js | WebGPU→WebGL2 renderer plus declarative depth-board/model scene | project plates/models/textures, camera staging, depth and light |
| Blender | modular action primitives, baked rigid-body test, RGBA sequence, VP9-alpha encoder and manifest | project model/rig/simulation and art-directed source scene |
| P2 proof | device backend report, mounted-renderer inventory, total/per-engine p95 report | target-device policy and justified shot budget |
| Proof | unit tests, HyperFrames strict checks and non-sequential snapshot protocol | visual judgment against the shot responsibility |

The remaining work is content authoring, not missing runtime plumbing. A Rive
rig or Blender performance cannot be generated generically without the
approved character identity, action, contact, camera, and exit state. Treat
those inputs as production assets and keep the adapters stable.

## 2. One-time project setup

From the installed Skill directory:

```bash
python3 scripts/init_paper_project.py \
  --manifest /absolute/path/to/story-manifest.json \
  --output /absolute/path/to/my-paper-story
```

Then install the versions pinned by the project template:

```bash
cd /absolute/path/to/my-paper-story
npm ci
```

The generated project pins:

- HyperFrames `0.7.83`;
- GSAP `3.15.0`;
- PixiJS `8.19.0`;
- `@rive-app/canvas-advanced-single` `2.39.1`;
- Three.js `0.185.1`.

Render-critical code and assets are local after installation. The generated
HTML does not load GSAP or an engine runtime from a CDN.

The template commits `package-lock.json`; do not regenerate it independently
per project. For an offline build machine, prepare a portable npm cache once on
a connected machine:

```bash
npm ci --cache /path/to/portable-npm-cache --prefer-offline
```

Then install without network fallback:

```bash
npm ci --offline --cache /path/to/portable-npm-cache
```

Run `npm run doctor` afterward. A missing cache entry is a setup failure, not
permission to fetch an unpinned version or restore a CDN import.

## 3. Route and scaffold one approved shot

```bash
python3 /path/to/paper-animation-director/scripts/route_shot_capabilities.py \
  shots/scene-01/shot-capabilities.json \
  --config hybrid-pipeline.json \
  --output shots/scene-01/engine-plan.json \
  --strict

python3 /path/to/paper-animation-director/scripts/scaffold_hybrid_shot.py \
  --plan shots/scene-01/engine-plan.json \
  --project .
```

The scaffolder creates or updates:

```text
compositions/scene-01.html
compositions/scene-01.motion.json
shots/scene-01/engine-plan.json
shots/scene-01/engine-inputs.json
shots/scene-01/performance-budget.json
shots/scene-01/rive-rig.json                 # when selected
shots/scene-01/three-scene.json              # when selected
shots/scene-01/webgpu-capability.json         # when selected
blender-action-library.json                  # when selected
shots/scene-01/assets/{characters,effects,space,prerender}/
assets/runtime/{adapters,effects,scenes}/
```

It may replace only a known development scaffold unless `--force` is supplied.
It never overwrites an existing `engine-inputs.json`; preserve reviewed asset
names and settings there.

## 4. PixiJS deterministic paper effects

The scaffold mounts
`assets/runtime/adapters/pixi-seekable.js` immediately. Edit the
`pixijs-webgpu.effects` array in the shot’s `engine-inputs.json`:

```json
{
  "id": "hoof-contact-dust",
  "preset": "hoof-dust",
  "seed": "scene-01:hoof-contact-dust",
  "origin": [0.64, 0.78],
  "start": 2.1,
  "duration": 1.4,
  "count": 34,
  "opacity": 0.78
}
```

Available bundled presets are `hoof-dust`, `impact-dust`, `snow`, `embers`,
`ink-motes`, `paper-scraps`, `falling-leaves`, `rain-streaks`, and
`smoke-wisps`. Live mask kinds are `rect`, `circle`, `polygon`, and `band`.
Positions, rotation, scale, color and opacity are derived from
the fixed seed and absolute local time; no ticker or accumulated particle state
is used.

Use the 2D emitter route for flat or multiplane effects. If Three.js already
owns the perspective scene, keep spatial particles in the Three scene instead
of adding a second canvas renderer without a clear reason.

## 5. Rive linear character animation

Export an approved `.riv` file containing a finite linear animation. Place it
at the path declared in `engine-inputs.json`, normally:

```text
shots/scene-01/assets/characters/scene-01.riv
```

Then replace the authored names and open the gate:

```json
{
  "ready": true,
  "asset": "./shots/scene-01/assets/characters/scene-01.riv",
  "artboard": "Character",
  "animation": "walk",
  "playback": "native",
  "animation_duration_seconds": null,
  "fit": "contain",
  "alignment": "center",
  "state_machine_forbidden": true
}
```

The adapter uses the embedded-WASM `canvas-advanced-single` build, recreates
the artboard and animation instance for every absolute sample, advances from
zero to the requested time, and draws exactly one frame. This is intentionally
stricter than resetting only `animation.time`: constraints can otherwise
retain solved state across non-sequential seeks.

Keep the generated `rig_manifest` field and run `inspect_rive_asset.mjs` before
opening the gate. Release matches the actual asset SHA, artboard, and animation
names against that report.

Use `playback: "native"` when the authored Rive animation owns its loop
semantics. `clamp` and `ping-pong` require an author-confirmed
`animation_duration_seconds`. Do not mount an input-history-dependent state
machine as a seekable shot. Pre-render it.

## 6. Three.js WebGPU 2.5D scene

The scaffold mounts a declarative paper scene from:

```text
assets/runtime/scenes/declarative-paper-2_5d.js
shots/scene-01/three-scene.json
```

The adapter uses `WebGPURenderer`, prefers WebGPU, and falls back to its WebGL2
backend only when policy permits. It initializes and compiles the renderer
before registration. Camera, light, plane/shape/model depth layers and motion
are declared in JSON and computed by:

```js
updateAt(localTimeSeconds, globalTimeSeconds)
```

Replace the template scene factory only after preserving its contract:

```js
export async function createShotScene({ THREE, renderer, width, height }) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, width / height, 0.1, 100);

  return {
    scene,
    camera,
    updateAt(localTime, globalTime) {
      // Set every animated camera, object, material, light and uniform from time.
    },
    dispose() {
      // Dispose geometries, materials and textures owned by this scene.
    },
  };
}
```

Do not add `THREE.Clock`, `requestAnimationFrame`, temporal accumulation,
feedback buffers or previous-frame solvers. Bake those effects. Keep pixel
ratio fixed; for strict cutout repeatability the bundled template uses
`antialias: false`.

`build_routed_shot.py --phase verify` also runs a real Three.js backend probe
from `webgpu-capability.json` and writes the result beside the shot review
artifacts.

## 7. Blender baked physical action

For the bundled impact proof or as a starting source scene:

```bash
python3 /path/to/paper-animation-director/scripts/render_blender_prerender.py \
  --output shots/scene-impact/assets/prerender \
  --shot-id scene-impact
```

The command builds and preserves the editable `.blend`, bakes the rigid-body
cache, renders an RGBA PNG sequence, verifies every PNG header and frame count,
encodes `scene-impact-alpha.webm`, probes it, hashes outputs, and writes
`prerender-manifest.json`. The scaffold’s `<video class="clip">` points to that
same filename and HyperFrames owns media seeking.

Before the Blender gate is marked ready, the timed `<video>` uses the bundled
local `pending-blender.webm` so HyperFrames can compile and check the
development project without pretending that the real physics render exists.
Setting `engines.blender.ready` to `true` swaps in the declared per-shot asset.
The placeholder is always a release failure and cannot satisfy
`engine_plan_fulfilled`.

Formal release also requires `source_blend`, `physics_baked: true`, and
`prerender_manifest` in `engine-inputs.json`. The engine-input auditor resolves
all three inside the project and rejects any path containing a pending or
placeholder marker.

The bundled builder proves the pipeline, not the final art. For a real hero
shot, replace the generated geometry and performance while retaining:

- fixed scale, axes, frame rate, camera and color management;
- baked simulation/cache evidence;
- editable `.blend` and external dependencies;
- exact render range and alpha policy;
- manifest hashes and proof frames.

## 8. Verification order

Run the static and unit contracts first:

```bash
python3 scripts/sync_engine_benchmark_runtime.py --check
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Then run the generated project:

```bash
npm run doctor
python3 tools/paper-pipeline/build_routed_shot.py \
  --project . \
  --shot-id scene-01 \
  --phase verify
```

The controller runs the pinned local HyperFrames binary, captures the ordered
and shuffled PNG sets, compares bytes and SHA-256 values per timestamp, and
writes `deterministic-seek-report.json`. It also verifies schema-v2 sidecars,
probes WebGPU when Three.js is selected, and writes
`engine-performance-report.json` from the per-shot budget. The order must not
matter.
This comparison covers the whole composite, including DOM text and GSAP
transforms—not only the specialized engine canvas. If differences are confined
to caption glyphs, remove subpixel transform animation or make the caption
state an explicit pure function of absolute time; do not weaken the comparator.
After deterministic proof, inspect the rendered frames for identity, contact,
occlusion, causal origin, camera, depth, subtitles and the shot’s declared
responsibility. Pixel stability proves reproducibility; it does not prove good
directing.

The runnable reference projects live under:

```text
assets/engine-benchmarks/pixi-paper-effects/
assets/engine-benchmarks/rive-linear-character/
assets/engine-benchmarks/blender-paper-impact/
assets/engine-benchmarks/three-paper-diorama/
```
