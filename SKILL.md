---
name: paper-animation-director
description: Direct and produce premium story-led paper, cutout, soft-gongbi, watercolor, or paper-theatre animation from script through animatic, production design, character model packs, sequence layout, shot assets, performance animation, deterministic multi-engine rendering, evidence-bound review, and master/social delivery. Use for 纸片动画, 剪纸动画, 工笔动画, 宣纸水彩故事, illustrated folktales, historical or cultural story films, recurring-character narrative animation, and premium social story animation where identity, orientation, acting, physical contact, art direction, sound, editorial value, and release quality must remain coherent.
---

# Paper Animation Director

Direct a film, not a pile of generated illustrations. Prove the story and performance cheaply; spend production effort only after timing, staging, visual language, and physical relationships work. Trust rendered evidence tied to exact files, not prompts, filenames, source-code intent, or self-declared `pass` fields.

## Route and load only what the stage needs

Use this skill for continuous narrative with recurring characters, spatial action, causes, and consequences. Use `vox-director` for editorial collage explainers. Use `imagegen` for raster generation/editing. For implementation or rendering, also load the mandatory `hyperframes` entry skill and its stage-specific references. Use `dynamic-video-watermark` only at delivery when requested.

Read these references on demand:

| Need | Required reference |
|---|---|
| production order, asset classes, WIP, automation | `references/production-architecture.md` |
| story/edit/timing | `references/story-and-beat-design.md` |
| Douyin/Reels/Shorts | `references/social-premium-production.md` |
| narrative short-drama mode, eight-second hook, anti-PPT staging | `references/v5-short-drama-production.md` |
| premium look development and asset curation | `references/visual-art-direction-and-asset-quality.md` |
| character identity, model pack, pose, rig, ensemble | `references/character-and-pose-system.md` |
| spatial layout and action targets | `references/shot-spatial-contract.md` |
| acting, timing, weight, locomotion, camera | `references/performance-and-motion-direction.md` |
| asset facts, motion contract, rendered evidence | `references/motion-integrity.md` |
| animation architecture decision | `references/animation-direction-framework.md` |
| engine routing and deterministic integration | `references/hybrid-shot-pipeline.md` |
| layer physics, effects, contact, occlusion | `references/layers-physics-and-occlusion.md` |
| prompts and generated-asset rejection | `references/image-generation-prompts.md` |
| voice, timing, subtitles | `references/voice-timing-and-subtitles.md` |
| acceptance and delivery | `references/quality-gates-and-delivery.md` |

Read `references/production-retrospective.md` when diagnosing a production failure or making a historical paper-shadow film. Also read `references/gongbi-fable-production-retrospective.md` for soft-gongbi cultural fables. These are case evidence, not a universal shot recipe.

## Production kernel

These invariants govern every route:

1. **Rendered evidence outranks declarations.** Bind reviews to hashes of source assets, contracts, render, and extracted proof frames. Upstream changes invalidate downstream approval.
2. **Editorial proof precedes production art.** A complete disposable animatic must work muted, audio-only, and combined before formal voice, production assets, or expensive engine work.
3. **Directing precedes tooling.** Declare the shot’s audience-facing responsibility, performance intention, visible change or intentional stillness, and proof moment before selecting an engine.
4. **Sequence continuity precedes shot polish.** Approve adjacent-shot geography, camera axis, floor line, screen direction, scale, light, entry/exit, timing, and eye trace before final assets.
5. **Reference design is not production media.** Use a canonical identity anchor plus a controlled reference-only model pack after animatic/style lock. Never animate those references; create or approve separate shot assets.
6. **Physical facts are explicit.** Asset facts record observed orientation, forward axis, asymmetry, support/contact, mirror policy, display-scale limits, and content hash. A filename such as `rabbit-right.png` proves nothing.
7. **Motion is compiled from a contract.** Travel vector, expected/rendered facing, active window, selector, engine, support, contact, and proof times have one owner. Do not retype them independently in prompts, JSON, CSS, and GSAP.
8. **Performance is primary motion.** Stage intention, anticipation, action, contact, settle, and reaction as needed. Do not use camera drift, whole-layer translation, particles, or transitions as false evidence of character action.
9. **Contact-sensitive units stay coherent.** Prefer complete connected poses, integrated ensembles, or full-scene states when separation would damage anatomy, load, perspective, light, bedding, rope, water, shared props, or precise contact.
10. **Use the least complex capable engine.** A still, stepped pose, DOM/GSAP layer, or multiplane shot is valid when it fulfils the directing need. Add rigs, PixiJS, Three.js, or Blender only for a proved capability requirement.
11. **Determinism is a release requirement.** Final behavior uses absolute time, local pinned assets, fixed dimensions, and seeded randomness. Pre-render stateful physics, feedback, cloth, hair, collisions, or state machines that cannot reconstruct any frame independently.
12. **Work in a limited adjacent-shot window; release in order.** After the benchmark, two or three adjacent shots may be in layout/production together for continuity and throughput. Each final MP4 still passes its own evidence gate before ordered sequence release.
13. **Voice is an editorial authority, not filler.** Preserve dry stems and a line ledger; fit picture to selected measured performances. Never globally stretch speech or let a music replacement erase narration.
14. **Masters are immutable.** Preserve editable sources, archival master, optional watermarked master, and platform derivatives separately. Verify derivatives by decode, frame inspection, audio ledger, and configured quality floor.
15. **Narrative hooks use an eight-second envelope.** In short-drama mode, establish anomaly by about one second, character or claim by three, the central contradiction or relationship by five, and a physical consequence, irreversible question, or forward pull by eight. Do not mistake a three-second slogan for a completed dramatic hook.
16. **Duration serves dramatic completion.** Do not impose a runtime before the causal chain, reaction time, and ending payoff work. Remove dead duration, but never compress a complete film merely to hit a platform stereotype.

