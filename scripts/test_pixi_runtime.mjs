import assert from "node:assert/strict";
import test from "node:test";

import {
  createEmitter,
  sampleEmitter,
} from "../assets/project-template/runtime/effects/paper-particles.js";
import {
  normalizeMask,
} from "../assets/project-template/runtime/effects/paper-masks.js";

class FakeParticle {
  constructor(options = {}) {
    this._alpha = options.alpha ?? 1;
    this._tint = options.tint ?? 0xffffff;
    Object.assign(this, options);
    this._updateColor();
  }

  _updateColor() {
    this.color = this._tint + ((this._alpha * 255 | 0) << 24);
  }

  get alpha() {
    return this._alpha;
  }

  set alpha(value) {
    this._alpha = Math.min(1, Math.max(0, value));
    this._updateColor();
  }

  get tint() {
    return this._tint;
  }

  set tint(value) {
    this._tint = value;
    this._updateColor();
  }
}

class FakeParticleContainer {
  constructor(options = {}) {
    this.options = options;
    this.particleChildren = [];
  }

  addParticle(particle) {
    this.particleChildren.push(particle);
  }
}

class FakeApplication {
  constructor() {
    this.renderCount = 0;
    this.stage = {
      children: [],
      addChild: (child) => this.stage.children.push(child),
    };
  }

  async init(options) {
    this.options = options;
  }

  stop() {}

  render() {
    this.renderCount += 1;
  }

  destroy() {}
}

class FakeGraphics {
  rect(...args) {
    this.shape = ["rect", ...args];
    return this;
  }

  circle(...args) {
    this.shape = ["circle", ...args];
    return this;
  }

  poly(...args) {
    this.shape = ["poly", ...args];
    return this;
  }

  fill(color) {
    this.fillColor = color;
    return this;
  }
}

globalThis.HTMLCanvasElement = class HTMLCanvasElement {};

const fakePixi = {
  Application: FakeApplication,
  Graphics: FakeGraphics,
  Particle: FakeParticle,
  ParticleContainer: FakeParticleContainer,
  Rectangle: class Rectangle {
    constructor(x, y, width, height) {
      Object.assign(this, { x, y, width, height });
    }
  },
  Texture: { WHITE: { id: "white" } },
};

test("paper particle sampling is identical after non-sequential seeks", () => {
  const emitter = createEmitter(
    {
      id: "impact",
      preset: "impact-dust",
      seed: "fixed-seed",
      origin: [0.5, 0.8],
      start: 0.4,
      duration: 1.8,
      count: 12,
    },
    { width: 1920, height: 1080 },
  );
  const midpointA = sampleEmitter(emitter, 1.1);
  sampleEmitter(emitter, 0);
  sampleEmitter(emitter, 2.1);
  const midpointB = sampleEmitter(emitter, 1.1);
  assert.deepEqual(midpointA, midpointB);
  assert(midpointA.some((state) => state.visible));
});

test("different fixed seeds produce different particle layouts", () => {
  const input = {
    id: "snow",
    preset: "snow",
    origin: [0.5, 0],
    start: 0,
    duration: 4,
    count: 8,
  };
  const first = createEmitter(
    { ...input, seed: "a" },
    { width: 800, height: 600 },
  );
  const second = createEmitter(
    { ...input, seed: "b" },
    { width: 800, height: 600 },
  );
  assert.notDeepEqual(sampleEmitter(first, 1.5), sampleEmitter(second, 1.5));
});

test("Pixi adapter renders from supplied absolute local time without a ticker", async () => {
  const { createPixiPaperEffects } = await import(
    "../assets/project-template/runtime/adapters/pixi-seekable.js"
  );
  const canvas = new HTMLCanvasElement();
  canvas.width = 640;
  canvas.height = 360;
  canvas.dataset = {};
  const renderer = await createPixiPaperEffects({
    PIXI: fakePixi,
    canvas,
    width: 640,
    height: 360,
    effects: [
      {
        id: "dust",
        preset: "hoof-dust",
        seed: "dust-seed",
        origin: [0.5, 0.8],
        start: 0.2,
        duration: 1.4,
        count: 6,
        mask: "ground",
      },
    ],
    masks: [
      {
        id: "ground",
        kind: "band",
        origin: [0, 0.6],
        size: [1, 0.4],
      },
    ],
  });
  renderer.renderAt(0.8);
  const particleLayer = renderer.app.stage.children.find((item) => item.particleChildren);
  const stateA = particleLayer.particleChildren.map((item) => ({
    alpha: item.alpha,
    rotation: item.rotation,
    x: item.x,
    y: item.y,
  }));
  renderer.renderAt(0.1);
  renderer.renderAt(1.5);
  renderer.renderAt(0.8);
  const stateB = particleLayer.particleChildren.map((item) => ({
    alpha: item.alpha,
    rotation: item.rotation,
    x: item.x,
    y: item.y,
  }));
  assert.deepEqual(stateA, stateB);
  assert(
    particleLayer.particleChildren.some(
      (particle) => particle.alpha > 0 && (particle.color >>> 24) > 0,
    ),
  );
  assert.equal(renderer.app.options.autoStart, false);
  assert.equal(renderer.app.options.sharedTicker, false);
  assert.equal(renderer.app.renderCount, 5);
  assert.equal(particleLayer.mask.name, "paper-mask:ground");
});


test("paper mask normalization is deterministic and rejects inverted live masks", () => {
  const first = normalizeMask({
    id: "door",
    kind: "polygon",
    points: [[0.1, 0.2], [0.8, 0.2], [0.7, 0.9]],
  });
  const second = normalizeMask({
    id: "door",
    kind: "polygon",
    points: [[0.1, 0.2], [0.8, 0.2], [0.7, 0.9]],
  });
  assert.deepEqual(first, second);
  assert.equal(first.points.length, 3);
});


test("new paper effects remain absolute-time deterministic", () => {
  for (const preset of ["paper-scraps", "falling-leaves", "rain-streaks", "smoke-wisps"]) {
    const emitter = createEmitter(
      {
        id: preset,
        preset,
        seed: `fixed:${preset}`,
        origin: [0.5, 0.5],
        start: 0.2,
        duration: 3,
        count: 10,
      },
      { width: 960, height: 540 },
    );
    const expected = sampleEmitter(emitter, 1.1);
    sampleEmitter(emitter, 2.7);
    assert.deepEqual(sampleEmitter(emitter, 1.1), expected);
  }
});
