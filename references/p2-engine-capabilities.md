# P2 engine capability contracts

Use this reference after `engine-plan.json` has selected a specialized engine.
P2 turns engine templates into auditable production contracts. It does not
pretend that a generic rig, model, physical performance, or effect is the final
shot content.

## 1. What a new project receives

`init_paper_project.py` copies the runtime, example manifests, and portable
pipeline commands into the project. `scaffold_hybrid_shot.py` then creates
schema-version-2 `engine-inputs.json` and only the sidecars required by the
accepted route:

```text
shots/<shot-id>/engine-inputs.json
shots/<shot-id>/performance-budget.json
shots/<shot-id>/rive-rig.json                 # when Rive is selected
shots/<shot-id>/three-scene.json              # when Three.js is selected
shots/<shot-id>/webgpu-capability.json         # when Three.js is selected
blender-action-library.json                    # when Blender is selected
```

The scaffolder never turns a missing Rive or Blender production asset into a
ready asset. Their gates remain false until the actual authored files and
release evidence exist. PixiJS and the declarative Three.js depth-board
template can mount immediately because they have complete deterministic local
runtime implementations.

Run the normal controller:

```bash
python3 tools/paper-pipeline/build_routed_shot.py \
  --project . \
  --shot-id scene-01 \
  --phase prepare

python3 tools/paper-pipeline/build_routed_shot.py \
  --project . \
  --shot-id scene-01 \
  --phase verify
```

Do not manually skip from one P2 tool to the next. The controller resolves the
selected route and invokes only the applicable audits, device probe, and
performance profile.

## 2. Standard Rive character rig

`rive-rig.json` separates the stable production contract from the shot’s
single selected animation:

- `profile`: `benchmark-linear` or `production-hero`;
- current local `.riv` asset;
- stable rig id and approved identity reference;
- exact artboard;
- named linear animations with playback and duration policy;
- stable root, head, hand, and foot anchors for a production hero;
- authored facings;
- deterministic fallback pre-render;
- runtime inspection report.

Inspect the real file through Chrome and Rive’s project-local WASM runtime:

```bash
node tools/paper-pipeline/inspect_rive_asset.mjs \
  --project . \
  --asset shots/scene-01/assets/characters/scene-01.riv \
  --runtime node_modules/@rive-app/canvas-advanced-single/canvas_advanced_single.mjs \
  --output shots/scene-01/review/rive-rig-inspection.json
```

Then audit it:

```bash
python3 tools/paper-pipeline/audit_rive_rig.py \
  shots/scene-01/rive-rig.json \
  --project . \
  --phase release
```

The audit matches asset SHA-256, artboard, and every declared animation against
the runtime inspection. `state_machine_forbidden` must remain true for the
embedded seekable release path. If the authored performance needs an input
history state machine, render it to a local deterministic fallback instead.

The bundled Centaur asset proves that real `.riv` inspection and absolute-time
linear playback work. It is a benchmark asset, not the visual identity or
production rig for a new protagonist.

## 3. Declarative Three.js 2.5D scene

`three-scene.json` is the scene source of truth. It declares:

- perspective or orthographic camera;
- local units, near/far planes, position, and look-at;
- ambient and directional lights;
- `plane`, `shape`, and optional `model` layers;
- one explicit depth per layer;
- material color, roughness, opacity, size, position, and scale;
- deterministic `static`, `parallax`, `bob`, or `sway` motion;
- complete back-to-front `occlusion_order`;
- local-assets-only and previous-frame-effect bans.

The scaffold fetches the manifest and mounts
`createDeclarativePaperScene()`. An optional missing model may be omitted during
development while the depth-board scene remains usable; a required production
model must exist for release.

Audit:

```bash
python3 tools/paper-pipeline/audit_three_scene.py \
  shots/scene-01/three-scene.json \
  --project . \
  --phase release
```

Use the manifest for camera/depth/content changes. Modify the runtime factory
only when the manifest vocabulary cannot express a required capability.

## 4. Blender modular physics actions

`blender-action-library.json` defines reusable paper-physics roles and
parameters. The bundled Python library provides active/passive rigid bodies,
planar constraints, hinge constraints, and rigid-body world configuration.
Current templates include:

- `rigid-drop`;
- `paper-impact`;
- `hinged-swing`.

Audit the library:

```bash
python3 tools/paper-pipeline/audit_blender_action_library.py \
  blender-action-library.json
```

