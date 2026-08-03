import assert from "node:assert/strict";
import test from "node:test";

import {
  applyGsapMotion,
  seekTimelineToPending,
} from "../assets/project-template/runtime/motion-contract.js";


test("compiled motion owns world-space placement and late async load re-seeks deterministically", () => {
  const element = {
    dataset: {},
    closest() {
      return { getAttribute: (name) => name === "data-start" ? "2" : null };
    },
  };
  globalThis.document = {
    querySelector(selector) {
      assert.equal(selector, "#rabbit");
      return element;
    },
  };
  globalThis.window = { __paperHybridPendingTime: 3.5 };
  const calls = [];
  const gsap = {
    set(target, values) {
      calls.push(["set", target, values]);
    },
  };
  const timeline = {
    to(target, values, at) {
      calls.push(["to", target, values, at]);
    },
    time(value, suppressEvents) {
      calls.push(["time", value, suppressEvents]);
    },
    duration() {
      return 4;
    },
  };
  const compiled = {
    schema_version: 1,
    duration: 4,
    tracks: [
      {
        actor_id: "rabbit",
        selector: "#rabbit",
        active: [0.25, 2.75],
        start_px: [100, 700],
        end_px: [800, 700],
        scale_x: 1,
        rendered_facing: "right",
        travel_direction: "right",
      },
    ],
  };

  applyGsapMotion({ gsap, timeline, compiled, actorId: "rabbit" });
  const local = seekTimelineToPending({ timeline, root: element, duration: compiled.duration });

  assert.equal(element.dataset.motionFacing, "right");
  assert.equal(element.dataset.motionTravel, "right");
  assert.deepEqual(calls[0][2], { x: 100, y: 700, scaleX: 1 });
  assert.equal(calls[1][2].duration, 2.5);
  assert.equal(calls[1][3], 0.25);
  assert.equal(local, 1.5);
  assert.deepEqual(calls.at(-1), ["time", 1.5, false]);
});