There are no universal quotas for shot length, pose count, layer count, movement density, gait frame count, or camera moves. Those are directing decisions. Objective constraints—identity, facing, support, contact, semantics, timing bounds, file identity, deterministic seeking, and delivery validity—must be enforced.

## Scientific production flow

### 0. Intake and editorial contract

Resolve source rights, adaptation scope, audience, platform, aspect, duration posture, language, subtitles, historical posture, and deliverables. Write story beats as observable change and consequence. For narrative social work, lock the eight-second hook envelope, save object, cover-to-opening match, and feed preview; require early evidence by three seconds, but let the hook complete through consequence or forward pull by eight.

Build a scratch-audio animatic with boards or shapes. Revise the whole edit until every beat earns its duration and the ending completes the opening. Do not generate production assets here.

Validate the manifest:

```bash
python3 scripts/validate_story_manifest.py story-manifest.json --phase editorial --strict
```

### 1. Visual development and production design

For premium/social work, compare at least three materially different art routes, then approve the opening-pressure, central-choice, and consequence hero-frame triad. Lock shape language, focal/value hierarchy, palette, line/texture, light/depth, camera family, composition, signature, anti-generic traits, and phone-size behavior.

After the timed animatic and style route establish real needs, build:

- one neutral frontal identity anchor per recurring character;
- a minimum reference-only model pack with both profiles, needed three-quarter construction, scale, asymmetry, expression range, attachment rules, and forbidden changes;
- recurring prop/environment design sheets and one character/prop/environment integration composite.

These are global references. Mark them reference-only and prohibit animation use.

### 2. Final audio and timed sequence layout

Cast voices with consistent test lines, preserve dry takes, record speaker/cue/speed/take/duration, and refit the edit to measured performances. Finalize shot boundaries, captions, action accents, reaction time, transitions, sound cues, and intentional silence.

Lay out neighboring shots together. Use cheap boxes or rough silhouettes to test geography, actor scale, axis, screen direction, gaze, entry/exit, floor line, obstacles, support, contact, occlusion, negative space, and subtitle space. Review the sequence before polishing a shot.

### 3. Benchmark vertical slice

Choose a short passage that exposes the hardest combination of acting, orientation, identity, contact, effects, compositing, sound, and deterministic rendering. Complete the real pipeline once:

```text
layout → asset facts → motion contract → rough performance → final assets
→ composite → rendered motion evidence → shot release
```

The benchmark establishes method and comparable quality, not a complexity quota for quiet shots. Do not expand production until it passes.

For short-drama work, the benchmark must prove actor intention, a readable reaction chain, at least one physical or spatial consequence, motivated camera/edit changes, and sound-picture timing. A polished still with camera drift is not a passing benchmark.

### 4. Shot planning and asset order

For each shot in the active WIP window:

1. approve narrative responsibility and `animation-decision.json`;
2. approve top-down/camera-facing `spatial-contract.json`;
3. derive `motion-contract.json` when the capability profile requires character/object travel, contact, or simulation;
4. create `shot-capabilities.json`, generate `engine-plan.json`, and accept the least complex route;
5. reuse an asset only if its facts prove compatibility; otherwise generate shot-specific media;
6. approve blocking and silhouette before cleanup, effects, and final light;
7. integrate art, captions, voice, ambience, and transitions;
8. render, extract evidence, review, and release.

Never bulk-generate a universal pose warehouse. Never prohibit useful global design references. Separate three asset classes:

- **global reference assets:** identity/model packs, scale charts, look keys, recurring design sheets;
- **reusable production assets:** only rigs, props, environments, and effects whose compatibility range is proved and hashed;
- **shot-specific assets:** final poses, state frames, backgrounds, masks, shadows, occluders, and contact-sensitive ensembles made just in time.

### 5. Guarded implementation

Initialize a project or prepare one routed shot:

```bash
python3 scripts/init_paper_project.py --manifest story-manifest.json --output ./my-paper-story
python3 scripts/build_routed_shot.py --project ./my-paper-story --shot-id scene-xx --phase prepare
```

`prepare` validates the production manifest, current spatial sidecar, directing decision, capability route, and planning-phase motion contract before scaffolding.

For every final moving asset, write an `asset-facts.json` from actual pixels, then audit and compile the motion source of truth:

