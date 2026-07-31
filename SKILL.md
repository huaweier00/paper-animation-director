---
name: paper-animation-director
description: Turn a story, folktale, fable, script, or narration into a historically and physically credible multi-layer paper animation with per-shot capability routing across HyperFrames/GSAP, Rive or Spine, PixiJS, Three.js WebGPU, and Blender; reference-only frontal character identities; shot-specific spatial contracts; just-in-time engine-shaped assets; realistic props and support; narration-driven timing; release gates; voice-stem recovery; and master/social delivery. Use when the user asks for 纸片动画, 剪纸动画, 柔和工笔动画, 宣纸水彩故事, paper-theatre animation, an illustrated folktale, a cultural or historical story film, a layered recurring-character story, or a narrative animation whose identity, direction, objects, space, actions, sound, moral ending, and platform delivery must remain consistent and readable.
---

# Paper Animation Director

Build recurring-character story animation, not a sequence of moving posters. Preserve character identity, real-world plausibility, action meaning, and audio completeness before adding decorative motion.

The production retrospective in `references/production-retrospective.md` is part of this skill, not optional background reading. It captures the spatial, historical, asset, motion, voice, subtitle, preview, and review rules learned from a full paper-shadow production.

For a soft hand-painted, gongbi-style fable, cultural story, or social-platform narrative, also read `references/gongbi-fable-production-retrospective.md`. It captures the end-to-end 《九色鹿》 production, its failed first delivery, its shot-by-shot V2 correction, narration recovery, watermarking, and VMAF-controlled compression.

## Route correctly

- Use this skill for continuous stories with recurring characters, props, causes, actions, and consequences.
- Use `vox-director` instead for editorial collage explainers whose primary unit is a poster-like beat.
- Use the `imagegen` skill for raster asset generation and editing.
- Use `hyperframes`, `hyperframes-core`, `hyperframes-animation`, `hyperframes-keyframes`, `hyperframes-creative`, and `hyperframes-cli` as required by the active production stage.
- Read `references/hybrid-shot-pipeline.md` after approving a shot's animation decision. Use its capability profile and generated engine plan before creating shot assets or authoring a specialized runtime.
- Use `dynamic-video-watermark` for the final moving ownership mark. Do not duplicate its implementation here.

## Non-negotiable rules

