import assert from "node:assert/strict";
import test from "node:test";

import {
  createSeekableRiveLinearAnimation,
  normalizeRiveAnimationTime,
} from "../assets/project-template/runtime/adapters/rive-seekable.js";


test("Rive time normalization supports loop, clamp, and ping-pong", () => {
  assert.equal(normalizeRiveAnimationTime(2.5, 2, "loop"), 0.5);
  assert.equal(normalizeRiveAnimationTime(2.5, 2, "clamp"), 2);
  assert.equal(normalizeRiveAnimationTime(2.5, 2, "ping-pong"), 1.5);
  assert.equal(normalizeRiveAnimationTime(-1, 2, "loop"), 0);
  assert.throws(() => normalizeRiveAnimationTime(1, 2, "state-machine"), /Unsupported/);
});


test("Rive adapter resets and seeks from absolute time without a free-running loop", async () => {
  const calls = [];
  class FakeLinearAnimationInstance {
    constructor(definition) {
      this.name = definition.name;
      this.duration = 2;
      this.time = 0;
    }
    advance(value) {
      calls.push(["advance", value]);
      this.time += value;
    }
    apply(value) {
      calls.push(["apply", value, this.time]);
    }
    delete() {
      calls.push(["animation.delete"]);
    }
  }
  const artboard = {
    bounds: { minX: 0, minY: 0, maxX: 100, maxY: 100 },
    animationByName(name) {
      return { name };
    },
    advance(value) {
      calls.push(["artboard.advance", value]);
    },
    draw() {
      calls.push(["artboard.draw"]);
    },
    delete() {
      calls.push(["artboard.delete"]);
    },
  };
  const renderer = {
    clear() {
      calls.push(["clear"]);
    },
    save() {
      calls.push(["save"]);
    },
    align() {
      calls.push(["align"]);
    },
    restore() {
      calls.push(["restore"]);
    },
    flush() {
      calls.push(["flush"]);
    },
    delete() {
      calls.push(["renderer.delete"]);
    },
  };
  const file = {
    defaultArtboard() {
      return artboard;
    },
    delete() {
      calls.push(["file.delete"]);
    },
  };
  const runtime = {
    Fit: { contain: 1 },
    Alignment: { center: 2 },
    LinearAnimationInstance: FakeLinearAnimationInstance,
    makeRenderer() {
      return renderer;
    },
    async load() {
      return file;
    },
    resolveAnimationFrame() {
      calls.push(["resolve"]);
    },
  };
  const canvas = { width: 960, height: 540, dataset: {} };
  const adapter = await createSeekableRiveLinearAnimation({
    RiveCanvas: async () => runtime,
    canvas,
    src: "./bird.riv",
    wasmUrl: "./rive.wasm",
    animationName: "idle",
    animationDuration: 2,
    playback: "loop",
    fetchImpl: async () => ({ ok: true, arrayBuffer: async () => new ArrayBuffer(8) }),
  });

  calls.length = 0;
  adapter.renderAt(1.4);
  adapter.renderAt(0.3);
  adapter.renderAt(1.4);
  const advances = calls.filter(([name]) => name === "advance").map(([, value]) => value);
  assert.deepEqual(advances, [1.4, 0.3, 1.4]);
  const applies = calls.filter(([name]) => name === "apply").map(([, , time]) => time);
  assert.deepEqual(applies, [1.4, 0.3, 1.4]);
  assert.equal(canvas.dataset.riveTime, "1.400000");
  assert.equal(globalThis.requestAnimationFrame, undefined);
  adapter.destroy();
  assert.equal(canvas.dataset.riveReady, "false");
});
