/**
 * Seek-safe Rive linear-animation adapter for HyperFrames.
 *
 * This deliberately uses the low-level canvas-advanced API. State machines are
 * not accepted because their result can depend on input history and transition
 * state. Use a finite linear animation here or pre-render the state machine.
 */

import { clamp, finite } from "../deterministic.js";


export function normalizeRiveAnimationTime(localTime, duration, playback = "loop") {
  const time = Math.max(0, finite(localTime, 0));
  const span = Math.max(0, finite(duration, 0));
  if (span === 0) {
    return 0;
  }
  if (playback === "clamp") {
    return clamp(time, 0, span);
  }
  if (playback === "ping-pong") {
    const phase = ((time % (span * 2)) + span * 2) % (span * 2);
    return phase <= span ? phase : span * 2 - phase;
  }
  if (playback !== "loop") {
    throw new Error(`Unsupported Rive playback mode: ${playback}`);
  }
  if (time < span) {
    return time;
  }
  return ((time % span) + span) % span;
}


export async function createSeekableRiveLinearAnimation({
  RiveCanvas,
  canvas,
  src,
  wasmUrl = null,
  animationName,
  animationDuration = null,
  artboardName = null,
  fit = "contain",
  alignment = "center",
  playback = "native",
  fetchImpl = globalThis.fetch,
}) {
  if (typeof RiveCanvas !== "function") {
    throw new TypeError("RiveCanvas must be the @rive-app/canvas-advanced module factory");
  }
  if (!canvas || !Number.isFinite(canvas.width) || !Number.isFinite(canvas.height)) {
    throw new TypeError("canvas must have fixed numeric width and height");
  }
  if (!src || !animationName) {
    throw new TypeError("src and animationName are required");
  }
  if (typeof fetchImpl !== "function") {
    throw new TypeError("fetchImpl must be available");
  }

  const rive = wasmUrl
    ? await RiveCanvas({ locateFile: () => wasmUrl })
    : await RiveCanvas();
  const renderer = rive.makeRenderer(canvas, true);
  if (!renderer) {
    throw new Error("Rive failed to create a canvas renderer");
  }
  const response = await fetchImpl(src);
  if (!response?.ok) {
    throw new Error(`Unable to load Rive asset ${src}: HTTP ${response?.status ?? "unknown"}`);
  }
  const file = await rive.load(new Uint8Array(await response.arrayBuffer()));
  let artboard = artboardName ? file.artboardByName(artboardName) : file.defaultArtboard();
  if (!artboard) {
    file.delete?.();
    renderer.delete?.();
    throw new Error(`Rive artboard was not found: ${artboardName ?? "<default>"}`);
  }
  const definition = artboard.animationByName(animationName);
  if (!definition) {
    artboard.delete?.();
    file.delete?.();
    renderer.delete?.();
    throw new Error(`Rive linear animation was not found: ${animationName}`);
  }
  let animation = new rive.LinearAnimationInstance(definition, artboard);
  const duration = finite(animationDuration, 0);
  if (playback !== "native" && duration <= 0) {
    animation.delete?.();
    artboard.delete?.();
    file.delete?.();
    renderer.delete?.();
    throw new Error(
      `Rive playback ${playback} requires an author-confirmed animationDuration for ${animationName}`,
    );
  }
  const fitValue = rive.Fit?.[fit];
  const alignmentValue = rive.Alignment?.[alignment];
  if (fitValue === undefined || alignmentValue === undefined) {
    throw new Error(`Unsupported Rive fit/alignment: ${fit}/${alignment}`);
  }
  const canvasBounds = {
    minX: 0,
    minY: 0,
    maxX: canvas.width,
    maxY: canvas.height,
  };
  let destroyed = false;

  function resetInstances() {
    animation?.delete?.();
    artboard?.delete?.();
    artboard = artboardName ? file.artboardByName(artboardName) : file.defaultArtboard();
    const nextDefinition = artboard?.animationByName(animationName);
    if (!artboard || !nextDefinition) {
      throw new Error(`Unable to recreate Rive ${artboardName ?? "<default>"}/${animationName}`);
    }
    animation = new rive.LinearAnimationInstance(nextDefinition, artboard);
  }

  function renderAt(localTime) {
    if (destroyed) {
      return;
    }
    const animationTime = playback === "native"
      ? Math.max(0, finite(localTime, 0))
      : normalizeRiveAnimationTime(localTime, duration, playback);
    // Recreate the artboard for every absolute sample. Some Rive constraints
    // retain solved state on the artboard even after animation.time is reset;
    // a fresh instance makes the same timestamp independent of seek history.
    resetInstances();
    renderer.clear();
    // Rive's own high-level scrub implementation resets time to zero and then
    // advances to the requested absolute position before apply().
    animation.time = 0;
    animation.advance(animationTime);
    animation.apply(1);
    artboard.advance(0);
    renderer.save();
    renderer.align(fitValue, alignmentValue, canvasBounds, artboard.bounds);
    artboard.draw(renderer);
    renderer.restore();
    renderer.flush?.();
    rive.resolveAnimationFrame?.();
    canvas.dataset.riveTime = animationTime.toFixed(6);
    canvas.dataset.riveAnimation = animationName;
  }

  function destroy() {
    if (destroyed) {
      return;
    }
    destroyed = true;
    animation?.delete?.();
    artboard?.delete?.();
    file.delete?.();
    renderer.delete?.();
    canvas.dataset.riveReady = "false";
  }

  canvas.dataset.riveReady = "true";
  canvas.dataset.riveDuration = duration > 0 ? duration.toFixed(6) : "native";
  renderAt(0);
  return {
    engine: "rive",
    animationName,
    duration: duration > 0 ? duration : null,
    playback,
    renderAt,
    destroy,
  };
}


export async function mountRiveLinearAnimation({
  registerRenderer,
  id,
  root,
  durationSeconds,
  ...options
}) {
  if (typeof registerRenderer !== "function") {
    throw new TypeError("registerRenderer is required");
  }
  const adapter = await createSeekableRiveLinearAnimation(options);
  const unregister = registerRenderer({
    id,
    engine: "rive",
    root,
    durationSeconds,
    renderAt: adapter.renderAt,
  });
  return {
    ...adapter,
    unregister() {
      unregister();
      adapter.destroy();
    },
  };
}