1. Treat multilayer animation as separation by depth and physical responsibility, not as permission to cut a person into pieces.
2. Approve exactly one neutral frontal identity reference for each recurring character. Treat it as generation conditioning only: never key, animate, place, or deliver it as a shot asset.
3. Generate no background, pose, gait, prop, effect, ensemble, or full-scene plate before the active shot has an approved semantic event and spatial contract. Lock global art direction early; design concrete assets just in time per shot.
4. Use complete connected character poses by default. Never reconstruct a hero from independently generated head, torso, arms, and legs when seams will be visible.
5. For shared-load or contact-sensitive actions such as carrying, lifting, embracing, rescuing, or handing off a heavy object, use a connected ensemble, integrated full-scene construction, or another approach that preserves believable contact and load. Do not separate participants by default.
6. Choose separation from the shot’s intended visible changes and physical risks. Keep contact-sensitive subjects integrated when separation would damage anatomy, perspective, light, or performance; separate a foreground, actor, prop, rope, water, fire, smoke, shadow, particle, caption, or watermark when independent control materially benefits the shot.
7. For each plot-bearing event the shot is responsible for showing, identify the relevant parts of `cause → action → propagation → result` and a muted visual proof. Do not force every contemplative, atmospheric, reaction, or elliptical shot through all four stages.
8. Lock narration before final timing. Use measured audio duration; do not stretch voice or pad scenes to an arbitrary target.
9. Do not use whole-frame image-to-video as the default animation engine. Keep story-critical characters, captions, and props on deterministic, seek-safe timelines.
10. Do not render a full film before a representative high-risk benchmark passage—long enough to expose the project’s real continuity, physics, timing, performance, and subtitle risks—passes review.
11. Draw and approve a top-down plan plus a camera-facing plan before generating any asset for a shot. Mark floor line, axes, actor start/end zones, facing, paths, clearances, obstacles, semantic targets, occlusions, and subtitle-safe zones.
12. Reject a shot whose action target is semantically wrong or unreachable. A line saying “write on the wall” must identify a writable wall target; a nearby window is not an acceptable substitute.
13. Treat historical accuracy as an adopt/reject contract: every period claim needs a source or explicit rationale, and every tempting later-period prop, floor, roof, stage, costume, or furniture choice must be rejected or justified.
14. Consider a complete full-scene construction when bed, bedding, canopy, character, furniture, perspective, or light contact would be fragile as separate layers. Consider independent complete characters when travel, reaction, pose, occlusion, or timing needs separate control. Choose between them from the shot responsibility and document the tradeoff; neither is the automatic default.
15. A lamp and its flame are one causal unit by default. A character is one connected body by default. A shared lift, restraint, carry, handoff, or embrace is one connected ensemble by default.
16. When the shot is responsible for making physical walking read, do not rely on translation-only tweens. Use a shot- and style-appropriate locomotion solution—such as a normalized complete-body gait cycle, stepped replacement poses, or a deliberately stylized equivalent—with coherent facing, body direction, feet/support behavior, and world-space travel.
17. Make travel vector, head, shoulders, chest, feet, and gaze agree. Treat a left/right mismatch as a failed asset, not a styling issue. Do not mirror or force-fit it unless a documented symmetry, handedness, text, light, contact, and continuity audit explicitly permits mirroring.
18. Do not reuse an existing asset merely because it is available. It is only a candidate and must pass the active shot’s space, scale, period, lighting, orientation, target, contact, and action contract; otherwise regenerate it.
19. Protect the complete head and readable face at all required review times. Reject any unplanned frame edge, `overflow`, crop, mask, matte, foreground, or layer boundary that slices through the scalp, facial contour, eyes, nose, or mouth and creates a half-face or amputated-head effect.
20. Allow partial face/head occlusion only when a visible physical occluder, depth order, time window, narrative reason, and unobstructed identity-proof frame are declared in the shot review contract. Natural profile is not clipping; an unexplained straight cut is.
21. Assign every spoken line to a speaker and an audio stem. Audition for accent as well as tone; reject dialect or identity drift, keep narrator and character dialogue from overlapping, and default Chinese captions to bottom-center safe placement.
22. Every shot must pass three reads: muted visual proof, voice-only speaker/timing proof, and combined picture/sound/subtitle proof. A Studio screenshot is not delivery evidence; review frames from the rendered MP4.
23. Treat “paper animation” as a layering and motion method, not a mandatory surface material. When the user requests soft gongbi, silk-like painting, or restrained hand-painted color, reject heavy fibers, torn white rims, embossed relief, cardboard thickness, curled edges, and paper-pulp grain.
24. Give every narrated or story-critical object a recognizability contract: real-world class, silhouette, proportion, material, attachment/support, applicable state changes, and proof. Reject arrows that become direction lines, grass that floats without roots, gold that reads as an abstract pile, or notices that read as placeholder icons.
25. Keep every standing actor, animal, wheel, vehicle, and placed prop attached to a declared support surface. Review feet, hooves, wheels, shadows, overlap, and scale at the first, midpoint, proof, and final frames. A guide “in front of the procession” must stand on the road, not above the horse or scenery.
26. When a shot is responsible for showing the effect of a command, treat it as a state transition rather than omitted narration. For example, an order to lower weapons may use `aimed → command/gesture → visibly lowered → safe final state`, or another staging that makes compliance unmistakable. If the command is intentionally off-screen or elliptical, make its consequence legible elsewhere.
27. Release exactly one shot at a time. Do not generate, animate, or approve the next shot until the current rendered MP4 passes semantic, realism, spatial, identity, audio, caption, and technical review. A visually attractive draft is not an approval.
28. Design the ending before production. Require consequence, cultural/source closure when relevant, and a concise transferable lesson. Do not let the film end on an information card that explains provenance but fails to complete the emotional or educational argument.
29. Preserve a voice ledger and dry voice stems independently of music. Before delivery, prove every expected line exists at its locked time and speaker. If narration is lost from a music-backed render, restore the approved stems onto the unchanged timeline rather than regenerating performances or retiming the film.
30. Preserve the archival master, watermarked master, and compressed social derivative as separate files. Verify the social file by full decode, technical probing, rendered-frame review, and a VMAF floor normally set to 95; never overwrite the master.
31. Do not impose universal quotas for shot duration, layer count, pose count, state count, camera movement, or cut frequency. These are directing decisions. Choose them from the shot’s narrative responsibility, physical relationships, rhythm, visual style, and production risk.
32. Before generating assets, declare what the shot is responsible for making the audience perceive and what visible change, if any, is needed to fulfil that responsibility. A still or nearly still tableau may be exactly right for an establishing view, revelation, dread, reflection, pause, icon-like illustration, or deliberate off-screen/elliptical action.
33. Do not claim that a plot-bearing visible action has been proved when the rendered evidence is only a whole-frame transform, camera move, text change, or decorative motion. Those devices are valid directing tools; they are insufficient only when the shot itself is responsible for showing an action they do not show.
34. Choose the animation architecture shot by shot: independently moving paper actors or props, a connected ensemble, a full-scene state change, a single tableau with selective local motion, a deliberate still, or a justified combination. Preserve contact and perspective where separation would damage them; separate elements only where independent change benefits the shot.
35. Compare later shots with the benchmark by comparable narrative demand, not by raw complexity. A quieter shot may intentionally use fewer layers or less motion. Flag only an unexplained downgrade where a shot with similar action, contact, or continuity demands no longer provides equivalent clarity.
36. Split or combine shots according to clarity, continuity, rhythm, and staging. Split when one composition cannot carry its responsibilities without flattening the event; keep a longer continuous shot when sustained space, stillness, or performance is the stronger choice.
37. Record the directing choice in `animation-decision.json` and review the rendered MP4 against that declared choice. The review is a contradiction check, not a formula for art direction.
38. Route every production shot through `shot-capabilities.json` and a generated `engine-plan.json` after the directing decision and before asset generation. Record objective capability needs first; do not choose an engine by fashion or convenience.
39. Keep HyperFrames as the final orchestrator unless the user explicitly changes the delivery framework. Let specialized engines own only their declared character, effects, spatial, or pre-render layer.
40. Use the least complex engine set that can prove the shot. Keep a credible still, rigid layer, stepped pose, or multiplane shot in GSAP/DOM when it fulfils the responsibility; do not add Rive, PixiJS, Three.js, or Blender as decoration.
41. Require absolute-time seeking, local assets, fixed dimensions, and seeded randomness for embedded runtimes. Pre-render any state machine, feedback effect, physics, cloth, hair, collision, or simulation whose state depends on earlier frames.
42. Shape asset generation to the accepted engine plan: rig-ready separated or mesh art for Rive/Spine, deterministic textures and emitter data for PixiJS, depth/model/camera assets for Three.js, and editable sources plus baked caches for Blender.
43. Prove each specialized engine with one representative benchmark before using it across the film. A benchmark must prove the selected capability and non-sequential seek stability, not merely that a canvas or asset loads.
44. Route production through `build_routed_shot.py`. Before formal release, audit `engine-inputs.json` against the generated plan, reject every pending engine gate and runtime-network asset, and reject Blender placeholder media even when the composition can display it during development.
45. Install JavaScript dependencies from the committed `package-lock.json`. Keep exact versions, use the project-local HyperFrames binary, and never let verification silently fall back to an online `npx` fetch.
46. Treat DOM and GSAP layers as seek-sensitive too. For rasterized text, avoid transform-based entrance motion unless ordered/shuffled capture proves byte stability; prefer an explicit time-zero baseline and opacity-only caption transitions when subpixel transforms retain seek history.
47. Treat `engine-inputs.json` schema version 2 as a sidecar contract, not only a renderer list. Every specialized route must point to its engine-specific manifest, and every embedded-renderer shot must carry a reviewed `performance-budget.json`.
48. Inspect every ready Rive `.riv` file with the project-local WASM runtime before release. Match the current asset SHA-256, artboard, and every selected linear animation; never infer those names from a filename or accept a state machine as the absolute-time release path.
49. Drive Three.js 2.5D shots from a declarative scene manifest with explicit camera, light, layer kind, depth, material, motion, and occlusion order. Keep optional models replaceable without breaking the depth-board scene, and reject previous-frame effects.
50. Declare PixiJS paper masks by stable id and attach effects to those ids. Use only deterministic live masks; pre-render an inverted, feedback, displacement-history, or otherwise stateful mask that cannot be reconstructed from absolute time.
51. Probe WebGPU with a real Three.js render on the intended build device. Record the actual backend and adapter limits; allow WebGL2 only when the shot’s `webgpu-capability.json` explicitly declares that fallback.
52. Build Blender physics shots from reusable action primitives, but preserve shot-specific art direction. A valid library does not replace the editable `.blend`, baked cache, build record, transparent master, or final composite review.
53. Measure the mounted renderer set at declared proof times under a per-shot performance budget. Block release when a selected embedded renderer is missing, renderer count exceeds the budget, or total/per-engine p95 exceeds its ceiling.
54. Keep P2 gates inside `build_routed_shot.py`. A separate successful probe, screenshot, or benchmark does not waive a failing controller step; fix the gate and rerun the same phase.
55. When using Fish Audio S2.1 Pro, derive concise square-bracket performance cues from the line's context and place them where the delivery changes. Do not constrain cues to a fixed vocabulary, treat 《九色鹿》 tag strings as a universal preset, or overload short lines with competing directions.
56. Treat Fish Audio pauses as expressive and non-deterministic. Prefer an explicit short/normal/long pause cue for performance; never assume repeated pause cues add a predictable duration. Split clauses and insert measured silence in the audio timeline whenever the picture requires an exact pause.
57. Do not assign one global speech speed to a film, role, or voice. Establish a voice-specific audition baseline, then choose and record segment-level speed from context, information density, physical state, emotional transition, and dramatic function. Use inline cues or separate requests for within-line changes, and fit picture to the selected measured performance.

