---
name: paper-animation-director
description: Direct and produce story-led paper animation through a fail-closed workflow that distinguishes shadow theatre, articulated cutout paper, and painterly limited animation. Use for 纸片动画, 皮影动画, 剪纸动画, 卡纸偶动画, 工笔动画, 宣纸水彩故事, illustrated folktales, historical or cultural narrative films, recurring-character animation, and premium social story films where medium truth, character performance, spatial contact, sound rhythm, rendered evidence, and release quality must remain coherent.
---

# Paper Animation Director

Direct performers in a declared medium. Do not decorate rigid illustrations until they resemble motion. A valid project proves, in this order:

```text
story deserves production
→ medium has one physical/visual truth
→ characters can perform the required actions
→ sound and motion share a rhythm
→ rendered shots fulfil their responsibilities
→ only released shots enter the master
```

Trust rendered evidence tied to exact files. Prompts, filenames, CSS class names, source-code intent, and self-declared `pass` values are not proof.

## Select one route before production art

Create and approve `medium-contract.json`, then read exactly one route reference completely:

| Route | Use when | Required reference |
|---|---|---|
| `shadow-theatre` | The film claims skin/paper shadow-puppet construction, rear light, screen-plane staging, rod/joint performance, or 皮影 language | `references/route-shadow-theatre.md` |
| `cutout-paper` | Opaque paper/card actors use pivots, replacement poses, layered depth, pins, folds, or visible material construction | `references/route-cutout-paper.md` |
| `painterly-limited` | Gongbi, watercolor, silk-like, ink, or illustrated characters use authored pose replacement, local rigs, or integrated state changes | `references/route-painterly-limited.md` |

Do not blend route claims casually. A painterly character may borrow shadow-theatre timing, but it must not claim transmitted leather light. A shadow-theatre route must not use an opaque full-body painting translated as the hero performance.

Read `references/performance-grammar.md` for every route before shot assets. Read `references/sound-action-cueing.md` before final timing or performance blocking.

## Fail-closed production kernel

1. **Complete the disposable film first.** Build a full scratch-audio animatic, not only a hook. It must work muted, audio-only, and combined before formal voices, production art, or full-film implementation.
2. **Lock the medium before the look.** `medium-contract.json` owns route, material/screen model, articulation or state-change model, depth model, sound posture, and forbidden shortcuts.
3. **Prove performance before polish.** Every action-bearing shot has `performance-contract.json` with objective, attention, lead control, support, performance mode, action phases, proof times, and sound cues. Background motion, camera motion, opacity, particles, and whole-actor transforms are presentation, not character performance.
4. **Use internal change for actor action.** Physical or emotional action must use articulated local controls, authored replacement poses, connected ensemble states, or integrated full-scene states. Rigid root translation is valid only for a deliberately rigid object or stylized travel whose support and action are proved elsewhere.
5. **Earn stillness.** A deliberate still identifies the prior cause, present result or tension, audience-facing purpose, sound/visual support, and exit condition. One unchanged pose must not carry incompatible intentions or several unshown plot verbs.
6. **Treat sound as a directing system.** Preserve dry stems and a cue ledger. Dialogue, singing, percussion, effects, holds, contacts, and cuts share measured times. A shadow-theatre release cannot be silent or music-only.
7. **Reject incompatible pose reuse.** Reuse a production asset only when identity, camera, facing, support, light, action, intention, and performance state are compatible. Availability is not authorization.
8. **Separate performance from presentation.** Review performance motion, physical response, presentation motion, and surface motion independently. Presentation or surface activity cannot satisfy a performance requirement.
9. **Sequence continuity precedes shot polish.** Approve adjacent layout, axis, floor/screen line, direction, scale, light, entry/exit, eye trace, acting intensity, and sound perspective before final assets.
10. **Choose the least complex performance-capable engine.** “Capable” means it can express the approved acting and contact, not merely move pixels. Use a still, stepped poses, DOM/GSAP, Rive, PixiJS, Three.js, or Blender only after the performance contract declares why.
11. **Bind review to the render.** Review exact entry, anticipation, action, contact, hold, settle, reaction, and exit evidence from the rendered MP4. Upstream changes invalidate downstream approval.
12. **Assemble released shots only.** A final master requires an ordered `release-index.json`, current shot-release hashes, a valid audio contract, and a verified decoded master. Do not create an alternate final-film directory that bypasses the controller.

## Required production flow

### 0. Intake and editorial proof

Resolve rights, adaptation boundary, audience, platform, aspect, duration posture, language, historical posture, subtitles, audio posture, and deliverables. Write observable beats and consequences.

Build the entire scratch animatic with temporary shapes, scratch voice, captions, sound accents, and intentional silence. Reject production expansion when only the opening has been tested.

Validate the story manifest:

```bash
python3 scripts/validate_story_manifest.py story-manifest.json --phase editorial --strict
```

### 1. Medium and visual development

Create `medium-contract.json` from the route-matched template (`medium-contract.example.json` for shadow theatre, or the named cutout/painterly examples) and validate it:

```bash
python3 scripts/audit_medium_contract.py medium-contract.json --strict
```

Compare at least three materially different visual routes inside the selected medium. Approve the opening-pressure, central-choice/contact, and consequence hero frames plus one character/prop/environment integration composite. Lock silhouette, value, palette, edge, material, light, depth, screen or ground behavior, signature, and anti-generic traits.

