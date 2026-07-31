import {
  createEmitter,
  sampleEmitter,
} from "../effects/paper-particles.js";
import {
  createPixiMask,
} from "../effects/paper-masks.js";

function requirePixi(PIXI) {
  const required = [
    "Application",
    "Particle",
    "ParticleContainer",
    "Rectangle",
    "Texture",
  ];
  const missing = required.filter((name) => !PIXI?.[name]);
  if (missing.length) {
    throw new Error(`PixiJS adapter is missing: ${missing.join(", ")}`);
  }
}

function applyParticleState(particle, state, textureSize = 64) {
  particle.x = state.x;
  particle.y = state.y;
  particle.scaleX = state.scaleX / textureSize;
  particle.scaleY = state.scaleY / textureSize;
  particle.rotation = state.rotation;
  particle.alpha = state.alpha;
  particle.tint = state.color;
}

function createPaperTexture(PIXI) {
  if (typeof document === "undefined" || typeof PIXI.Texture.from !== "function") {
    return PIXI.Texture.WHITE;
  }
  const surface = document.createElement("canvas");
  surface.width = 64;
  surface.height = 64;
  const context = surface.getContext("2d");
  const gradient = context.createRadialGradient(32, 32, 3, 32, 32, 31);
  gradient.addColorStop(0, "rgba(255,255,255,.92)");
  gradient.addColorStop(0.52, "rgba(255,255,255,.68)");
  gradient.addColorStop(0.82, "rgba(255,255,255,.22)");
  gradient.addColorStop(1, "rgba(255,255,255,0)");
  context.fillStyle = gradient;
  context.fillRect(0, 0, 64, 64);
  return PIXI.Texture.from(surface);
}

async function createPixiPaperEffects(options) {
  const {
    PIXI,
    canvas,
    width = canvas?.width || 1920,
    height = canvas?.height || 1080,
    effects = [],
    masks = [],
    rendererPreference = "webgl",
    resolution = 1,
  } = options || {};
  requirePixi(PIXI);
  if (!(canvas instanceof HTMLCanvasElement)) {
    throw new TypeError("PixiJS adapter requires an HTMLCanvasElement");
  }
  if (!Array.isArray(effects) || effects.length === 0) {
    throw new Error("PixiJS adapter requires at least one paper effect emitter");
  }

  const app = new PIXI.Application();
  await app.init({
    antialias: true,
    autoDensity: false,
    autoStart: false,
    backgroundAlpha: 0,
    canvas,
    height,
    preference: rendererPreference,
    resolution,
    sharedTicker: false,
    width,
  });
  app.stop();

  const emitters = effects.map((effect) => createEmitter(effect, { width, height }));
  const maskMap = new Map(
    masks.map((mask) => {
      const entry = createPixiMask(PIXI, mask, { width, height });
      app.stage.addChild(entry.graphics);
      return [entry.id, entry];
    }),
  );
  const paperTexture = createPaperTexture(PIXI);
  const layers = emitters.map((emitter, emitterIndex) => {
    const container = new PIXI.ParticleContainer({
      boundsArea: new PIXI.Rectangle(-width * 0.5, -height * 0.5, width * 2, height * 2),
      dynamicProperties: {
        color: true,
        position: true,
        rotation: true,
        vertex: true,
      },
    });
    const particles = emitter.particles.map(() => {
      const particle = new PIXI.Particle({
        alpha: 0,
        anchorX: 0.5,
        anchorY: 0.5,
        scaleX: 0,
        scaleY: 0,
        texture: paperTexture,
      });
      container.addParticle(particle);
      return particle;
    });
    const maskId = effects[emitterIndex]?.mask;
    if (maskId != null) {
      const mask = maskMap.get(String(maskId));
      if (!mask) throw new Error(`PixiJS effect ${emitter.id} references unknown mask ${maskId}`);
      container.mask = mask.graphics;
    }
    app.stage.addChild(container);
    return { container, emitter, particles };
  });

  function renderAt(localTime) {
    let visibleParticles = 0;
    for (const layer of layers) {
      const states = sampleEmitter(layer.emitter, localTime);
      for (let index = 0; index < layer.particles.length; index += 1) {
        applyParticleState(layer.particles[index], states[index]);
        if (states[index].visible && states[index].alpha > 0.001) {
          visibleParticles += 1;
        }
      }
    }
    app.render();
    canvas.dataset.paperHybridTime = Number(localTime).toFixed(6);
    canvas.dataset.paperHybridVisibleParticles = String(visibleParticles);
  }

  function destroy() {
    app.destroy(false, {
      children: true,
      context: true,
      texture: false,
      textureSource: false,
    });
    if (paperTexture !== PIXI.Texture.WHITE) {
      paperTexture.destroy(true);
    }
  }

  renderAt(0);
  return {
    app,
    destroy,
    emitters,
    masks: maskMap,
    engine: "pixijs-webgpu",
    renderAt,
  };
}

async function mountPixiPaperEffects(options) {
  const { registerRenderer, id, root, durationSeconds } = options || {};
  if (typeof registerRenderer !== "function") {
    throw new TypeError("mountPixiPaperEffects requires registerRenderer");
  }
  const renderer = await createPixiPaperEffects(options);
  const unregister = registerRenderer({
    id,
    engine: "pixijs-webgpu",
    root,
    durationSeconds,
    renderAt: renderer.renderAt,
  });
  return {
    ...renderer,
    unregister() {
      unregister();
      renderer.destroy();
    },
  };
}

export {
  applyParticleState,
  createPaperTexture,
  createPixiPaperEffects,
  mountPixiPaperEffects,
};