## Workflow

### 0. Run the retrospective and production intake

Read `references/production-retrospective.md` before designing a new historical, cultural, or recurring-character paper story. For soft gongbi or social-platform fables, read `references/gongbi-fable-production-retrospective.md` as well. Record the project’s aspect-ratio decision, surface-style decision, historical evidence tier, adopt/reject list, spatial plan, asset architecture, voice policy, ending contract, proof frames, and approval gates. Treat “looks nice” as insufficient evidence for a scene, asset, motion, or prop choice.

### 1. Create the story contract

Read `references/story-and-beat-design.md` and the retrospective’s “visible event” rules. Convert the source into `story-manifest.json`; start from `assets/project-template/manifests/story-manifest.example.json`. Lock the platform, aspect ratio, first-three-second hook, ending argument, and source/copyright boundary before generation.

Require each scene to contain a narrative goal. For plot-bearing events, record the applicable parts of `cause`, `action`, `propagation`, `result`, and `proof`; a non-applicable or deliberately omitted part needs a directing rationale rather than invented activity. Validate before generating assets:

```bash
python3 scripts/validate_story_manifest.py story-manifest.json --strict
```

Obtain approval for the story action table before expensive generation.

### 2. Lock voice, speaker ownership, and timing

Read `references/voice-timing-and-subtitles.md`. When using Fish Audio
S2.1 Pro, also read `references/fish-audio-s2.1-pro-production.md` and start
the project's voice-direction ledger from
`assets/project-template/manifests/voice-direction.example.json`. Audition
multiple voices per role—typically 3–5, or more when the market is
inconsistent—with representative material that tests neutral narration,
contextual emotion, local emphasis, short/long pauses, endings, accent, and
response to speed changes. Search the Fish Audio public model market broadly,
retain public model IDs and URLs, and reject celebrity imitation, dialect
drift, advertising cadence, unclear diction, or a voice that cannot follow
the story's required directions.

