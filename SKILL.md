---
name: paper-animation-director
description: Turn a story, folktale, fable, script, or narration into a historically and physically credible multi-layer paper animation with reference-only frontal character identities, shot-specific spatial contracts, just-in-time shot assets, complete connected poses, realistic and recognizable props, ground/support continuity, narration-driven timing, per-shot release gates, voice-stem recovery, and master/social delivery. Use when the user asks for 纸片动画, 剪纸动画, 柔和工笔动画, 宣纸水彩故事, paper-theatre animation, an illustrated folktale, a cultural or historical story film, a layered recurring-character story, or a narrative animation whose identity, direction, objects, space, actions, sound, moral ending, and platform delivery must remain consistent and readable.
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
- Use `dynamic-video-watermark` for the final moving ownership mark. Do not duplicate its implementation here.

## Non-negotiable rules

1. Treat multilayer animation as separation by depth and physical responsibility, not as permission to cut a person into pieces.
2. Approve exactly one neutral frontal identity reference for each recurring character. Treat it as generation conditioning only: never key, animate, place, or deliver it as a shot asset.
3. Generate no background, pose, gait, prop, effect, ensemble, or full-scene plate before the active shot has an approved semantic event and spatial contract. Lock global art direction early; design concrete assets just in time per shot.
4. Use complete connected character poses by default. Never reconstruct a hero from independently generated head, torso, arms, and legs when seams will be visible.
5. Generate a connected ensemble pose or state atlas for shared-load actions such as carrying, lifting, embracing, rescuing, or handing off a heavy object.
6. Separate only elements that need independent motion: foreground, atmosphere, props, rope, water, fire, smoke, shadows, particles, captions, and watermark.
7. Express every important event as `cause → action → propagation → result`, with a proof frame that remains understandable when audio is muted.
8. Lock narration before final timing. Use measured audio duration; do not stretch voice or pad scenes to an arbitrary target.
9. Do not use whole-frame image-to-video as the default animation engine. Keep story-critical characters, captions, and props on deterministic, seek-safe timelines.
10. Do not render a full film before the hardest 8–15 second benchmark shot passes continuity, physics, timing, and subtitle review.
11. Draw and approve a top-down plan plus a camera-facing plan before generating any asset for a shot. Mark floor line, axes, actor start/end zones, facing, paths, clearances, obstacles, semantic targets, occlusions, and subtitle-safe zones.
12. Reject a shot whose action target is semantically wrong or unreachable. A line saying “write on the wall” must identify a writable wall target; a nearby window is not an acceptable substitute.
13. Treat historical accuracy as an adopt/reject contract: every period claim needs a source or explicit rationale, and every tempting later-period prop, floor, roof, stage, costume, or furniture choice must be rejected or justified.
14. Prefer a complete full-scene plate when bed, bedding, canopy, character, furniture, or light contact would be fragile as separate layers. Prefer independent complete characters only when they must travel, react, or change pose.
15. A lamp and its flame are one causal unit by default. A character is one connected body by default. A shared lift, restraint, carry, handoff, or embrace is one connected ensemble by default.
16. Never simulate walking with translation-only tweens. Generate a shot-specific normalized complete-body gait cycle with one facing direction, shared canvas, center, and feet baseline; animate the cycle on a world-space parent track.
17. Make travel vector, head, shoulders, chest, feet, and gaze agree. Treat a left/right mismatch as a failed asset, not a styling issue. Do not mirror or force-fit it unless a documented symmetry, handedness, text, light, contact, and continuity audit explicitly permits mirroring.
18. Do not reuse an existing asset merely because it is available. It is only a candidate and must pass the active shot’s space, scale, period, lighting, orientation, target, contact, and action contract; otherwise regenerate it.
19. Protect the complete head and readable face at all required review times. Reject any unplanned frame edge, `overflow`, crop, mask, matte, foreground, or layer boundary that slices through the scalp, facial contour, eyes, nose, or mouth and creates a half-face or amputated-head effect.
20. Allow partial face/head occlusion only when a visible physical occluder, depth order, time window, narrative reason, and unobstructed identity-proof frame are declared in the shot review contract. Natural profile is not clipping; an unexplained straight cut is.
21. Assign every spoken line to a speaker and an audio stem. Audition for accent as well as tone; reject dialect or identity drift, keep narrator and character dialogue from overlapping, and default Chinese captions to bottom-center safe placement.
22. Every shot must pass three reads: muted visual proof, voice-only speaker/timing proof, and combined picture/sound/subtitle proof. A Studio screenshot is not delivery evidence; review frames from the rendered MP4.
23. Treat “paper animation” as a layering and motion method, not a mandatory surface material. When the user requests soft gongbi, silk-like painting, or restrained hand-painted color, reject heavy fibers, torn white rims, embossed relief, cardboard thickness, curled edges, and paper-pulp grain.
24. Give every narrated or story-critical object a recognizability contract: real-world class, silhouette, proportion, material, attachment/support, state changes, and proof time. Reject arrows that become direction lines, grass that floats without roots, gold that reads as an abstract pile, or notices that read as placeholder icons.
25. Keep every standing actor, animal, wheel, vehicle, and placed prop attached to a declared support surface. Review feet, hooves, wheels, shadows, overlap, and scale at the first, midpoint, proof, and final frames. A guide “in front of the procession” must stand on the road, not above the horse or scenery.
26. Treat commands as state transitions, not omitted narration. When a ruler orders weapons lowered, preserve `aimed → command/gesture → visibly lowered → safe final state` in picture and sound.
27. Release exactly one shot at a time. Do not generate, animate, or approve the next shot until the current rendered MP4 passes semantic, realism, spatial, identity, audio, caption, and technical review. A visually attractive draft is not an approval.
28. Design the ending before production. Require consequence, cultural/source closure when relevant, and a concise transferable lesson. Do not let the film end on an information card that explains provenance but fails to complete the emotional or educational argument.
29. Preserve a voice ledger and dry voice stems independently of music. Before delivery, prove every expected line exists at its locked time and speaker. If narration is lost from a music-backed render, restore the approved stems onto the unchanged timeline rather than regenerating performances or retiming the film.
30. Preserve the archival master, watermarked master, and compressed social derivative as separate files. Verify the social file by full decode, technical probing, rendered-frame review, and a VMAF floor normally set to 95; never overwrite the master.

