import { clamp, finite } from "../deterministic.js";


const MASK_KINDS = new Set(["rect", "circle", "polygon", "band"]);


function normalizedPoint(value, fallback = [0.5, 0.5]) {
  if (!Array.isArray(value) || value.length !== 2) return [...fallback];
  return [
    clamp(finite(value[0], fallback[0]), 0, 1),
    clamp(finite(value[1], fallback[1]), 0, 1),
  ];
}


function normalizeMask(input) {
  if (!input || typeof input !== "object") throw new TypeError("paper mask must be an object");
  const id = String(input.id || "").trim();
  if (!id) throw new Error("paper mask requires a stable id");
  const kind = String(input.kind || "");
  if (!MASK_KINDS.has(kind)) throw new Error(`unknown paper mask kind: ${kind}`);
  const normalized = {
    id,
    kind,
    invert: input.invert === true,
  };
  if (kind === "rect" || kind === "band") {
    normalized.origin = normalizedPoint(input.origin, [0, 0]);
    normalized.size = normalizedPoint(input.size, [1, 1]);
  } else if (kind === "circle") {
    normalized.center = normalizedPoint(input.center);
    normalized.radius = clamp(finite(input.radius, 0.25), 0.001, 1);
  } else {
    if (!Array.isArray(input.points) || input.points.length < 3) {
      throw new Error(`paper mask ${id} polygon requires at least three points`);
    }
    normalized.points = input.points.map((point) => normalizedPoint(point));
  }
  return normalized;
}


function createPixiMask(PIXI, input, frame) {
  if (typeof PIXI?.Graphics !== "function") throw new TypeError("PixiJS Graphics is required for masks");
  const mask = normalizeMask(input);
  if (mask.invert) throw new Error("inverted paper masks require a pre-rendered alpha matte");
  const width = Math.max(1, finite(frame?.width, 1920));
  const height = Math.max(1, finite(frame?.height, 1080));
  const graphics = new PIXI.Graphics();
  if (mask.kind === "rect" || mask.kind === "band") {
    graphics
      .rect(
        mask.origin[0] * width,
        mask.origin[1] * height,
        mask.size[0] * width,
        mask.size[1] * height,
      )
      .fill(0xffffff);
  } else if (mask.kind === "circle") {
    graphics
      .circle(mask.center[0] * width, mask.center[1] * height, mask.radius * Math.min(width, height))
      .fill(0xffffff);
  } else {
    graphics
      .poly(mask.points.flatMap(([x, y]) => [x * width, y * height]))
      .fill(0xffffff);
  }
  graphics.name = `paper-mask:${mask.id}`;
  return { id: mask.id, graphics, spec: mask };
}


export {
  MASK_KINDS,
  createPixiMask,
  normalizeMask,
  normalizedPoint,
};
