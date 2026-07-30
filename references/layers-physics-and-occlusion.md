# Layers, physics, and occlusion

## Layer by responsibility

Use layers because elements differ in depth, ownership, or motion. A useful scene often contains background fill, distance atmosphere, midground architecture, actors, active props/effects, foreground occlusion, paper texture, captions, and watermark. Do not force every scene to use the same count.

Do not split a causal unit merely because a layer list permits it. A complete lamp normally contains its bowl, wick, flame, and local contact shadow; a bed scene may contain the bed, bedding, canopy, and person as one full-scene state. Separate only the channel that truly needs independent motion.

## Containers and water

- Place the water surface behind the front rim mask and inside the container silhouette.
- Anchor a stream to a visible mouth, lip, spout, or rupture point.
- Make the stream intersect its target; do not float a blue ribbon between them.
- Couple every pour to source tilt, changing water surface, target ripple/splash, wet mark, and optional reaction.
- Keep water hue inside the painted palette; avoid saturated digital cyan unless the style demands it.

## Fire and smoke

Show ignition cause before the main fire. Use distinct stages: source instability, spill or contact, small ignition, propagation along a material, uncontrolled fire, response, suppression, steam/smoke, and wet/cool residue.

Avoid replacing a tiny flame with an unrelated large sticker. Preserve a visible path between phases.

## Rope, poles, and load

- Keep attachment points continuous.
- Show compression, sag, lag, or counter-swing to sell weight.
- Let bodies change balance in response to load.
- Move a connected ensemble as one world-space subject; layer internal secondary motion on nested elements.

## Prop ownership

Every traveling prop needs one owner at a time. Define `source → owner → handoff → target → rest/exit`. During handoff, overlap ownership only for the short contact interval. Hide or retire previous instances deterministically; never leave a duplicate bucket moving behind the action.

## Occlusion and shadow

Use foreground masks and contact shadows to place elements in one space. When a prop crosses a rim, hand, body, doorway, or foreground plant, animate the relevant z-order or mask instead of letting the prop float above every layer.

Treat a character head and face as protected review regions. Never let a scene-host boundary, `overflow: hidden`, alpha crop, mask, matte, foreground edge, transition, caption, or watermark cut through the scalp or identity-critical facial features. A straight edge that removes half the face reads as amputation, not depth.

Allow partial head/face coverage only when the occluding object is visible, belongs at the declared depth, crosses the actor along a physically readable path, and appears in the shot’s intentional-occlusion contract. Preserve an unobstructed identity-proof frame before or after the coverage. Natural profile is allowed when the skull, facial contour, visible features, jaw, and neck remain coherent.

At every pose swap, keep canvas padding, anchor, scale, crop, and mask bounds consistent. Check the frame before the swap, the overlap, and the frame after it; mismatched atlas padding often produces a one-frame sliced scalp or half-face.

For a light-to-screen-to-observer scene, write the depth order explicitly and keep it stable: `lamp → complete shadow object → screen → observer`. If the light moves, the shadow scale and edge sharpness must respond in the correct direction. Use the same contact-shadow and floor-line logic for characters crossing the space.
