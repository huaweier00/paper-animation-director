---
name: paper-animation-director
description: Direct and produce story-led paper animation, shadow theatre, articulated cutout animation, and painterly limited animation with strong character acting, readable physical cause and effect, distinctive art direction, sound-action rhythm, and human-reviewed visual quality. Use for 纸片动画, 皮影动画, 剪纸动画, 卡纸偶动画, 工笔动画, 宣纸水彩故事, illustrated folktales, historical or cultural narrative films, recurring-character animation, and for diagnosing or improving paper-animation projects that feel generic, stiff, slideshow-like, over-engineered, or technically correct but emotionally weak.
---

# Paper Animation Director

Direct the film before governing the pipeline. Optimize for a memorable finished scene, not for the number of records, engines, layers, or passing checks.

## Non-negotiable hierarchy

Use this order whenever rules compete:

1. story pressure and character intention;
2. readable performance, contact, force, and consequence;
3. a project-specific visual identity;
4. rhythm, stillness, sound, and editing;
5. medium honesty;
6. implementation reliability;
7. release evidence and delivery compliance.

Do not sacrifice a stronger scene merely to reuse a template, satisfy an optional schema, display a medium technique in every shot, or use a more sophisticated engine.

Automated checks may reject technical defects. They never certify taste, acting, emotional force, visual distinction, or final approval.

## Work in two modes

### Mode A — creative development

Keep this mode open and inexpensive. Rough drawings, temporary audio, incomplete assets, alternate cuts, deliberate stillness, unusual framing, and contradictory experiments are allowed.

Require only lightweight working documents:

- a brief with audience, duration, aspect, emotional promise, and forbidden outcomes;
- a beat sheet or storyboard with one dramatic responsibility per scene;
- a short list of character, space, and sound continuity facts.

Do not require release manifests, hashes, engine readiness records, or per-shot approval packages during exploration.

To scaffold a neutral creative project, start from `assets/project-template/manifests/story-manifest.creative.example.json` and run:

```bash
python3 scripts/init_paper_project.py --manifest creative-manifest.json --output ./project-name
```

Use `--production` only after benchmark approval and only when the advanced pipeline is justified.

### Mode B — production and release

Enter this mode only after the user approves the visual direction and the performance benchmark. Then add the minimum contracts and deterministic checks needed by the chosen implementation and delivery target.

Do not apply every available gate. Load and run only the gates justified by the actual medium, engine, risk, and release destination.

## Creative workflow

### 1. Find the dramatic spine

For the film and for every scene, write the visible chain in plain language:

```text
pressure or desire
→ decision
→ preparation
→ action
→ contact or state change
→ physical consequence
→ another character's reaction
→ changed story state
```

If a silent viewer cannot identify the changed state, repair the scene before producing final art. Do not use narration to excuse missing visual causality.

### 2. Choose the medium without turning it into a demonstration

Select the dominant route:

| Route | Use when | Read completely |
| --- | --- | --- |
| `shadow-theatre` | Light, screen distance, silhouette articulation, rods, joints, or shadow optics carry story meaning | `references/route-shadow-theatre.md` |
| `cutout-paper` | Opaque card or paper actors use pivots, replacement poses, folds, pins, layered depth, or visible construction | `references/route-cutout-paper.md` |
| `painterly-limited` | Gongbi, watercolor, silk-like, ink, or illustrated characters use authored pose or whole-tableau state changes | `references/route-painterly-limited.md` |

Use the route to prevent false material claims. Do not force every shot to prove the route. Once the audience understands the medium, let it serve the story quietly.

Read `references/performance-grammar.md` when blocking acting. Read `references/sound-action-cueing.md` when timing action and sound. Do not load unrelated engine or release references yet.

### 3. Establish a visual identity before using a scaffold

Create at least three materially different look studies inside the selected medium. Vary silhouette, proportion, palette, edge, negative space, light, paper behavior, typography, and motion posture—not only color grading.

Reject:

- universal beige antique paper;
- default teal-and-gold history grading;
- generic AI prettiness;
- identical subtitle cards across unrelated stories;
- constant paper grain, drifting particles, slow push-ins, breathing scale, or parallax used as proof of animation;
- cute proportions that erase age, danger, hierarchy, labor, or cultural specificity.

Start from a neutral technical canvas. Add every aesthetic choice deliberately.

### 4. Build a timed scratch animatic before final assets

Use crude blocks, temporary poses, or rough whole-tableau states. Lock:

- scene order and duration;
- entrances, exits, sightlines, and screen direction;
- the action target and contact point;
- reaction windows and intentional silence;
- where narration ends and picture must carry the story;
- the exact moment each scene has completed its dramatic responsibility.

Cut dead time now. Grain, camera drift, particles, ambient loops, or unchanged held plates do not justify duration.

### 5. Prove the hardest 8–15 seconds

Choose the passage with the hardest combination of acting, identity, contact, medium truth, and sound. Build it to near-final quality before expanding the film.

The benchmark must include:

- a character wanting or resisting something;
- anticipation or hesitation;
- a specific action and readable contact or state change;
- force propagation or a credible material response;
- a consequence and reaction;
- at least one purposeful hold or still moment;
- shot-specific sound timing when sound matters.

A polished still, camera move, particle layer, root translation, silent montage, or engine demo is not a passing performance benchmark.