## Workflow

### 0. Run the retrospective and production intake

Read `references/production-retrospective.md` before designing a new historical, cultural, or recurring-character paper story. For soft gongbi or social-platform fables, read `references/gongbi-fable-production-retrospective.md` as well. Record the project’s aspect-ratio decision, surface-style decision, historical evidence tier, adopt/reject list, spatial plan, asset architecture, voice policy, ending contract, proof frames, and approval gates. Treat “looks nice” as insufficient evidence for a scene, asset, motion, or prop choice.

### 1. Create the story contract

Read `references/story-and-beat-design.md` and the retrospective’s “visible event” rules. Convert the source into `story-manifest.json`; start from `assets/project-template/manifests/story-manifest.example.json`. Lock the platform, aspect ratio, first-three-second hook, ending argument, and source/copyright boundary before generation.

Require each scene to contain a narrative goal and at least one event with `cause`, `action`, `result`, and `proof`. Add `propagation` whenever the result is not instantaneous. Validate before generating assets:

```bash
python3 scripts/validate_story_manifest.py story-manifest.json --strict
```

Obtain approval for the story action table before expensive generation.

### 2. Lock voice, speaker ownership, and timing

Read `references/voice-timing-and-subtitles.md`. Audition at least 3–5 voices per role with one representative paragraph that tests calm narration, emotional dialogue, sentence endings, and accent. When the user requests Fish Audio, search its public model market broadly, retain model IDs and public URLs, shortlist multiple candidates, render same-line tests, and reject celebrity imitation, dialect drift, advertising cadence, and unclear diction. Assign every line to a speaker before mixing, and generate the selected voice by scene at natural speed unless the user requests otherwise. Preserve a voice ledger and original dry stems. Never store credentials in the project or skill.

Probe delivered audio:

```bash
python3 scripts/probe_voice_timing.py assets/audio/*.mp3 --output voice-manifest.json
```

Write measured durations and audio paths back to the story manifest before building the full timeline.

### 3. Lock reference-only character identities

Read `references/character-and-pose-system.md` and `references/image-generation-prompts.md`. Generate one neutral frontal, preferably full-body identity image for each recurring character and record stable traits plus forbidden changes. Mark the image `purpose: identity-consistency-reference-only` and `animation_use: false`. Obtain approval before producing the benchmark shot.

Do not generate side views, gait cycles, expressions, action poses, chroma atlases, props, backgrounds, or effects at this stage. Do not place the frontal identity image in the animation. It exists only to condition later shot-specific generation.

### 4. Plan and generate one shot at a time

Treat each `scene` entry in the manifest as one production shot unless the project explicitly subdivides it. Read `references/shot-spatial-contract.md`, then write and approve the shot’s semantic event, top-down plan, camera-facing plan, and `spatial_contract`.

Before generation, prove:

- start and end zones fit inside the frame and intended motion corridor;
- the corridor remains clear of non-passable obstacles and is wide enough for the actor or shared load;
- travel vector, facing, gaze, camera side, entry, and exit agree;
- every action target exists, supports the narrated action, is reachable, and stays readable;
- the background reserves the path, target, proof frame, head/face-safe region, and subtitle-safe zones;
- `review_contract` protects head and face and declares every intentional occlusion.

Only after `asset_plan.space_approved: true`, list the minimum assets required by that shot and generate them using the approved frontal identity reference. For every critical prop, write its real-world class, silhouette, scale reference, material cues, support/attachment points, state sequence, and proof frame before generation. Generate coupled actors plus a shared load as one connected ensemble. Generate a full-scene multi-frame state when contact or perspective is fragile. Keep backgrounds free of characters, text, watermarks, and story-critical effects unless the approved full-scene decision requires them.

