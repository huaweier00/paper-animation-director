# HyperFrames production

Read the active HyperFrames skills before authoring, checking, previewing, or rendering. This reference adds paper-story conventions; it does not replace the HyperFrames contract.

## Project shape

Use one standalone root `index.html` and one sub-composition per story scene. Keep scene IDs, host IDs, template IDs, and timeline registry keys exact. Put all audio tracks directly under the standalone root.

Maintain global layers for captions, short chapter tags, transitions, paper grain, and watermark. Do not add a progress bar or permanent presentation chrome.

## Scene internals

Build every scene synchronously with one paused registered GSAP timeline. Use block-level sized wrappers. Animate visual channels and nested wrappers, not `.clip` lifecycle. Keep full-frame fills on children rather than the root.

Use complete pose images as state frames. Crossfade only when replacement is the intended pose change; keep the overlap short and preserve world position. Prefer one connected transform path for travel, with secondary bob, load, rope, or water motion on nested elements.

When an approved `engine-plan.json` selects a specialized layer, follow `hybrid-shot-pipeline.md` instead of forcing the requirement into pose replacement or whole-image transforms. Keep GSAP for shot orchestration and DOM overlays. Drive Rive/Spine, PixiJS, and Three.js from absolute shot-local time through `hf-seek` or the bundled hybrid runtime. Bake Blender and every history-dependent simulation before assembly.

## Motion proof

Create a `*.motion.json` sidecar for each scene. Assert real story selectors: lamp fall, bucket arrival, water stream, fire reduction, prop contact, final pose, or another observable event. A helper or decorative particle is not proof.

## Validation loop

Run the project wrapper when present:

```bash
npm run check -- --samples 25
```

Capture each scene midpoint, each transition boundary, every proof frame, the first frame, final-minus-hold, and exact final. Use focused keyframe shots for contact and paths. Review the assembled pixels, not only logs.

For every embedded specialized engine, also seek proof times in non-sequential order and compare repeated captures at the same timestamp. A live preview that only works after playing from frame zero is a failed deterministic integration.

Render only after the complete Studio preview is approved. Extract frames from the resulting MP4 and verify audio streams with FFprobe.