The real Blender builder imports these primitives, saves the editable
`.blend`, bakes the cache, records proof transforms, and renders RGBA frames.
Deprecation warnings from a newer Blender version are not a release failure;
missing imports, unbaked physics, absent frames, or a false build record are.

The library standardizes mechanics, not performance. A hero fall, cloth
reaction, water collision, or breakage shot still needs its approved model,
camera, action, scale, material, contact, and exit state.

## 5. PixiJS paper effects and masks

Bundled deterministic presets:

```text
hoof-dust
impact-dust
snow
embers
ink-motes
paper-scraps
falling-leaves
rain-streaks
smoke-wisps
```

Bundled live mask kinds:

```text
rect
circle
polygon
band
```

Declare masks once and reference them by id from effects:

```json
{
  "masks": [
    {
      "id": "ground-contact-zone",
      "kind": "band",
      "origin": [0, 0.58],
      "size": [1, 0.42],
      "invert": false
    }
  ],
  "effects": [
    {
      "id": "impact-scraps",
      "preset": "paper-scraps",
      "seed": "scene-01:impact-scraps",
      "origin": [0.55, 0.74],
      "start": 1.2,
      "duration": 1.6,
      "count": 36,
      "opacity": 0.8,
      "mask": "ground-contact-zone"
    }
  ]
}
```

An unknown mask id fails the engine-input audit. Inverted live masks are
rejected because a reliable complement mask needs a reviewed pre-render or a
more explicit bounded implementation.

## 6. WebGPU real-device gate

`webgpu-capability.json` declares whether WebGPU is mandatory or whether a
WebGL2 fallback is accepted. The release probe opens the project-local Chrome,
imports the pinned Three.js WebGPU build, initializes a renderer, renders a
real plane, and records:

- `navigator.gpu` availability;
- actual Three.js backend;
- adapter information exposed by the browser;
- `maxTextureDimension2D`;
- `maxBindGroups`;
- required backend and pass/fail.

Manual diagnostic form:

```bash
node tools/paper-pipeline/probe_webgpu_runtime.mjs \
  --project . \
  --required-backend webgpu \
  --output shots/scene-01/review/webgpu-capability-report.json
```

The controller chooses `webgpu` when the policy requires it and `any` when the
declared WebGL2 fallback is acceptable.

## 7. Multi-engine performance budget

`performance-budget.json` controls:

- viewport profile;
- warmup and measured iterations;
- maximum mounted renderers;
- total p95 render-call time;
- per-engine p95 thresholds;
- whether a missing selected renderer blocks release.

The profiler opens an instrumented flattened form of the real HyperFrames
composition, waits for the selected adapters to mount, and samples their
`renderAt()` calls at the shot’s review times. It writes:

```text
shots/<shot-id>/review/engine-performance-report.json
```

This is deterministic render-call instrumentation, not a claim about final
video encoding speed or every GPU pipeline stall. Use it to prevent silent
renderer loss and large per-shot regressions. Use HyperFrames render benchmarks
and platform profiling when end-to-end throughput or device-class coverage is
the decision.

## 8. What the controller blocks

For schema-version-2 shots, `prepare`, `verify`, and `release` add the following
route-aware gates:

| Selected capability | Development | Verify/release |
| --- | --- | --- |
| Rive ready asset | rig contract; inspection warning allowed | matching inspection report and current asset SHA required |
| Three.js | scene-manifest audit | release scene audit plus real-device backend probe |
| Blender ready asset | action-library contract | library, editable source, bake, pre-render and manifest gates |
| PixiJS | masks, presets, seeds and bounds | same contract with no pending assets |
| Any embedded renderer | budget sidecar present | mounted-renderer inventory and p95 budget pass |

The environment doctor also checks schema-v2 sidecar completeness. A legacy
schema-version-1 shot remains supported and does not acquire P2 gates until it
is intentionally migrated or re-scaffolded.

## 9. Failure policy

- Fix a runtime inspection mismatch by correcting the manifest or asset; never
  edit the report hash.
- Fix an occlusion-order failure in `three-scene.json`; never compensate with
  undocumented z offsets in the adapter.
- Fix a missing Blender import or bake in the source builder and rerun it.
- Fix a performance timeout by confirming that the real HyperFrames
  composition mounts the selected adapter; do not record a zero-renderer pass.
- Raise a performance ceiling only after measuring the target device and
  documenting why the shot legitimately needs the larger budget.
