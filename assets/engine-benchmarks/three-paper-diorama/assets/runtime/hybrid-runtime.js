import {
  clamp,
  finite,
  hashString,
  seededUnit,
} from "./deterministic.js";

const registry = new Map();
let currentGlobalTime = Math.max(0, finite(window.__paperHybridPendingTime, 0));

function resolveCompositionStart(root) {
  const element =
    typeof root === "string" ? document.querySelector(root) : root instanceof Element ? root : null;
  const host = element?.closest?.("[data-composition-src][data-start]");
  return finite(host?.getAttribute("data-start"), 0);
}

function localTimeFor(entry, globalTime) {
  const start =
    entry.startSeconds == null
      ? resolveCompositionStart(entry.root)
      : finite(entry.startSeconds, 0);
  const raw = globalTime - start;
  if (entry.durationSeconds == null) return Math.max(0, raw);
  return clamp(raw, 0, finite(entry.durationSeconds, 0));
}

function seek(globalTime) {
  currentGlobalTime = Math.max(0, finite(globalTime, 0));
  window.__paperHybridPendingTime = currentGlobalTime;
  for (const [id, entry] of registry) {
    const root =
      typeof entry.root === "string"
        ? document.querySelector(entry.root)
        : entry.root;
    if (root instanceof Element && !root.isConnected) {
      registry.delete(id);
      continue;
    }
    entry.renderAt(localTimeFor(entry, currentGlobalTime), currentGlobalTime);
  }
}


function rendererInventory() {
  return Array.from(registry, ([id, entry]) => ({
    id,
    engine: entry.engine,
    root: typeof entry.root === "string" ? entry.root : null,
  }));
}


function profileRenderers(globalTime) {
  const time = Math.max(0, finite(globalTime, 0));
  const now = () => globalThis.performance?.now?.() ?? 0;
  const samples = [];
  for (const [id, entry] of registry) {
    const started = now();
    entry.renderAt(localTimeFor(entry, time), time);
    const elapsed = Math.max(0, now() - started);
    samples.push({
      id,
      engine: entry.engine,
      milliseconds: elapsed,
    });
  }
  return {
    globalTime: time,
    totalMilliseconds: samples.reduce((sum, item) => sum + item.milliseconds, 0),
    samples,
  };
}

function registerRenderer(options) {
  if (!options || typeof options !== "object") {
    throw new TypeError("registerRenderer requires an options object");
  }
  const id = String(options.id || "").trim();
  if (!id) throw new Error("registerRenderer requires a stable id");
  if (typeof options.renderAt !== "function") {
    throw new TypeError(`renderer ${id} requires renderAt(localTime, globalTime)`);
  }
  registry.set(id, {
    engine: String(options.engine || "custom"),
    root: options.root || null,
    startSeconds: options.startSeconds,
    durationSeconds: options.durationSeconds,
    renderAt: options.renderAt,
  });
  const entry = registry.get(id);
  entry.renderAt(localTimeFor(entry, currentGlobalTime), currentGlobalTime);
  return () => registry.delete(id);
}

window.addEventListener("hf-seek", (event) => {
  seek(event?.detail?.time);
});

const api = Object.freeze({
  clamp,
  hashString,
  inventory: rendererInventory,
  profileRenderers,
  registerRenderer,
  seededUnit,
  seek,
});

window.__paperHybrid = api;

export {
  clamp,
  hashString,
  profileRenderers,
  registerRenderer,
  rendererInventory,
  seededUnit,
  seek,
};