```bash
python3 scripts/audit_motion_contract.py shots/scene-xx/motion-contract.json --project . --phase implementation --strict
python3 scripts/compile_motion_contract.py shots/scene-xx/motion-contract.json --project . --output shots/scene-xx/compiled-motion-track.json
```

Use the compiled track in the composition. It owns selector, active times, pixel start/end, instance scale, observed facing, and travel direction. Engine-specific character acting may add pose or rig performance, but it must not contradict the compiled world-space track.

Run implementation verification:

```bash
python3 scripts/build_routed_shot.py --project . --shot-id scene-xx --phase verify
```

This revalidates manifest/space/motion, detects plan drift, audits engine inputs, runs offline checks, verifies deterministic ordered/shuffled seeking, and enforces engine-specific gates.

### 6. Performance and finish

Block the actor’s thought and force path before cleanup. Inspect silhouette, line of action, pose contrast, timing, spacing, arcs, weight, foot/support behavior, overlaps, drag/follow-through, contact, settle, reaction, and cut motivation. Use actual species/mechanism behavior; do not force humans, rabbits, birds, carts, and crowds through one gait template.

Review in distinct passes:

1. editorial and consequence;
2. layout, continuity, scale, staging, and eye trace;
3. acting, motion, direction, weight, support, and contact;
4. identity, anatomy, focal/value/color/light/texture/depth integration;
5. voice, sound, captions, render determinism, decode, and delivery.

Return every defect to its earliest responsible layer. Effects do not repair layout; camera shake does not repair weak contact; polish does not repair an unearned beat.

### 7. Rendered evidence and release

Build evidence from the actual rendered MP4:

```bash
python3 scripts/build_motion_review.py \
  --contract shots/scene-xx/motion-contract.json \
  --video renders/scene-xx.mp4 \
  --project . \
  --output shots/scene-xx/rendered-motion-review.json
```

Inspect the generated entry/contact/settle/exit frames and contact sheet. Record observed facing, travel, support, contact, result, notes, and reviewer. Then run:

```bash
python3 scripts/audit_rendered_motion.py shots/scene-xx/rendered-motion-review.json --project . --strict
python3 scripts/bind_release_evidence.py shots/scene-xx/shot-release.json
python3 scripts/build_routed_shot.py --project . --shot-id scene-xx --phase release
```

Schema-v4 release records declare `motion_required: true|false` and bind the rendered MP4, upstream records, and proof frames to their SHA-256 hashes. Dynamic shots additionally require hash-bound motion evidence and `motion_integrity: pass`; static shots must not fabricate it. All shots still require semantic, spatial, visual, voice/caption, deterministic-render, frame, and technical evidence appropriate to their route.

Review adjacent approved shots as a sequence before opening the next WIP window. Sequence review may invalidate an individually approved shot when continuity, acting intensity, repeated poses, light, eye trace, or sound perspective fails at the cut.

### 8. Final assembly and delivery

Assemble only released shots. Confirm the opening promise, causal progression, emotional consequence, ending lesson/save object, voice ledger, caption safety, sound perspective, and sequence continuity. Render the archival master first; apply a moving watermark only when requested; encode a separate platform derivative.

```bash
python3 scripts/make_review_contact_sheet.py --video master.mp4 --manifest story-manifest.json --output review.jpg
python3 scripts/encode_social_delivery.py master.mp4 social-1080p.mp4 --vmaf-floor 95
```

Report editable project, master, optional watermarked master, social derivative, dimensions, frame rate, duration, codecs, audio streams, expected/confirmed lines, file sizes, compression ratio, VMAF, proof package, and intentional limitations. Never overwrite the master.

## Failure policy

Stop expansion when an upstream gate fails, but continue repairing autonomously within scope. Diagnose the earliest cause, invalidate dependent evidence, fix that layer, and rerun the same controller phase. Add automation only for generalizable objective failures; keep artistic approval human-reviewable and evidence-assisted.

Common returns:

- wrong meaning or weak ending → story/edit;
- wrong target, path, axis, scale, or occlusion → sequence/spatial layout;
- identity, facing, crop, or light mismatch → model pack/source asset/facts;
- sliding, weightless, mechanical, or backward travel → performance/motion contract/implementation;
- pasted-on look → integration/value/light/edge/shadow pass;
- dialect, missing line, or dead timing → voice ledger/edit;
- stale or inconsistent proof → rebuild evidence from current hashes;
- nondeterministic frame → engine route or pre-render decision.
- PPT feeling, narration parked on one image, or an unchanged plate lasting through several clauses → return to beat design, blocking, and shot-specific asset order; do not add more global zoom or particles.

## Core artifacts

- `story-manifest.json`
- `animation-decision.json`
- `spatial-contract.json`
- `shot-capabilities.json` and generated `engine-plan.json`
- `asset-facts/*.json`
- `motion-contract.json` and `compiled-motion-track.json`
- `engine-inputs.json`
- rendered MP4 and extracted evidence
- `rendered-motion-review.json` when motion is required
- schema-v4 `shot-release.json`
- voice ledger, dry stems, edit/master/social deliverables

The project is complete only when the finished film, not merely the documentation, proves its story, performance, physical credibility, visual authorship, sound, and delivery quality.
