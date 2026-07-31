/**
 * Capture HyperFrames seek time before asynchronous engine modules finish.
 *
 * Rive WASM, Three.js assets, and other engines can finish loading after the
 * first hf-seek event. The runtime consumes this retained value when each
 * renderer registers, preventing the first captured frame from falling back to
 * time zero.
 */

if (!window.__paperHybridSeekCaptureInstalled) {
  window.__paperHybridSeekCaptureInstalled = true;
  window.__paperHybridPendingTime = 0;
  window.addEventListener("hf-seek", (event) => {
    const value = Number(event?.detail?.time);
    if (Number.isFinite(value)) {
      window.__paperHybridPendingTime = Math.max(0, value);
    }
  });
}
