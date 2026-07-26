---
name: paper-animation-director
description: Turn a story, folktale, fable, script, or narration into a historically and physically credible multi-layer paper-cut animation with consistent recurring characters, spatial-first scene plans, connected full-body pose atlases, normalized gait frames, ensemble contact poses, full-scene multi-frame states, independent props and physical effects, narration-driven HyperFrames timing, standard-voice auditions, centered subtitles, semantic action checks, dynamic watermarking, and master/social delivery. Use when the user asks for 纸片动画, 剪纸动画, 宣纸水彩故事, paper-theatre animation, an illustrated folktale, a non-heritage or historical craft film, a layered recurring-character story, or a narrative animation whose actions must remain physically and semantically readable.
---

# Paper Animation Director

Build recurring-character story animation, not a sequence of moving posters. Preserve character identity and action meaning before adding decorative motion.

The production retrospective in `references/production-retrospective.md` is part of this skill, not optional background reading. It captures the spatial, historical, asset, motion, voice, subtitle, preview, and review rules learned from a full paper-shadow production.

## Route correctly

- Use this skill for continuous stories with recurring characters, props, causes, actions, and consequences.
- Use `vox-director` instead for editorial collage explainers whose primary unit is a poster-like beat.
- Use the `imagegen` skill for raster asset generation and editing.
- Use `hyperframes`, `hyperframes-core`, `hyperframes-animation`, `hyperframes-keyframes`, `hyperframes-creative`, and `hyperframes-cli` as required by the active production stage.
- Use `dynamic-video-watermark` for the final moving ownership mark. Do not duplicate its implementation here.

## Non-negotiable rules

1. Treat multilayer animation as separation by depth and physical responsibility, not as permission to cut a person into pieces.
2. Use complete connected character poses by default. Never reconstruct a hero from independently generated head, torso, arms, and legs when seams will be visible.
3. Generate a connected ensemble pose or ensemble pose atlas for shared-load actions such as carrying, lifting, embracing, rescuing, or handing off a heavy object.
4. Separate only elements that need independent motion: foreground, atmosphere, props, rope, water, fire, smoke, shadows, particles, captions, and watermark.
5. Express every important event as `cause → action → propagation → result`, with a proof frame that remains understandable when audio is muted.
6. Lock narration before final timing. Use measured audio duration; do not stretch voice or pad scenes to an arbitrary target.
7. Do not use whole-frame image-to-video as the default animation engine. Keep story-critical characters, captions, and props on deterministic, seek-safe timelines.
8. Do not render a full film before the hardest 8–15 second benchmark scene passes continuity, physics, timing, and subtitle review.
9. Draw a top-down spatial plan and a front-facing camera plan before generating a background. Mark the floor line, sight axis, light axis, actor paths, contact distances, occlusions, and subtitle-safe zones.
10. Treat historical accuracy as an adopt/reject contract: every period claim needs a source or explicit rationale, and every tempting later-period prop, floor, roof, stage, costume, or furniture choice must be rejected or justified.
11. Prefer a complete full-scene plate when bed, bedding, canopy, character, furniture, or light contact would be fragile as separate layers. Prefer independent complete characters only when they must travel, react, or change pose.
12. A lamp and its flame are one causal unit by default. A character is one connected body by default. A shared lift, restraint, carry, handoff, or embrace is one connected ensemble by default.
13. Never simulate walking with translation-only tweens. Use a normalized complete-body gait cycle with shared canvas, center, feet baseline, and facing direction; animate the cycle on a world-space parent track.
14. Choose a side or three-quarter side camera when two characters must both be readable. Do not let head, shoulder, chest, feet, and gaze point in conflicting directions during approach or confrontation.
15. Do not reuse an existing asset merely because it is available. Suitability for the current space, scale, period, lighting, orientation, and action outranks reuse.
16. Assign every spoken line to a speaker and an audio stem. Audition for accent as well as tone; reject dialect or identity drift, keep narrator and character dialogue from overlapping, and default Chinese captions to bottom-center safe placement.
17. Every scene must pass three reads: muted visual proof, voice-only speaker/timing proof, and combined picture/sound/subtitle proof. A Studio screenshot is not delivery evidence; review frames from the rendered MP4.

## Workflow

### 0. Run the retrospective and production intake

Read `references/production-retrospective.md` before designing a new historical, non-heritage, or recurring-character paper story. Record the project’s aspect-ratio decision, historical evidence tier, adopt/reject list, spatial plan, asset architecture, voice policy, proof frames, and approval gates. Treat “looks nice” as insufficient evidence for a scene, asset, or motion choice.

### 1. Create the story contract

Read `references/story-and-beat-design.md` and the retrospective’s “visible event” rules. Convert the source into `story-manifest.json`; start from `assets/project-template/manifests/story-manifest.example.json`.

Require each scene to contain a narrative goal and at least one event with `cause`, `action`, `result`, and `proof`. Add `propagation` whenever the result is not instantaneous. Validate before generating assets:

```bash
python3 scripts/validate_story_manifest.py story-manifest.json --strict
```

Obtain approval for the story action table before expensive generation.

### 2. Lock voice, speaker ownership, and timing

Read `references/voice-timing-and-subtitles.md`. Audition 3–5 voices with one representative paragraph that tests calm narration, emotional dialogue, sentence endings, and accent. Check Mandarin/other language fit explicitly; a “deep” or “authoritative” label is not proof of standard pronunciation. Assign every line to a speaker before mixing, and generate the selected voice by scene at natural speed unless the user requests otherwise. Never store credentials in the project or skill.