Assign every line to a speaker and analyze its dramatic function before
synthesis. Generate an untagged baseline, then concise context-derived cue
variants; begin with one primary direction and add a physical, tonal, pause,
or emphasis cue only when audition evidence requires it. Establish a
voice-specific speed baseline during casting, but choose formal
`prosody.speed` per line or semantic beat rather than copying one value across
the film. Split requests when the same line requires a material speed or
emotional transition. Preserve the raw text, annotated text, speed rationale,
API parameters, selected take, measured duration, voice ledger, and original
dry stems. Never store credentials in the project or skill.

Probe delivered audio:

```bash
python3 scripts/probe_voice_timing.py assets/audio/*.mp3 --output voice-manifest.json
```

Write measured durations and audio paths back to the story manifest before building the full timeline.

### 3. Lock reference-only character identities

Read `references/character-and-pose-system.md` and `references/image-generation-prompts.md`. Generate one neutral frontal, preferably full-body identity image for each recurring character and record stable traits plus forbidden changes. Mark the image `purpose: identity-consistency-reference-only` and `animation_use: false`. Obtain approval before producing the benchmark shot.

Do not generate side views, gait cycles, expressions, action poses, chroma atlases, props, backgrounds, or effects at this stage. Do not place the frontal identity image in the animation. It exists only to condition later shot-specific generation.

