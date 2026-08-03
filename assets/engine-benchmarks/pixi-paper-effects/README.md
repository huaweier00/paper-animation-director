# PixiJS deterministic paper-effects benchmark

This benchmark mounts the bundled `pixijs-webgpu` adapter with a fixed-seed
impact-dust emitter. Particle birth, lifetime, position, rotation, scale,
opacity and tint are sampled directly from absolute HyperFrames seconds. The
Pixi ticker is stopped; there is no free-running animation loop or accumulated
particle state.

Run:

```bash
npm install
npx hyperframes check --strict
npx hyperframes snapshot --at 0.1,0.9,1.8,2.7 --no-end
```

Repeat the timestamps in a different order and compare PNG hashes. A
previous-frame filter or feedback simulation must be reconstructable from
absolute time or delivered as a pre-render.
