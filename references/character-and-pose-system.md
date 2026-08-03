# Character, model-pack, and pose system

## Three distinct asset layers

Do not ask one image to solve identity, performance, and final compositing at once.

1. **Canonical identity anchor** — approve one neutral, frontal, full-body reference for each recurring character. It fixes face, proportions, costume silhouette, palette, footwear, and signature traits.
2. **Reference-only model pack** — after the animatic, staging, and style route are locked, derive controlled left profile, right profile, useful three-quarter views, scale reference, asymmetry notes, expression range, and attachment rules. These images guide generation and review; they never enter a final shot.
3. **Shot production assets** — generate only the connected poses, layers, or state frames required by an approved shot contract. These are the only character images allowed into the render.

The frontal anchor remains the identity source of truth. The model pack is not a generic pose library and must not invent story action. Its job is to remove ambiguity about direction, handedness, costume asymmetry, scale, facial construction, and attachment points before expensive shot work begins.

Mark both identity layers `reference_only: true` or with the canonical identity purpose, and `animation_use: false`. Do not animate or deliver them. Record every final production asset separately in `asset-facts.json`, including its file hash and observed orientation.

## When to build the model pack

Do not create a large turnaround before the story has a timed animatic; early speculative sheets waste time and freeze the wrong camera assumptions. Build the minimum reusable pack only when all of these are true:

- the character recurs across shots;
- the visual route and proportions are approved;
- the sequence layout establishes which sides and camera angles are needed;
- identity inconsistency or facing ambiguity would otherwise repeat.

One-off background figures can use a smaller identity note. A protagonist crossing, turning, carrying, or interacting across multiple shots needs both profiles and the relevant three-quarter views.

## Pose design follows performance

Design poses from the shot's intention and action phases, not from a universal walk-cycle inventory. The minimum useful set usually covers:

`intention/read → anticipation → primary action → contact or passing pose → settle → reaction`

A locomotion shot may need contacts, passing positions, compression, extension, or held poses, but there is no mandatory six-frame count. Frame count and drawing changes follow screen size, speed, emotion, species, camera, and edit duration. A frightened rabbit, an exhausted person, and a ceremonial procession must not share one normalized gait recipe.

For every moving asset, approve the silhouette at its intended display size and record:

- intrinsic facing and forward axis;
- head, chest, pelvis/torso, feet, and gaze evidence;
- support or contact points;
- asymmetrical costume, hair, props, text, light, and handedness;
- whether mirroring is forbidden, conditionally safe, or approved for this shot.

Reject a pose when its rendered travel vector conflicts with its head/chest/feet/gaze evidence. Fix the source or select the correct view; do not hide the error in filenames, prompts, or negative `scaleX` values.

## Rig-ready cutout rules

Use cutout rigs only when the action benefits from controlled articulation. Establish a stable root, foot or support baseline, named pivots, rest pose, draw order, and attachment points before animation. Keep transparent safety margin around all moving parts and include hidden overlap under joints so motion does not open gaps.

Use complete connected poses when a rig would expose anatomy seams or create a mechanical puppet feel. Prefer full-scene state frames when the contact problem is harder than the motion problem—for example body + bed + bedding, hand + rope + shared load, or animal + tree-stump impact.

## Contact and ensembles

Generate actors as one connected ensemble when they share a load, embrace, support a body, pull one rope, or require exact hand-to-object contact. Keep the shared object and its attachment points in the same state frame when separate layers would create gaps, sliding grips, or false depth.

Every ensemble state must contain the exact actor count, one continuous shared object, valid support/contact points, and no extra limbs or duplicate props. Contact frames are proof frames and must be included in the motion review.

## Atlas production

Use a 2×2 or 3×2 atlas only when it improves consistency and each cell can remain semantically complete. Record the shot ID, identity anchor, model-pack views used, camera side, screen direction, intrinsic facing, light direction, and required action. Keep one complete state per cell; disconnected held items stay in that cell.

After keying and splitting, audit alpha, crop safety, empty cells, edge contamination, baseline consistency, and accidental baked effects. Then register each extracted file in `asset-facts.json`. Do not patch a missing head or hand with an unrelated generation unless identity, anatomy, lighting, and attachment can all be proven; regeneration is normally cheaper than downstream repair.