Before approval, compare the benchmark with `references/gold-standard-regression.md`. A technically valid benchmark that is flatter, less readable, more generic, or less rhythmically alive than the gold passages must be revised.

### 6. Produce one shot and one dominant problem at a time

For each shot:

1. state the shot's single dramatic responsibility;
2. identify the one failure that most harms it;
3. make the smallest change that can solve that failure;
4. preview the exact passage with sound;
5. compare before and after;
6. keep the change only if the scene becomes clearer, stronger, or more distinctive;
7. cut any embellishment that competes with the responsibility.

Do not attempt to improve art direction, acting, physics, captions, mix, transitions, engine architecture, and release evidence in the same pass.

### 7. Direct performance as phrases, not perpetual motion

Prefer complete connected poses, route-appropriate rigs, connected ensembles, or whole-tableau state changes. Preserve silhouette and weight.

Shape phrases from intention:

```text
notice → decide → prepare → act → make contact → absorb force → hold → react → settle
```

Not every phrase needs every beat, but entry, action, result, and exit must be intelligible. Vary timing by thought, force, fatigue, status, and material. Avoid symmetric easing and identical loops.

Use stillness when a character is thinking, withholding, grieving, listening, or realizing. Stillness passes only when pressure changes within or around it; a frozen plate plus drifting texture is not acting.

### 8. Make sound land on causes and consequences

Use sound to clarify weight, material, distance, and edit rhythm. Bind important cues to visible events: foot plant, pole flex, bucket handoff, water impact, blade scrape, curtain pull, lamp fall, fire spread, screen reveal, or reaction.

Audit the actual mix, not merely stream presence. Confirm audibility, sync, hierarchy, silence, and emotional posture at normal listening level.

### 9. Review the film as a viewer

Review the exact rendered or previewed timeline in four passes:

1. silent: story, intention, contact, and changed state;
2. audio-only: voice, pauses, sound hierarchy, and edit rhythm;
3. normal playback: attention, emotion, surprise, fatigue, and pacing;
4. frame inspection: identity, silhouette, edges, grounding, occlusion, captions, and medium artifacts.

Ask the user to approve the benchmark and final preview. Do not infer approval from automated checks.

## Human creative gates

A scene advances only when a human review can answer yes to all five:

1. **Silent readability** — Can a viewer understand who wants what and what changed?
2. **Performance** — Do anticipation, force, weight, hold, and reaction feel authored rather than procedural?
3. **Space and contact** — Are facing, ground, depth, target, touch, and consequence credible?
4. **Visual identity** — Could this frame belong only to this project, rather than to a generic paper-animation template?
5. **Rhythm and sound** — Does the scene enter, develop, land, and leave at the right moments, with sound supporting rather than explaining it?

Record concise review notes in the storyboard, production notes, or existing review document. Do not create a new schema solely to store these answers.

## Implementation routing

Use the least complex technique that preserves the approved performance:

- whole-tableau or replacement-pose animation for integrated painterly acting;
- connected ensemble frames for contact-heavy character interaction;
- GSAP/DOM for deterministic rigid layers, masks, opacity, replacement poses, and local transforms;
- PixiJS for a genuinely demanding 2D effects field;
- Rive or Spine for sustained local skeletal or mesh deformation that authored assets support;
- Three.js for necessary spatial depth or camera behavior;
- Blender only for physical action, simulation, or 3D construction that simpler methods cannot credibly produce.

Specialized engines are optional implementation tools, not signs of artistic quality. Read `references/hybrid-shot-pipeline.md` and `references/engine-execution-templates.md` only after a shot has earned a specialized route.

For HyperFrames authoring, preview, checks, and rendering, load the mandatory `hyperframes` skill and only its stage-relevant references. Use `imagegen` for raster generation or editing when needed.

## Release discipline

After creative approval, read only the applicable release references:

- production order or invalidation risk: `references/production-architecture.md`;
- asset art direction: `references/visual-art-direction-and-asset-quality.md`;
- identity and pose continuity: `references/character-and-pose-system.md`;
- detailed spatial contracts: `references/shot-spatial-contract.md`;
- rendered motion evidence: `references/motion-integrity.md`;
- voice and subtitles: `references/voice-timing-and-subtitles.md`;
- final delivery: `references/quality-gates-and-delivery.md`.

Use hashes, manifests, engine probes, and release scripts only to protect a finished creative decision from technical drift. Never use their green status as a substitute for watching the film.

## Return conditions

Return to the earliest failed creative layer:

- unclear story state → rewrite beats or staging;
- generic visual identity → redo look studies, not color polish;
- weak acting → reblock intention, pose, timing, contact, and reaction;
- floating or false contact → repair space, actor assets, and force propagation;
- slideshow feeling → add meaningful state change or shorten the shot, not more drift;
- repetitive movement → vary thought, force, fatigue, status, and consequence;
- correct files but weak film → continue directing; do not add schemas;
- strong preview but broken output → repair implementation or rendering without redesigning the approved scene.

## Completion

The film is complete only when:

- the user has reviewed and approved the final preview;
- the five human creative gates pass;
- comparison with the gold standards reveals no unexplained regression in acting, causality, rhythm, or distinctiveness;
- required technical checks pass for the chosen implementation;
- the rendered master is watched and its sound, duration, resolution, and delivery files are verified.

Passing validators alone never completes a paper-animation film.
