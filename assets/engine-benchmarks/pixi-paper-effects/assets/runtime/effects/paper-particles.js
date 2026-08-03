import {
  clamp,
  finite,
  lerp,
  seededRange,
  seededUnit,
} from "../deterministic.js";

const PRESETS = Object.freeze({
  "hoof-dust": {
    count: 34,
    emissionWindow: 0.34,
    lifetime: [0.72, 1.28],
    velocityX: [-0.20, 0.05],
    velocityY: [-0.16, -0.035],
    gravity: 0.18,
    drift: 0.024,
    size: [0.018, 0.052],
    stretch: [1.4, 2.6],
    colors: [0x8d6b46, 0xa9845a, 0xc2a174],
  },
  "impact-dust": {
    count: 58,
    emissionWindow: 0.18,
    lifetime: [0.82, 1.55],
    velocityX: [-0.24, 0.24],
    velocityY: [-0.28, -0.07],
    gravity: 0.25,
    drift: 0.035,
    size: [0.022, 0.065],
    stretch: [1.1, 2.2],
    colors: [0x76563b, 0x9b7651, 0xc29d72],
  },
  snow: {
    count: 86,
    emissionWindow: 2.4,
    lifetime: [2.7, 4.4],
    velocityX: [-0.035, 0.055],
    velocityY: [0.08, 0.17],
    gravity: 0.006,
    drift: 0.055,
    size: [0.004, 0.013],
    stretch: [0.8, 1.25],
    colors: [0xf8f3e6, 0xeee8d8, 0xffffff],
  },
  embers: {
    count: 42,
    emissionWindow: 0.9,
    lifetime: [1.0, 2.2],
    velocityX: [-0.05, 0.05],
    velocityY: [-0.23, -0.08],
    gravity: -0.012,
    drift: 0.06,
    size: [0.004, 0.012],
    stretch: [0.8, 1.4],
    colors: [0xffc15a, 0xe8682a, 0xffe0a1],
  },
  "ink-motes": {
    count: 28,
    emissionWindow: 0.6,
    lifetime: [1.3, 2.8],
    velocityX: [-0.08, 0.08],
    velocityY: [-0.12, 0.025],
    gravity: 0.035,
    drift: 0.075,
    size: [0.008, 0.03],
    stretch: [0.7, 1.7],
    colors: [0x241d19, 0x44352d, 0x5d4b40],
  },
  "paper-scraps": {
    count: 38,
    emissionWindow: 0.42,
    lifetime: [1.2, 2.4],
    velocityX: [-0.16, 0.16],
    velocityY: [-0.26, -0.06],
    gravity: 0.22,
    drift: 0.08,
    size: [0.012, 0.032],
    stretch: [1.5, 3.4],
    colors: [0xd8b77b, 0xb9894f, 0x86372c, 0x4e2d25],
  },
  "falling-leaves": {
    count: 48,
    emissionWindow: 2.8,
    lifetime: [2.4, 4.8],
    velocityX: [-0.06, 0.09],
    velocityY: [0.08, 0.2],
    gravity: 0.008,
    drift: 0.12,
    size: [0.009, 0.024],
    stretch: [1.2, 2.1],
    colors: [0x9b6a35, 0xb24a2f, 0x6e542d, 0xc58a3d],
  },
  "rain-streaks": {
    count: 96,
    emissionWindow: 1.8,
    lifetime: [0.65, 1.2],
    velocityX: [0.04, 0.08],
    velocityY: [0.42, 0.7],
    gravity: 0.02,
    drift: 0.008,
    size: [0.003, 0.008],
    stretch: [5.5, 10],
    colors: [0x9fb3b8, 0xb9c8c9, 0x7f979e],
  },
  "smoke-wisps": {
    count: 44,
    emissionWindow: 1.2,
    lifetime: [1.8, 3.8],
    velocityX: [-0.04, 0.06],
    velocityY: [-0.2, -0.07],
    gravity: -0.01,
    drift: 0.1,
    size: [0.025, 0.07],
    stretch: [1.3, 2.8],
    colors: [0x5d554d, 0x756b60, 0x8f8375],
  },
});

function presetFor(name) {
  const preset = PRESETS[name];
  if (!preset) {
    throw new Error(`Unknown paper particle preset: ${name}`);
  }
  return preset;
}

