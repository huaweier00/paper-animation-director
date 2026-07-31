# Rive linear-character benchmark

This benchmark uses the low-level `@rive-app/canvas-advanced-single` runtime and an
official `rive-app/rive-wasm` example asset. It does not run a state machine or
a free-running animation loop. Every HyperFrames `hf-seek` resets the
`LinearAnimationInstance` to zero, advances to the requested absolute time,
applies the keys, advances the artboard, and draws one frame.

Asset provenance:

- source repository: `https://github.com/rive-app/rive-wasm`
- source path: `wasm/examples/centaur_game/centaur.riv`
- source artboard and animation: `Character` / `Walk`
- repository license: MIT

Run:

```bash
npm install
npx hyperframes check
npx hyperframes snapshot --at 0.1,0.7,1.4,2.2 --no-end
```

Repeat the same timestamps in a different order and compare PNG hashes. A
state-machine-based character must be pre-rendered unless its entire state can
be reconstructed from absolute time and fixed inputs.
