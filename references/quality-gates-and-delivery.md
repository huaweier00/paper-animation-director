# Quality gates and delivery

## P0 — semantic clarity

- The story remains broadly understandable with audio muted.
- Every key verb has an observable proof frame or interval.
- Actor, object, cause, and result are unambiguous.
- Shared work, refusal, rotation, rescue, and other relational actions are staged rather than merely narrated.

Stop and restage when P0 fails.

Run a muted visual pass before adding polish. If a reviewer cannot identify actor, location, action, and result without narration, the scene is not ready for effects, music, or final typography.

## P1 — identity and physical continuity

- Character identity, anatomy, costume, and scale remain stable.
- Heads and feet are complete; no chroma plate or rectangular residue remains.
- Hands, shoulders, ropes, poles, containers, and shared loads make contact.
- Water is inside containers; effects originate and land correctly.
- Prop ownership and retirement are deterministic.
- Foreground occlusion, rim masks, and contact shadows place subjects in one space.

## P2 — motion, voice, and pacing

- Pose phases and travel agree.
- No teleport, unexplained duplicate, frozen tail, or decorative-only dead zone remains.
- Narration uses approved natural playback and measured timing.
- Caption changes do not overlap unreadably.
- Scene completion is followed by a cut, earned reaction, or transition within roughly 0.6–1.2 seconds.
- Transitions clarify continuity, time, location, or energy instead of imitating slides.
- Voice-only review confirms speaker ownership, accent, emotional register, and absence of overlap.
- Captions default to centered safe placement and do not cover proof contacts or get clipped at the frame edge.

## P3 — technical delivery

- HyperFrames strict check passes.
- Keyframe diagnostics and focused shots prove real action selectors.
- Midpoints, transitions, proof frames, first frame, final-minus-hold, and final frame are visually reviewed.
- Frames extracted from the rendered MP4 match the approved preview.
- Never treat a stale Studio tab, a local file preview, or one unrendered screenshot as delivery proof; refresh the project server and inspect rendered-MP4 frames.
- FFprobe confirms plausible duration, resolution, frame rate, and intended audio streams.
- Moving watermark is visible on both light and dark rendered frames while avoiding captions and sustained face coverage.
- The archival master is preserved.
- The social H.264 derivative uses Fast Start and reaches the configured VMAF floor, normally 95 or higher.

## Handoff

Report project path, preview URL, master path, social path, dimensions, fps, duration, codecs, audio mode, watermark text/settings, file sizes, compression ratio, VMAF, and any intentional limitations. A moving watermark raises removal cost but cannot prevent manual reconstruction.