### 4. Plan and generate one shot at a time

Treat each `scene` entry in the manifest as a story unit, not an automatic one-shot instruction. Decide whether it should remain one continuous shot or become several shots from narrative clarity, spatial continuity, performance, and rhythm. Read `references/shot-spatial-contract.md`, then write and approve the chosen shot’s semantic event, top-down plan, camera-facing plan, and `spatial_contract`.

Before generation, prove:

- start and end zones fit inside the frame and intended motion corridor;
- the corridor remains clear of non-passable obstacles and is wide enough for the actor or shared load;
- travel vector, facing, gaze, camera side, entry, and exit agree;
- every action target exists, supports the narrated action, is reachable, and stays readable;
- the background reserves the path, target, proof frame, head/face-safe region, and subtitle-safe zones;
- `review_contract` protects head and face and declares every intentional occlusion.

Only after `asset_plan.space_approved: true`, list the assets justified by that shot and generate them using the approved frontal identity reference. For every critical prop, write its real-world class, silhouette, scale reference, material cues, support/attachment points, intended change when applicable, and proof frame before generation. Consider a connected ensemble for coupled actors and a shared load. Consider a full-scene state or tableau when contact, perspective, light, or stillness would be damaged by separation. Keep backgrounds free of characters, text, watermarks, and story-critical effects unless the approved shot architecture deliberately keeps them together.

Before any asset prompt, read `references/animation-direction-framework.md`, create the shot’s `animation-decision.json`, and run:

```bash
python3 scripts/review_animation_decision.py shots/scene-xx/animation-decision.json --phase planning
```

This review checks whether the proposed visual evidence matches the declared shot responsibility. It must not reject a choice merely because it is still, long, uses a single plate, uses few layers, or differs in complexity from another shot. It must reject a claim that an unfolding action is visible when the plan contains no credible visible change and no deliberate elliptical or off-screen treatment.

After the animation decision passes, read `references/hybrid-shot-pipeline.md`. Create `shot-capabilities.json` from the bundled example, then generate and review the engine plan:

```bash
python3 scripts/route_shot_capabilities.py \
  shots/scene-xx/shot-capabilities.json \
  --config hybrid-pipeline.json \
  --output shots/scene-xx/engine-plan.json \
  --strict
```

Do not generate assets until the selected engine roles, integration modes, fallbacks, asset requirements, benchmark requirement, and proof requirements agree with the directing and spatial contracts.

Do not ask an image model to improvise important writing, official notices, maps, currency, treasure, weapons, plants, or symbolic connectors. Generate a historically credible blank base when needed, then typeset or composite verified content deterministically. Reject graphic shorthand that cannot be recognized with sound muted.

Prepare shot-specific atlases and keyed assets only after that gate:

```bash
python3 scripts/remove_chroma_key.py atlas-magenta.png atlas-alpha.png --key-color '#ff00ff'
python3 scripts/split_pose_atlas.py atlas-alpha.png poses --cols 3 --rows 2 --trim --padding 16
python3 scripts/audit_asset_integrity.py poses --kind character --strict
```

Reject and regenerate assets that fail identity, orientation, camera, scale, light, contact, target, crop, or semantics. Never force a wrong-direction asset into the timeline because it already exists.

### 5. Prove the benchmark shot

Choose a representative high-risk passage with difficult contact, shared load, water, fire, destruction, handoff, subtle acting, or deliberate stillness. Build only enough of it to prove the project’s hardest directing and technical decisions before expanding. It must prove:

- stable character identity and complete heads, hands, and feet;
- no half-face, sliced scalp, or amputated-head effect at first, midpoint, pose-change, occlusion-boundary, proof, and transition frames;
- correct hand/shoulder/prop contact;
- the intended action, condition, reaction, reveal, or stillness reads without relying on an explanatory caption;
- purposeful depth and physical separation where the scene benefits from them, without splitting connected subjects merely to increase layer count;
- correct container masks, prop ownership, and effect origins;
- narration, subtitle, and transition timing.
- muted proof of the event chain and a voice-only check for speaker ownership, accent, and overlap.
- the visible change—or intentional stillness—declared in `animation-decision.json`;
- a rendered responsibility review showing that the shot does what it claims to do.

