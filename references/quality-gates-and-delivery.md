# Quality gates and delivery

## P0 — semantic clarity

- The story remains broadly understandable with audio muted.
- Every key verb has an observable proof frame or interval.
- Every narrated or plot-bearing noun is present, recognizable, and the correct object class.
- Actor, object, cause, and result are unambiguous.
- The visible action uses the semantic target named by narration and the shot contract; a window, doorway, or nearby prop cannot silently replace a required wall, seat, container, or other target.
- Weapons, plants, currency/treasure, official documents, vehicles, tools, and symbolic connectors use real construction, scale, material cues, support, and state changes rather than abstract lines, icons, piles, or placeholder marks.
- Shared work, refusal, rotation, rescue, and other relational actions are staged rather than merely narrated.
- A command that changes a group state shows the initial state, issuing gesture/line, propagated response, and readable final state.

Stop and restage when P0 fails.

Run a muted visual pass before adding polish. If a reviewer cannot identify actor, location, action, and result without narration, the scene is not ready for effects, music, or final typography.

## P1 — identity and physical continuity

- Character identity, anatomy, costume, and scale remain stable.
- The frontal identity image remains reference-only and never appears as a keyed, animated, or delivered shot layer.
- Heads and feet are complete; no chroma plate or rectangular residue remains.
- No frame edge, `overflow`, crop, alpha boundary, mask, matte, transition, foreground, subtitle, or watermark slices through the scalp, facial contour, eyes, nose, mouth, jaw, or neck and produces a half-face or amputated-head effect.
- Natural profile preserves coherent skull and facial anatomy. Any partial head/face occlusion has a visible physical occluder, declared depth order/time window/reason, and an unobstructed identity-proof frame before or after it.
- Actor start/end zones, travel direction, facing, feet, torso, gaze, and entry/exit agree with the approved spatial contract.
- Named motion corridors remain clear and provide enough room for the actor, costume, carried load, contact, and reaction.
- Every standing person, animal, wheel, vehicle, rooted plant, hanging object, and placed prop remains attached to its named support surface or attachment target.
- Feet, hooves, wheels, seats, roots, knots, bowstrings, containers, and contact shadows share credible perspective, scale, and load.
- Hands, shoulders, ropes, poles, containers, and shared loads make contact.
- Water is inside containers; effects originate and land correctly.
- Prop ownership and retirement are deterministic.
- Foreground occlusion, rim masks, and contact shadows place subjects in one space.

## P2 — motion, voice, and pacing

- Pose phases and travel agree.
- No wrong-facing asset is mirrored, rotated, translated, or otherwise force-fit without a documented symmetry, handedness, text, light, contact, and continuity audit.
- No teleport, unexplained duplicate, frozen tail, or decorative-only dead zone remains.
- Narration uses approved natural playback and measured timing.
- Caption changes do not overlap unreadably.
- Scene completion is followed by a cut, earned reaction, or transition within roughly 0.6–1.2 seconds.
- Transitions clarify continuity, time, location, or energy instead of imitating slides.
- Voice-only review confirms speaker ownership, accent, emotional register, and absence of overlap.
- The expected-line ledger confirms that every required narration and dialogue stem is present at the locked time; music-only or BGM replacement renders must not silently remove speech.
- Captions default to centered safe placement and do not cover proof contacts or get clipped at the frame edge.

## P3 — technical delivery

- HyperFrames strict check passes.
- Keyframe diagnostics and focused shots prove real action selectors.
- Midpoints, transitions, proof frames, first frame, final-minus-hold, and final frame are visually reviewed.
- Frames extracted from the rendered MP4 match the approved preview.
- Review first, midpoint, every pose change, intentional-occlusion entry/maximum/exit, proof, transition, and final frames. Enlarge each visible head and face enough to inspect scalp, facial contour, eyes, nose, mouth, jaw, neck connection, and mask edges.
- Never treat a stale Studio tab, a local file preview, or one unrendered screenshot as delivery proof; refresh the project server and inspect rendered-MP4 frames.
- FFprobe confirms plausible duration, resolution, frame rate, and intended audio streams.
- A full decode completes without errors; the final mix is compared with the expected voice ledger or voice-only reference mix so an audio stream containing only music cannot pass.
- Moving watermark is visible on both light and dark rendered frames while avoiding captions and sustained face coverage.
- The archival master is preserved.
- The social H.264 derivative uses Fast Start and reaches the configured VMAF floor, normally 95 or higher.
- Hand-painted line work, subtitle edges, faces, and low-contrast mineral colors remain intact in beginning/middle/climax/ending frames extracted from the compressed social file.

## Per-shot release rule

Release one shot at a time. The current shot must have:

- an approved semantic and spatial contract;
- approved shot-specific assets and critical-prop recognizability specs;
- a rendered draft MP4;
- muted, voice-only, combined, and real-world plausibility reviews;
- first, midpoint, contact, proof, and final extracted frames;
- a written `approved` decision.

Do not start the next shot while the current decision is `rejected`, `needs-fix`, or undocumented. When review finds a failure, return to the earliest responsible layer: script, spatial contract, prop spec, source asset, animation, audio, caption, or encode.

## Ending gate

Before final assembly, confirm that the ending contains:

1. a visible consequence of the climax;
2. source/cultural closure when the project promises it;
3. a concise, transferable lesson in narration and/or a readable final card.

An origin note, bibliography, or “the end” card alone does not complete an educational story. Put interaction prompts in the social package after the film has stated its own conclusion.

## Handoff

Report project path, preview URL, master path, watermarked master path, social path, dimensions, fps, duration, codecs, audio mode, expected/confirmed voice-line count, watermark text/settings, file sizes, compression ratio, VMAF, and any intentional limitations. Include title, description, and pinned-comment options when the destination is a social platform. A moving watermark raises removal cost but cannot prevent manual reconstruction.
