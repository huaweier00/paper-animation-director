export function getMotionTrack(compiled, actorId) {
  if (!compiled || compiled.schema_version !== 1 || !Array.isArray(compiled.tracks)) {
    throw new Error("compiled motion track must use schema_version 1");
  }
  const track = compiled.tracks.find((item) => item.actor_id === actorId);
  if (!track) throw new Error(`motion track not found for ${actorId}`);
  return track;
}

export function applyGsapMotion({ gsap, timeline, compiled, actorId, ease = "none" }) {
  if (!gsap || !timeline) throw new Error("gsap and timeline are required");
  const track = getMotionTrack(compiled, actorId);
  const [start, end] = track.active;
  const element = document.querySelector(track.selector);
  if (!element) throw new Error(`motion selector not found: ${track.selector}`);
  element.dataset.motionActor = actorId;
  element.dataset.motionFacing = track.rendered_facing;
  element.dataset.motionTravel = track.travel_direction;
  gsap.set(element, {
    x: track.start_px[0],
    y: track.start_px[1],
    scaleX: track.scale_x,
  });
  timeline.to(
    element,
    {
      x: track.end_px[0],
      y: track.end_px[1],
      duration: end - start,
      ease,
    },
    start,
  );
  return track;
}

export function seekTimelineToPending({ timeline, root, duration }) {
  if (!timeline) throw new Error("timeline is required");
  const element = typeof root === "string" ? document.querySelector(root) : root;
  const host = element?.closest?.("[data-composition-src][data-start]");
  const compositionStart = Number(host?.getAttribute("data-start") || 0);
  const globalTime = Number(window.__paperHybridPendingTime || 0);
  const maximum = Number.isFinite(Number(duration)) ? Number(duration) : timeline.duration();
  const localTime = Math.max(0, Math.min(maximum, globalTime - compositionStart));
  timeline.time(localTime, false);
  return localTime;
}