Build reference-only identity/model packs after the timed animatic establishes required views. Build a route-appropriate performer model for each recurring hero:

- shadow theatre: parts, joints, pivots, rods/controls, screen side, translucent material, signature action phrases;
- cutout paper: parts or pose-family decision, pivots/overlap, draw order, material thickness, support and contact points;
- painterly limited: authored pose/state family, identity construction, local-control limits, integration and repaint rules.

Reference design never enters a final shot unless separately approved and registered as production media.

### 2. Final audio and sequence layout

Select measured performances, preserve dry stems, and create `audio-contract.json`. Fit picture to chosen takes. Lay out adjacent shots with rough silhouettes; prove geography, support, contact, occlusion, subtitle space, action accents, reactions, and cut motivation.

### 3. Performance benchmark

Choose an 8–15 second passage or another short passage long enough to expose the hardest combination of acting, route truth, identity, contact, sound, integration, and deterministic rendering. The benchmark must contain:

- at least one readable intention-to-result performance phrase;
- at least one reaction or relationship change;
- route-specific material/screen evidence;
- sound-picture timing;
- a static-camera read before optional presentation motion.

A polished still, root translation, camera push, particle layer, or silent montage is not a passing action benchmark. Do not open the full-film WIP window until the benchmark passes.

### 4. Plan and build each shot

For each shot in a limited adjacent-shot window:

1. approve `animation-decision.json` and `spatial-contract.json`;
2. create and approve `performance-contract.json`;
3. create `shot-capabilities.json`; route and approve `engine-plan.json`;
4. create `motion-contract.json` when travel, contact, or simulation requires it;
5. create shot-specific assets and `asset-facts.json` only after planning passes;
6. block performance with rough shapes before final art;
7. audit pose reuse before accepting an existing production asset;
8. integrate final art, light, captions, voice, ambience, effects, and transitions;
9. render, extract evidence, review, and release in sequence order.

Run the guarded controller:

```bash
python3 scripts/build_routed_shot.py --project . --shot-id scene-xx --phase prepare
python3 scripts/build_routed_shot.py --project . --shot-id scene-xx --phase verify
python3 scripts/build_routed_shot.py --project . --shot-id scene-xx --phase release
```

The controller must validate the project medium contract and the shot performance contract in every phase. Do not replace it with ad hoc rendering.

### 5. Performance and sequence dailies

Review each shot in this order:

1. editorial responsibility and consequence;
2. static layout, silhouette, axis, scale, support, and eye trace;
3. intention, anticipation, lead part, timing, spacing, contact, hold, settle, and reaction;
4. route truth: material, joints/states, screen/ground, light, edges, and integration;
5. voice, singing/music, percussion/effects, captions, and cut rhythm;
6. deterministic render, decode, proof hashes, and delivery.

Review adjacent shots for repeated poses, acting intensity, direction, light, sound perspective, and transition energy. An individually approved shot may return when sequence dailies expose a downgrade.

### 6. Final assembly and delivery

Create an ordered release index and audio contract. Audit before and after assembly:

```bash
python3 scripts/bind_release_index.py release-index.json --project .
python3 scripts/audit_release_index.py release-index.json --project . --strict
python3 scripts/audit_audio_mode.py audio-contract.json --project . --video master.mp4 --strict
```

Preserve editable sources, dry stems, archival master, optional watermarked master, and platform derivatives separately. Verify decode, audio streams, expected lines, captions, phone-size frames, compression, and save/ending object. Never overwrite the archival master.

## Failure policy

Stop expansion at the earliest failed layer and repair autonomously within scope:

- moving poster, rigid PNG acting, or repeated incompatible pose → performance contract/source asset;
- shadow route without transmitted light, joints, screen behavior, or sound → medium route/model;
- beautiful actor pasted into a background → integration/value/light/edge/contact;
- correct files but weak acting → performance blocking and benchmark, not more schemas;
- narration parked over unchanged art → edit, shot division, performance states, and sound cueing;
- missing contract or stale hash → rebuild evidence; do not bypass;
- final master assembled from unreleased shots or missing audio → reject assembly.

## Reference map

Read only what the active stage requires, except the selected route, performance grammar, and sound cueing, which are mandatory:

- route truth: `references/route-shadow-theatre.md`, `references/route-cutout-paper.md`, `references/route-painterly-limited.md`;
- acting and motion phrases: `references/performance-grammar.md`;
- music/dialogue/effects timing: `references/sound-action-cueing.md`;
- production order and invalidation: `references/production-architecture.md`;
- art development and asset curation: `references/visual-art-direction-and-asset-quality.md`;
- identity, model packs, poses, rigs, ensembles: `references/character-and-pose-system.md`;
- space and action targets: `references/shot-spatial-contract.md`;
- detailed motion direction: `references/performance-and-motion-direction.md`;
- motion contracts and rendered proof: `references/motion-integrity.md`;
- engine routing/integration: `references/hybrid-shot-pipeline.md`;
- prompts and asset rejection: `references/image-generation-prompts.md`;
- voice, timing, subtitles: `references/voice-timing-and-subtitles.md`;
- release and delivery: `references/quality-gates-and-delivery.md`.

For implementation/rendering, also load the mandatory `hyperframes` entry skill and its required stage references. Use `imagegen` for raster generation/editing and `dynamic-video-watermark` only when requested at delivery.

The project is complete only when the finished film proves its story, route truth, actor performance, physical relationships, sound rhythm, visual authorship, and release integrity.