Do not ask an image model to improvise important writing, official notices, maps, currency, treasure, weapons, plants, or symbolic connectors. Generate a historically credible blank base when needed, then typeset or composite verified content deterministically. Reject graphic shorthand that cannot be recognized with sound muted.

Prepare shot-specific atlases and keyed assets only after that gate:

```bash
python3 scripts/remove_chroma_key.py atlas-magenta.png atlas-alpha.png --key-color '#ff00ff'
python3 scripts/split_pose_atlas.py atlas-alpha.png poses --cols 3 --rows 2 --trim --padding 16
python3 scripts/audit_asset_integrity.py poses --kind character --strict
```

Reject and regenerate assets that fail identity, orientation, camera, scale, light, contact, target, crop, or semantics. Never force a wrong-direction asset into the timeline because it already exists.

### 5. Prove the benchmark shot

Choose the scene with the hardest contact, shared load, water, fire, destruction, or handoff. Build only 8–15 seconds first. It must prove:

- stable character identity and complete heads, hands, and feet;
- no half-face, sliced scalp, or amputated-head effect at first, midpoint, pose-change, occlusion-boundary, proof, and transition frames;
- correct hand/shoulder/prop contact;
- readable cause, action, and result without narration;
- at least six useful depth/physical layers where the scene benefits from them;
- correct container masks, prop ownership, and effect origins;
- narration, subtitle, and transition timing.
- muted proof of the event chain and a voice-only check for speaker ownership, accent, and overlap.

Do not expand to the full film until this benchmark is approved. Afterward, keep the same gate for every shot: contract → minimum assets → animation → rendered MP4 → muted/voice/combined/reality review → release record → next shot.

### 6. Build the deterministic project

Read `references/layers-physics-and-occlusion.md` and `references/hyperframes-production.md`. Scaffold a generic project:

```bash
python3 scripts/init_paper_project.py --manifest story-manifest.json --output ./my-paper-story
```

Rebuild only the generic scene hosts and timing skeleton when the manifest changes:

```bash
python3 scripts/build_hyperframes_timeline.py --manifest story-manifest.json --project ./my-paper-story
```

Replace development placeholders with generated assets and seek-safe scene motion. Keep audio as direct children of the top-level composition root. Give each scene a motion sidecar with selectors that prove actual story actions.

### 7. Animate physical relationships and normalized movement

Read `references/semantic-action-checks.md`. For every moving prop, define ownership and lifecycle: `source → owner → handoff → target → exit/rest`. For every standing or walking subject, declare the support surface and review feet/hooves/wheels/contact shadows against it. For every walking character, use a normalized complete-body gait cycle and check feet baseline, support foot, facing, torso direction, and world-space travel. For water, fire, impact, breakage, light, shadow, weapons, plants, documents, treasure, and load, animate visible cause and feedback rather than swapping decorative stickers.

### 8. Fit picture to narration

Run the pacing audit after scene timing and activity windows are present:

```bash
python3 scripts/audit_pacing.py story-manifest.json --voice-manifest voice-manifest.json --output PACE-AUDIT.md --strict
```

Cut within roughly 0.6–1.2 seconds after semantic completion unless a new action, sound, or transition carries the interval. Do not count paper grain, dust, or slow parallax as story activity.

### 9. Pass the quality gates

Read `references/quality-gates-and-delivery.md` and the retrospective’s three-read review. Pass in order:

- P0 semantic clarity and required-object recognizability;
- P1 identity, real-world proportion, ground/support contact, occlusion, and physical continuity;
- P2 motion, voice, captions, pacing, and transitions;
- P3 HyperFrames checks, final-MP4 frame review, expected-line/audio-stem audit, watermark, and delivery.

Add a project-specific failure log when a preview exposes a wrong spatial relation, character drift, dialect, caption occlusion, or stale-cache problem. Convert each repeated failure into a rule or a new manifest field before continuing.

Create one shot-release record from `assets/project-template/manifests/shot-release.example.json`, then enforce the next-shot lock:

```bash
python3 scripts/audit_shot_release.py shots/scene-xx/shot-release.json --strict
```

The record must point to the rendered MP4, first/midpoint/contact/proof/final frames, critical-prop specifications, expected voice lines, and all review results. Do not start the next shot until this command passes.

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
- HyperFrames project and timeline contract: `references/hyperframes-production.md`
- Semantic proof and action-specific checks: `references/semantic-action-checks.md`
- P0–P3 acceptance and delivery: `references/quality-gates-and-delivery.md`
- Per-shot release template: `assets/project-template/manifests/shot-release.example.json`

## Delivery posture

Preserve the editable project, reference-only frontal identity images, per-shot spatial contracts, approved shot asset sidecars, approved voice files, source atlases, alpha assets, high-quality master, and social derivative. Treat generated social files as disposable derivatives and the master as the archival source.