Do not expand to the full film until this benchmark is approved. Record its directing logic, asset architecture, physical risks, and proof method as a reference—not a complexity quota. Afterward, keep the same gate for every shot: contract → animation decision → justified assets → animation → rendered MP4 → responsibility review → muted/voice/combined/reality review → release record → next shot. Compare shots with similar narrative and physical demands; permit intentional variation in stillness, density, duration, and technique.

### 6. Build the deterministic project

Read `references/layers-physics-and-occlusion.md`,
`references/hyperframes-production.md`, and
`references/engine-execution-templates.md`. Scaffold a generic project:

```bash
python3 scripts/init_paper_project.py --manifest story-manifest.json --output ./my-paper-story
```

Rebuild only the generic scene hosts and timing skeleton when the manifest changes:

```bash
python3 scripts/build_hyperframes_timeline.py --manifest story-manifest.json --project ./my-paper-story
```

For an approved routed shot, scaffold the selected engine layers:

```bash
python3 scripts/scaffold_hybrid_shot.py \
  --plan shots/scene-xx/engine-plan.json \
  --project ./my-paper-story
```

Prefer the guarded one-command controller for production work:

```bash
python3 scripts/build_routed_shot.py \
  --project ./my-paper-story \
  --shot-id scene-xx \
  --phase prepare
```

After authoring the real engine assets and composition, run `--phase verify`.
After the rendered MP4, proof frames, voice checks, and release record are
complete, run `--phase release`. The controller rechecks plan drift, audits
engine inputs, runs the offline doctor, runs HyperFrames check, captures
ordered/shuffled seek evidence, and enforces both release reviewers.

The scaffold is a runnable development composition, not an approved shot. It
mounts the verified PixiJS and Three.js templates immediately and wires the
strict Rive adapter behind an explicit `.riv` asset gate; Blender is a seekable
pre-render layer behind its baked-media gate. Configure the generated
`engine-inputs.json`, replace template art with the approved engine-shaped
assets, and clear all required-asset gates before review. Keep audio as direct
children of the top-level composition root. Give each shot an
`animation-decision.json`, `shot-capabilities.json`, `engine-plan.json`, and
`engine-inputs.json`; add motion sidecars and selectors for observable story
evidence.

### 7. Animate physical relationships and normalized movement

Read `references/semantic-action-checks.md` and `references/animation-direction-framework.md`. For every moving prop, define ownership and lifecycle as far as the shot needs it: `source → owner → handoff → target → exit/rest`. For every standing or walking subject, declare the support surface and review feet/hooves/wheels/contact shadows against it. When a shot needs walking to read as physical travel, use a complete-body gait or another stylistically coherent locomotion solution and check feet baseline, support, facing, torso direction, and world-space travel. For water, fire, impact, breakage, light, shadow, weapons, plants, documents, treasure, and load, show the cause and feedback needed for the intended read.

Camera moves, whole-frame transforms, background drift, focus changes, grain, captions, and graphic marks may be the right visual language for a shot. Judge them against the declared responsibility. They can carry attention, time, mood, reveal, or transition; do not use them as false evidence that a character, prop, contact, or physical consequence visibly changed.

### 8. Fit picture to narration

Run the pacing audit after scene timing and activity windows are present:

```bash
python3 scripts/audit_pacing.py story-manifest.json --voice-manifest voice-manifest.json --output PACE-AUDIT.md --strict
```

Cut after semantic completion when the remaining duration no longer contributes performance, thought, atmosphere, sound, suspense, or transition. Hold longer when duration is the point; cut sooner when the beat has already landed. Do not let paper grain, dust, or slow parallax disguise an unintentionally empty interval.

### 9. Pass the quality gates

Read `references/quality-gates-and-delivery.md` and the retrospective’s three-read review. Pass in order:

- P0 semantic clarity and required-object recognizability;
- P1 identity, real-world proportion, ground/support contact, occlusion, and physical continuity;
- P2 motion, voice, captions, pacing, and transitions;
- P3 HyperFrames checks, final-MP4 frame review, expected-line/audio-stem audit, watermark, and delivery.

Add a project-specific failure log when a preview exposes a wrong spatial relation, character drift, dialect, caption occlusion, or stale-cache problem. Convert each repeated failure into a rule or a new manifest field before continuing.

Create one shot-release record from `assets/project-template/manifests/shot-release.example.json`, then enforce the next-shot lock:

```bash
python3 scripts/build_routed_shot.py \
  --project . \
  --shot-id scene-xx \
  --phase release
```