function normalizeEmitter(input, frame) {
  if (!input || typeof input !== "object") {
    throw new TypeError("paper particle emitter must be an object");
  }
  const presetName = String(input.preset || "").trim();
  const preset = presetFor(presetName);
  const width = Math.max(1, finite(frame?.width, 1920));
  const height = Math.max(1, finite(frame?.height, 1080));
  const start = Math.max(0, finite(input.start, 0));
  const duration = Math.max(0.001, finite(input.duration, 1.5));
  const origin = Array.isArray(input.origin) ? input.origin : [0.5, 0.72];
  return {
    id: String(input.id || `${presetName}-emitter`).trim(),
    preset: presetName,
    seed: String(input.seed || input.id || presetName),
    count: Math.max(1, Math.floor(finite(input.count, preset.count))),
    start,
    duration,
    originX: clamp(origin[0], -0.25, 1.25) * width,
    originY: clamp(origin[1], -0.25, 1.25) * height,
    width,
    height,
    emissionWindow: Math.min(
      duration,
      Math.max(0, finite(input.emissionWindow, preset.emissionWindow)),
    ),
    opacity: clamp(input.opacity ?? 1, 0, 1),
    presetData: preset,
  };
}

function particleBlueprint(emitter, index) {
  const preset = emitter.presetData;
  const seed = `${emitter.seed}:${index}`;
  const colorIndex = Math.floor(
    seededUnit(seed, 0) * preset.colors.length,
  ) % preset.colors.length;
  return {
    index,
    birthOffset: seededRange(
      seed,
      1,
      0,
      emitter.emissionWindow,
    ),
    lifetime: seededRange(seed, 2, preset.lifetime[0], preset.lifetime[1]),
    vx: seededRange(seed, 3, preset.velocityX[0], preset.velocityX[1]) * emitter.width,
    vy: seededRange(seed, 4, preset.velocityY[0], preset.velocityY[1]) * emitter.height,
    gravity: preset.gravity * emitter.height,
    drift: preset.drift * emitter.width,
    driftPhase: seededRange(seed, 5, 0, Math.PI * 2),
    driftCycles: seededRange(seed, 6, 0.7, 1.9),
    size: seededRange(seed, 7, preset.size[0], preset.size[1]) * Math.min(emitter.width, emitter.height),
    stretch: seededRange(seed, 8, preset.stretch[0], preset.stretch[1]),
    rotation: seededRange(seed, 9, -Math.PI, Math.PI),
    spin: seededRange(seed, 10, -2.2, 2.2),
    color: preset.colors[colorIndex],
    originJitterX: seededRange(seed, 11, -0.018, 0.018) * emitter.width,
    originJitterY: seededRange(seed, 12, -0.012, 0.012) * emitter.height,
  };
}

function createEmitter(input, frame) {
  const emitter = normalizeEmitter(input, frame);
  return {
    ...emitter,
    particles: Array.from(
      { length: emitter.count },
      (_, index) => particleBlueprint(emitter, index),
    ),
  };
}

function alphaEnvelope(progress) {
  const fadeIn = clamp(progress / 0.14, 0, 1);
  const fadeOut = clamp((1 - progress) / 0.42, 0, 1);
  return Math.min(fadeIn, fadeOut);
}

function sampleParticle(emitter, particle, localTime) {
  const age = finite(localTime, 0) - emitter.start - particle.birthOffset;
  const effectiveLifetime = Math.min(particle.lifetime, emitter.duration - particle.birthOffset);
  if (age < 0 || age > effectiveLifetime || effectiveLifetime <= 0) {
    return {
      visible: false,
      x: emitter.originX,
      y: emitter.originY,
      scaleX: 0,
      scaleY: 0,
      rotation: particle.rotation,
      alpha: 0,
      color: particle.color,
    };
  }
  const progress = clamp(age / effectiveLifetime, 0, 1);
  const drift =
    Math.sin(progress * Math.PI * 2 * particle.driftCycles + particle.driftPhase)
    * particle.drift
    * Math.sin(progress * Math.PI);
  const expansion = lerp(0.68, 1.22, Math.sin(progress * Math.PI * 0.5));
  return {
    visible: true,
    x: emitter.originX + particle.originJitterX + particle.vx * age + drift,
    y:
      emitter.originY
      + particle.originJitterY
      + particle.vy * age
      + 0.5 * particle.gravity * age * age,
    scaleX: particle.size * particle.stretch * expansion,
    scaleY: particle.size * expansion,
    rotation: particle.rotation + particle.spin * age,
    alpha: alphaEnvelope(progress) * emitter.opacity,
    color: particle.color,
  };
}

function sampleEmitter(emitter, localTime) {
  return emitter.particles.map((particle) =>
    sampleParticle(emitter, particle, localTime),
  );
}

export {
  PRESETS,
  createEmitter,
  normalizeEmitter,
  presetFor,
  sampleEmitter,
  sampleParticle,
};
