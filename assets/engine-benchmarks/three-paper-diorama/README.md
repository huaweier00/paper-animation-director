# Three.js WebGPU 2.5D paper-diorama benchmark

This benchmark uses the `three/webgpu` build. `WebGPURenderer` selects WebGPU
when available and falls back to its WebGL 2 backend; the selected backend is
recorded on the canvas. The renderer is initialized and compiled before it is
registered with HyperFrames.

There is no `Clock`, `requestAnimationFrame`, animation loop, or accumulated
simulation. At every `hf-seek`, camera position, parallax, paper character,
limbs, light, and particles are derived directly from absolute seconds.

Run:

```bash
npm install
npx hyperframes check
npx hyperframes snapshot --at 0.1,0.9,1.8,2.7 --no-end
```

Repeat those times in a different order and compare PNG hashes. Temporal
accumulation, feedback buffers, fluid solvers, and previous-frame effects must
be baked instead of added to this live scene.