The release record must point to the rendered MP4, relevant proof frames,
critical-prop specifications, expected voice lines, directing decision,
capability profile, generated plan, and audited engine inputs. Do not start the
next shot until the controller passes.

Inspect head and face regions at enlarged scale in frames extracted from the rendered MP4. Distinguish a natural side/profile view from clipping: profile preserves a coherent skull and facial contour; clipping introduces a frame-, mask-, container-, or foreground-shaped cut. Fix z-order, overflow, mask path, crop, actor position, camera, or source asset before approval.

Create a contact sheet from proof times or explicit review times:

```bash
python3 scripts/make_review_contact_sheet.py --video final.mp4 --manifest story-manifest.json --output review.jpg
```

Always review frames extracted from the rendered MP4; a correct Studio preview alone is not delivery proof.

### 10. Deliver master, social version, and publishing package

After final preview approval, render the high-quality master. Verify the expected voice-line ledger against the final mix before applying music-only or platform-specific replacements. Apply the reusable moving watermark when requested. Then make a separate H.264 social upload while preserving the master:

```bash
python3 scripts/encode_social_delivery.py master.mp4 social-1080p.mp4 --vmaf-floor 95
```

Report master and social paths, sizes, duration, resolution, frame rate, audio streams, watermark settings, compression ratio, and VMAF. Never overwrite the master. For social publication, also provide several title options, a culturally grounded description, and an interactive pinned comment that invites a meaningful response without weakening the film’s final lesson.

## Resource map

- Story structure and timing policy: `references/story-and-beat-design.md`
- Project retrospective, historical/spatial rules, asset decisions, gait, voice, captions, preview, and failure patterns: `references/production-retrospective.md`
- Soft gongbi fable workflow, 《九色鹿》 V1/V2 failures, realistic-prop gates, voice recovery, ending design, watermarking, and compression: `references/gongbi-fable-production-retrospective.md`
- Character continuity and ensemble poses: `references/character-and-pose-system.md`
- Shot coordinates, motion corridors, direction, obstacles, action targets, continuity, and asset gates: `references/shot-spatial-contract.md`
- Image-generation prompt contracts: `references/image-generation-prompts.md`
- Layering, masks, water, fire, rope, and load: `references/layers-physics-and-occlusion.md`
- Voice auditions, measured timing, subtitles, and titles: `references/voice-timing-and-subtitles.md`
- Fish Audio S2.1 Pro natural-language cue semantics, contextual speed direction, pause policy, audition matrix, API baseline, and acceptance gates: `references/fish-audio-s2.1-pro-production.md`
- Contextual Fish Audio line-direction ledger: `assets/project-template/manifests/voice-direction.example.json`
- HyperFrames project and timeline contract: `references/hyperframes-production.md`
- Semantic proof and action-specific checks: `references/semantic-action-checks.md`
- Context-sensitive shot architecture, intentional stillness, visual-evidence review, and benchmark comparison: `references/animation-direction-framework.md`
- Capability vocabulary, engine routing, deterministic integration, new-project commands, engine build contracts, benchmarks, and migration: `references/hybrid-shot-pipeline.md`
- Executable PixiJS, Rive, Blender, and Three.js templates; pinned versions;
  asset gates; scaffolding outputs; and deterministic verification commands:
  `references/engine-execution-templates.md`
- P2 standard Rive rig contract, declarative Three.js depth board, Blender
  action library, PixiJS masks/effects, WebGPU device probe, and multi-engine
  performance budget: `references/p2-engine-capabilities.md`
- Animation decision sidecar example: `assets/project-template/manifests/animation-decision.example.json`
- Shot capability example: `assets/project-template/manifests/shot-capabilities.example.json`
- Generated engine-plan example: `assets/project-template/manifests/engine-plan.example.json`
- P0–P3 acceptance and delivery: `references/quality-gates-and-delivery.md`
- Per-shot release template: `assets/project-template/manifests/shot-release.example.json`
- One-command routed shot controller: `scripts/build_routed_shot.py`
- Engine-input development/release audit: `scripts/audit_engine_inputs.py`
- Ordered/shuffled seek proof: `scripts/verify_deterministic_seek.py`
- Offline environment and lock doctor: `scripts/doctor_paper_pipeline.py`

## Delivery posture

Preserve the editable project, reference-only frontal identity images, per-shot spatial contracts, approved shot asset sidecars, approved voice files, source atlases, alpha assets, high-quality master, and social derivative. Treat generated social files as disposable derivatives and the master as the archival source.
