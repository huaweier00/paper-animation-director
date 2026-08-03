# Blender paper-impact benchmark

Generate the baked source, cache, RGBA frames, VP9-alpha layer, and manifest:

```bash
python3 ../../../scripts/render_blender_prerender.py \
  --output ./assets/blender
```

Then install the pinned local runtime and run the HyperFrames checks:

```bash
npm install
npx hyperframes check
npx hyperframes snapshot --at 0.1,0.84,1.36,1.96 --no-end
```

The benchmark is intentionally generated rather than shipping an unexplained
binary. `assets/blender/prerender-manifest.json` records the Blender version,
physics-bake status, frame range, hashes, codec, dimensions, and proof frames.