Probe delivered audio:

```bash
python3 scripts/probe_voice_timing.py assets/audio/*.mp3 --output voice-manifest.json
```

Write measured durations and audio paths back to the story manifest before building the full timeline.

### 3. Build the spatial, character, and asset bible

Read `references/character-and-pose-system.md`, `references/image-generation-prompts.md`, and the retrospective’s spatial/asset decision matrix. Draw a top-down plan and a front-facing camera plan before generating any background. Generate one approved identity reference per recurring character, then generate complete pose atlases from that reference. If contact or perspective is fragile, generate a full-scene multi-frame state or a connected ensemble instead of separate cutouts.

For coupled actions, mark `ensemble_required: true` and generate the actors plus shared load as one connected composition. Keep backgrounds free of characters, text, watermarks, and story-critical effects.

Prepare generated atlases and keyed assets with the bundled scripts:

```bash
python3 scripts/remove_chroma_key.py atlas-magenta.png atlas-alpha.png --key-color '#ff00ff'
python3 scripts/split_pose_atlas.py atlas-alpha.png poses --cols 3 --rows 2 --trim --padding 16
python3 scripts/audit_asset_integrity.py poses --kind character --strict
```

### 4. Prove the benchmark scene

Choose the scene with the hardest contact, shared load, water, fire, destruction, or handoff. Build only 8–15 seconds first. It must prove:

- stable character identity and complete heads, hands, and feet;
- correct hand/shoulder/prop contact;
- readable cause, action, and result without narration;
- at least six useful depth/physical layers where the scene benefits from them;
- correct container masks, prop ownership, and effect origins;
- narration, subtitle, and transition timing.
- muted proof of the event chain and a voice-only check for speaker ownership, accent, and overlap.

Do not expand to the full film until this benchmark is approved.

### 5. Build the deterministic project

Read `references/layers-physics-and-occlusion.md` and `references/hyperframes-production.md`. Scaffold a generic project:

```bash
python3 scripts/init_paper_project.py --manifest story-manifest.json --output ./my-paper-story
```

Rebuild only the generic scene hosts and timing skeleton when the manifest changes:

```bash
python3 scripts/build_hyperframes_timeline.py --manifest story-manifest.json --project ./my-paper-story
```

Replace development placeholders with generated assets and seek-safe scene motion. Keep audio as direct children of the top-level composition root. Give each scene a motion sidecar with selectors that prove actual story actions.

### 6. Animate physical relationships and normalized movement

Read `references/semantic-action-checks.md`. For every moving prop, define ownership and lifecycle: `source → owner → handoff → target → exit/rest`. For every walking character, use a normalized complete-body gait cycle and check feet baseline, support foot, facing, torso direction, and world-space travel. For water, fire, impact, breakage, light, shadow, and load, animate visible cause and feedback rather than swapping decorative stickers.

### 7. Fit picture to narration

Run the pacing audit after scene timing and activity windows are present:

```bash
python3 scripts/audit_pacing.py story-manifest.json --voice-manifest voice-manifest.json --output PACE-AUDIT.md --strict
```

Cut within roughly 0.6–1.2 seconds after semantic completion unless a new action, sound, or transition carries the interval. Do not count paper grain, dust, or slow parallax as story activity.

### 8. Pass the quality gates

Read `references/quality-gates-and-delivery.md` and the retrospective’s three-read review. Pass in order:

- P0 semantic clarity;
- P1 identity, contact, occlusion, and physical continuity;
- P2 motion, voice, captions, pacing, and transitions;
- P3 HyperFrames checks, final-MP4 frame review, audio probing, watermark, and delivery.

Add a project-specific failure log when a preview exposes a wrong spatial relation, character drift, dialect, caption occlusion, or stale-cache problem. Convert each repeated failure into a rule or a new manifest field before continuing.

Create a contact sheet from proof times or explicit review times:

```bash
python3 scripts/make_review_contact_sheet.py --video final.mp4 --manifest story-manifest.json --output review.jpg
```

Always review frames extracted from the rendered MP4; a correct Studio preview alone is not delivery proof.

### 9. Deliver master and social versions

After final preview approval, render the high-quality master. Apply the reusable moving watermark when requested. Then make a separate H.264 social upload while preserving the master:

```bash
python3 scripts/encode_social_delivery.py master.mp4 social-1080p.mp4 --vmaf-floor 95
```

Report master and social paths, sizes, duration, resolution, frame rate, audio streams, watermark settings, compression ratio, and VMAF. Never overwrite the master.

## Resource map

- Story structure and timing policy: `references/story-and-beat-design.md`
- Project retrospective, historical/spatial rules, asset decisions, gait, voice, captions, preview, and failure patterns: `references/production-retrospective.md`
- Character continuity and ensemble poses: `references/character-and-pose-system.md`
- Image-generation prompt contracts: `references/image-generation-prompts.md`
- Layering, masks, water, fire, rope, and load: `references/layers-physics-and-occlusion.md`
- Voice auditions, measured timing, subtitles, and titles: `references/voice-timing-and-subtitles.md`
- HyperFrames project and timeline contract: `references/hyperframes-production.md`
- Semantic proof and action-specific checks: `references/semantic-action-checks.md`
- P0–P3 acceptance and delivery: `references/quality-gates-and-delivery.md`

## Delivery posture

Preserve the editable project, approved voice files, character references, source atlases, alpha assets, high-quality master, and social derivative. Treat generated social files as disposable derivatives and the master as the archival source.
