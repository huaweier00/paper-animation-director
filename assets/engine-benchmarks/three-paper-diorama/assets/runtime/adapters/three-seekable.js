/**
 * Seek-safe Three.js WebGPU/WebGL2 adapter for HyperFrames.
 *
 * The scene owns no free-running clock. Camera, mixers, shader uniforms,
 * particles, and all other animated values must be derived from renderAt(t).
 */

import { finite } from "../deterministic.js";


export async function createSeekableThreeScene({
  THREE,
  canvas,
  width,
  height,
  sceneFactory,
  pixelRatio = 1,
  alpha = true,
  antialias = true,
  forceWebGL = false,
  rendererFactory = null,
}) {
  if (!THREE || typeof THREE.WebGPURenderer !== "function") {
    throw new TypeError("THREE must be the three/webgpu build");
  }
  if (!canvas) {
    throw new TypeError("canvas is required");
  }
  const renderWidth = Math.max(1, Math.round(finite(width, canvas.width)));
  const renderHeight = Math.max(1, Math.round(finite(height, canvas.height)));
  if (typeof sceneFactory !== "function") {
    throw new TypeError("sceneFactory({ THREE, renderer, width, height }) is required");
  }
  const makeRenderer = rendererFactory
    ?? ((options) => new THREE.WebGPURenderer(options));

  async function initializeRenderer(forceFallback) {
    const instance = makeRenderer({
      canvas,
      antialias,
      alpha,
      forceWebGL: forceFallback,
    });
    instance.setPixelRatio(pixelRatio);
    instance.setSize(renderWidth, renderHeight, false);
    await instance.init();
    return instance;
  }

  let renderer;
  try {
    renderer = await initializeRenderer(forceWebGL);
  } catch (error) {
    if (forceWebGL) {
      throw error;
    }
    renderer?.dispose?.();
    renderer = await initializeRenderer(true);
    canvas.dataset.threeFallbackReason = error instanceof Error ? error.message : String(error);
  }
  renderer.setClearColor?.(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const spec = await sceneFactory({
    THREE,
    renderer,
    width: renderWidth,
    height: renderHeight,
  });
  if (!spec?.scene || !spec?.camera || typeof spec.updateAt !== "function") {
    renderer.dispose?.();
    throw new TypeError("sceneFactory must return { scene, camera, updateAt(localTime, globalTime) }");
  }

  spec.updateAt(0, 0);
  await renderer.compileAsync?.(spec.scene, spec.camera);
  renderer.render(spec.scene, spec.camera);
  let destroyed = false;

  function renderAt(localTime, globalTime = localTime) {
    if (destroyed) {
      return;
    }
    const local = Math.max(0, finite(localTime, 0));
    const global = Math.max(0, finite(globalTime, local));
    spec.updateAt(local, global);
    renderer.render(spec.scene, spec.camera);
    canvas.dataset.threeTime = local.toFixed(6);
    canvas.dataset.threeRenderCalls = String(renderer.info?.render?.calls ?? 0);
  }

  function destroy() {
    if (destroyed) {
      return;
    }
    destroyed = true;
    spec.dispose?.();
    renderer.dispose?.();
    canvas.dataset.threeReady = "false";
  }

  const backend = renderer.backend?.isWebGPUBackend === true ? "webgpu" : "webgl2";
  canvas.dataset.threeReady = "true";
  canvas.dataset.threeBackend = backend;
  return {
    engine: "three-webgpu",
    backend,
    renderer,
    scene: spec.scene,
    camera: spec.camera,
    renderAt,
    destroy,
  };
}


export async function mountThreeSeekableScene({
  registerRenderer,
  id,
  root,
  durationSeconds,
  ...options
}) {
  if (typeof registerRenderer !== "function") {
    throw new TypeError("registerRenderer is required");
  }
  const adapter = await createSeekableThreeScene(options);
  const unregister = registerRenderer({
    id,
    engine: "three-webgpu",
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
