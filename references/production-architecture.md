# Paper-animation production architecture

Use this reference during project intake, after the scratch animatic, and when a project is drifting into expensive asset generation without stronger animation. It separates global development, sequence planning, shot production, and release so that continuity and throughput improve without weakening objective gates.

## Contents

1. Production principles
2. Why average-looking work survives a complex pipeline
3. Scientific production order
4. Asset order and reuse
5. Sequence and shot scheduling
6. Quality-control structure
7. Automation architecture
8. Failure recovery and dependency invalidation

## 1. Production principles

Treat the film as four connected systems:

```text
editorial system → visual/performance system → production system → evidence system
```

- The editorial system decides what the audience must understand, feel, and remember.
- The visual/performance system decides staging, acting, design, cinematography, motion language, and sound rhythm.
- The production system creates only the assets and engine work justified by approved plans.
- The evidence system checks the rendered result rather than trusting filenames, prompts, declarations, or source-code intent.

Do not confuse a large number of documents with a controlled production. A gate is real only when it has an artifact, a validator, an owner, an invalidation rule, and a downstream consequence.

Use low freedom for fragile invariants: file identity, orientation, support, contact, timing ranges, hashes, deterministic seeking, and release evidence. Use high freedom for directing choices: duration, pose count, stillness, shot division, visual style, performance intensity, and camera language.

## 2. Why average-looking work survives a complex pipeline

A technically elaborate paper-animation project can still feel average for predictable reasons:

1. **The animatic proves information, not performance.** Boards establish plot, but no pass proves intention, anticipation, line of action, weight, contact, settle, and reaction.
2. **Generated stills become animation assets too early.** A beautiful isolated pose is accepted before testing silhouette, scale, edge integration, support, neighboring poses, or actual display size.
3. **Motion is presentation-led.** Camera drift, whole-layer translation, fades, and particles create activity while the character does not perform.
4. **Character identity is under-specified.** One frontal image anchors the face but not profile construction, height, asymmetry, hands, costume overlap, or expression range.
5. **Shots are optimized locally.** Each image may be attractive, while lens, axis, screen direction, scale, light, and acting intensity jump across the sequence.
6. **Timing follows narration mechanically.** The picture fills voice duration instead of shaping anticipation, accent, contact, recovery, thought, and silence.
7. **Engine sophistication substitutes for direction.** A rig, particle system, WebGPU layer, or Blender render cannot repair weak staging or generic poses.
8. **Review evidence is too sparse.** First/mid/final frames miss short direction flips, pose pops, sliding feet, bad overlap, and contact errors.
9. **Approval is self-reported.** A field containing `pass` proves that someone typed `pass`; it does not prove what was inspected.
10. **The workflow is too serial or too broad.** Strict one-shot-only work prevents sequence continuity; bulk asset generation creates mismatch and sunk-cost pressure.

Raise quality by moving effort upstream into writing, boards, layout, model packs, performance blocking, and representative motion tests. Do not wait for final compositing to discover that the action is weak.

## 3. Scientific production order

### Stage A — development

1. Lock source rights, adaptation boundary, platform, audience, duration range, aspect, and delivery posture.
2. Write the story contract, scene goals, action table, opening promise, ending consequence, and transferable point.
3. Build a disposable audio-board animatic with shapes, scratch voice, temporary captions, and basic sound.
4. Revise until the complete edit works muted, audio-only, and combined.

Do not generate production art in Stage A. The purpose is to prove the film deserves production.

### Stage B — visual development and production design

After the full scratch animatic passes:

1. Compare materially different visual routes.
2. Approve the opening/conflict/consequence hero-frame triad.
3. Lock value hierarchy, palette, line, texture, light, depth, composition, signature, and anti-generic traits.
4. Build a production-design pack:
   - one canonical frontal identity anchor per recurring character;
   - reference-only controlled profile and three-quarter construction views when the film needs them;
   - scale chart, asymmetry map, costume/prop attachment map, expression range, hand/hoof/foot rules, and forbidden changes;
   - recurring prop design sheets;
   - environment keys, perspective/floor-line rules, and reusable material samples.
5. Prove one character/prop/environment integration composite at intended display scale.

Reference-only design material is not a shot asset. It may be created globally because its job is consistency, not staging.

### Stage C — final audio and timed sequence animatic

Formal voice production and the controlled identity pack may proceed in parallel after Stage B starts, because neither should wait unnecessarily on the other. Before shot production:

1. Select formal voices and preserve dry stems.
2. Measure every approved take.
3. Refit the scratch edit to the approved performances.
4. Add final shot boundaries, layout boards, action accents, pauses, transitions, captions, and sound cues.
5. Review the complete timed sequence for rhythm and continuity.

Lock timing before expensive cleanup. Permit later timing changes only through an explicit edit change that invalidates affected shots.

### Stage D — sequence layout and blocking

Plan a coherent sequence before polishing individual shots:

1. Lock camera axis, lens/scale family, floor line, geography, entrances/exits, screen direction, light, and continuity anchors.
2. Create top-down and camera-facing plans for adjacent shots.
3. Block characters and props with boxes or rough silhouettes.
4. Test travel, support, contact, occlusion, subtitle space, and transition continuity.
5. Build a rough motion playblast with temporary shapes or low-cost poses.

This is where direction errors should be cheap. Do not discover them after premium asset generation.

### Stage E — benchmark

Choose a representative passage that exposes the production's hardest combination of acting, identity, motion, contact, integration, timing, and sound. Prove the complete vertical slice:

```text
approved layout → asset facts → motion contract → rough motion → final assets → composite → rendered review → release
```

