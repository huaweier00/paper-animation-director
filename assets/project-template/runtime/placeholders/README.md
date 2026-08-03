# Runtime gate media

`pending-blender.webm` is a 16×16, 60-second, local VP9 placeholder used only
while a Blender route is waiting for its baked per-shot media. HyperFrames
requires a compile-time `src` on timed video elements. The hybrid scaffold
records the real required asset separately and replaces `video.src` only when
the shot's `engine-inputs.json` Blender gate is explicitly marked ready.

The placeholder is not production content and must never satisfy
`engine_plan_fulfilled` or the shot release gate.
