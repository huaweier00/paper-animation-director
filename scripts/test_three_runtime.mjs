import assert from "node:assert/strict";
import test from "node:test";

import {
  createSeekableThreeScene,
} from "../assets/project-template/runtime/adapters/three-seekable.js";
import {
  normalizeSceneManifest,
} from "../assets/project-template/runtime/scenes/declarative-paper-2_5d.js";


test("Three adapter initializes once and renders directly from absolute time", async () => {
  const calls = [];
  const renderer = {
    backend: { isWebGPUBackend: true },
    info: { render: { calls: 1 } },
    setPixelRatio(value) {
      calls.push(["pixelRatio", value]);
    },
    setSize(width, height, updateStyle) {
      calls.push(["size", width, height, updateStyle]);
    },
    async init() {
      calls.push(["init"]);
    },
    setClearColor(color, alpha) {
      calls.push(["clear", color, alpha]);
    },
    async compileAsync() {
      calls.push(["compile"]);
    },
    render() {
      calls.push(["render"]);
    },
    dispose() {
      calls.push(["renderer.dispose"]);
    },
  };
  const updates = [];
  const sceneSpec = {
    scene: {},
    camera: {},
    updateAt(local, global) {
      updates.push([local, global]);
    },
    dispose() {
      calls.push(["scene.dispose"]);
    },
  };
  const canvas = { width: 960, height: 540, dataset: {} };
  const THREE = {
    WebGPURenderer: class {},
    SRGBColorSpace: "srgb",
  };
  const adapter = await createSeekableThreeScene({
    THREE,
    canvas,
    width: 960,
    height: 540,
    sceneFactory: async () => sceneSpec,
    rendererFactory: () => renderer,
  });

  updates.length = 0;
  adapter.renderAt(1.25, 4.5);
  adapter.renderAt(0.2, 3.45);
  adapter.renderAt(1.25, 4.5);
  assert.deepEqual(updates, [[1.25, 4.5], [0.2, 3.45], [1.25, 4.5]]);
  assert.equal(canvas.dataset.threeBackend, "webgpu");
  assert.equal(canvas.dataset.threeTime, "1.250000");
  assert.equal(globalThis.requestAnimationFrame, undefined);
  adapter.destroy();
  assert.equal(canvas.dataset.threeReady, "false");
});


test("declarative Three scene normalizes depth layers without runtime state", () => {
  const manifest = normalizeSceneManifest({
    schema_version: 1,
    scene_id: "depth-test",
    camera: {
      kind: "perspective",
      fov_degrees: 38,
      near: 0.1,
      far: 80,
      position: [0, 1, 9],
      look_at: [0, 0, 0],
    },
    layers: [
      {
        id: "back",
        kind: "plane",
        depth: -2,
        size: [10, 6],
        motion: { kind: "static" },
      },
      {
        id: "hero",
        kind: "shape",
        depth: 0,
        points: [[0, 0], [1, 0], [0, 1]],
        motion: { kind: "bob", axis: "y", amplitude: 0.1, frequency: 2 },
      },
    ],
  });
  assert.equal(manifest.sceneId, "depth-test");
  assert.equal(manifest.layers.length, 2);
  assert.deepEqual(manifest.layers.map((item) => item.depth), [-2, 0]);
  assert.equal(manifest.layers[1].motion.kind, "bob");
});