The benchmark sets a method and quality bar. It does not set a quota for every quieter shot.

### Stage F — shot production

For each approved shot:

1. Finalize narrative responsibility and animation decision.
2. Finalize spatial and motion contracts.
3. Select the least complex capable engine.
4. Generate or reuse assets only after passing shot-fit and asset-fact review.
5. Build a blocking pass before cleanup.
6. Review silhouette, weight, timing, support, contact, direction, and pose continuity.
7. Finish art integration, effects, lighting, captions, and sound.
8. Render the MP4, build evidence, and release the shot.

### Stage G — sequence dailies and final assembly

After adjacent shots are available, review them as a sequence. Check:

- geography, axis, entry/exit, gaze and screen direction;
- character scale, costume and light continuity;
- acting intensity and pose repetition;
- cut motivation and eye trace;
- audio perspective, ambience continuity, caption rhythm, and transition energy.

An individually approved shot may return to production if the sequence reveals a contradiction.

### Stage H — delivery and postmortem

Preserve archival master, watermarked master, social derivative, audio stems, editable projects, contracts, asset facts, motion reports, and review evidence. Record failures as schema fields or automated tests only when the rule generalizes.

## 4. Asset order and reuse

Use three asset classes.

### Global reference assets

Create after the edit and visual direction pass:

- identity anchors and controlled construction views;
- scale charts and asymmetry maps;
- recurring prop and environment design sheets;
- palette, texture, lighting, and edge references.

Mark them `reference_only: true` and prohibit direct animation use.

### Reusable production assets

Create only when the benchmark or multiple approved layouts prove reuse:

- a recurring rig or validated gait family;
- a modular prop with known states;
- a perspective-locked environment master;
- reusable deterministic effects;
- verified typography and caption components.

Give each reusable asset an `asset-facts.json` record, content hash, supported cameras/actions/facings, display-scale limits, mirror policy, and rejection history. Reuse is conditional compatibility, not availability.

### Shot-specific assets

Create just in time from the approved shot contracts:

- exact complete poses or pose sequences;
- contact-sensitive ensembles;
- final background plate or state change;
- shot-specific effects, masks, occluders, and shadows.

Do not pre-generate a general pose warehouse. Do not ban all global design work. Separate reference design from production media.

## 5. Sequence and shot scheduling

Replace both harmful extremes:

- Avoid producing the whole film in bulk before review.
- Avoid allowing only one shot to exist at any stage.

Use a limited work-in-progress window of adjacent shots, normally two or three after the benchmark passes. Requirements:

- all shots in the window have approved editorial, timing, layout, spatial, and motion contracts;
- shared assets have approved facts and compatibility ranges;
- final release still occurs one shot at a time and in sequence order;
- a failed upstream contract invalidates every dependent shot in the window;
- review the window as a sequence before opening the next one.

This preserves continuity and throughput without permitting uncontrolled bulk generation.

## 6. Quality-control structure

Use five distinct passes. Do not collapse them into one general “looks good” review.

1. **Editorial pass:** promise, clarity, consequence, pace, ending.
2. **Layout pass:** geography, staging, silhouette, scale, lens, axis, negative space.
3. **Performance/motion pass:** intention, anticipation, weight, arcs, spacing, contact, settle, reaction, direction.
4. **Art-integration pass:** identity, anatomy, value, color, light, texture, edges, depth, shadows, phone readability.
5. **Picture/sound/release pass:** voice ownership, sound perspective, captions, deterministic render, decode, proof records, delivery.

Assign findings to the earliest responsible layer. Do not fix a layout defect with effects, a motion defect with camera shake, or an editorial defect with more polish.

## 7. Automation architecture

Automate objective work and accelerate judgment work.

### Objective automation

- schema validation;
- path and hash validation;
- direction-vector and facing alignment;
- mirror authorization;
- start/end corridor feasibility;
- deterministic seeking;
- audio duration and expected-line presence;
- file decode, dimensions, alpha, crop safety, and delivery metrics;
- dependency drift and stale evidence detection.

### Judgment acceleration

- generate candidate comparison sheets;
- generate asset-orientation cards;
- generate motion contact sheets at entry, quarter, midpoint, three-quarter, contact, settle, and exit;
- overlay travel and facing arrows in review-only media;
- render silhouette, grayscale, blur/focal, phone-size, and enlarged-detail variants;
- play motion at 0.25×, 1×, and 2×;
- keep rejection reasons and recurring failure tags searchable.

Do not automate approval by asking one model to affirm its own output. Bind every approval to observable evidence and the exact artifact hash.

### Incremental build and invalidation

Treat the project as a dependency graph:

```text
story/edit
  → timing
  → sequence layout
  → spatial contract
  → asset facts
  → motion contract
  → engine inputs
  → render
  → review evidence
  → release
```

When an upstream hash changes, mark downstream evidence stale. Never preserve `approved` merely because filenames remain unchanged.

## 8. Failure recovery and dependency invalidation

Return to the earliest responsible layer:

- wrong story meaning → edit/story contract;
- wrong action target or path → layout/spatial contract;
- wrong identity, orientation, light, or asymmetry → asset generation/asset facts;
- sliding, weak weight, bad anticipation, or timing → blocking/motion contract;
- broken contact or perspective → architecture choice or connected ensemble;
- muddy integration → compositing/art direction;
- missing line or accent → audio ledger/timeline;
- stale render → dependency hashes/build cache.

Preserve rejected artifacts outside active production paths or mark them unusable. Never allow a rejected file to remain addressable under an approved asset ID.
