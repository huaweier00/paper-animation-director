# Performance and motion direction

Use this reference whenever a character, animal, prop, camera, cloth, effect, or group visibly changes. Read it before engine selection: animation quality begins with performance design, not software choice.

## Contents

1. Motion hierarchy
2. Acting and key poses
3. Timing and spacing
4. Locomotion
5. Contact, impact, and recovery
6. Secondary motion
7. Camera motion
8. Motion review
9. Engine tiers

## 1. Motion hierarchy

Build motion in this order:

```text
intention → anticipation → primary action → contact/change → settle → reaction
```

Not every shot needs every phase, but every visible phase must serve meaning. A paper aesthetic may use held drawings and stepped changes; it does not excuse missing intention, weight, direction, or consequence.

Separate four kinds of movement:

- **performance motion:** pose, gaze, balance, gesture, locomotion, interaction;
- **physical response:** recoil, drag, sag, splash, smoke, debris, shadow, residue;
- **presentation motion:** camera, parallax, focus, captions, graphic marks;
- **surface motion:** grain, dust, fiber, flicker.

Never let presentation or surface motion stand in for a required performance or physical response.

## 2. Acting and key poses

For every acting shot, state:

- the character's immediate objective;
- what changes that objective or understanding;
- where attention and gaze begin and end;
- which body part leads;
- where weight is supported;
- the strongest readable silhouette;
- the final thought or physical state.

Design poses from line of action, weight, asymmetry, negative space, and eye direction. Do not approve a pose because the face is attractive while the body is neutral or contradictory.

Use a pose hierarchy:

1. **story pose:** instantly communicates the action or relationship;
2. **extreme/contact pose:** carries the largest physical or emotional change;
3. **breakdown:** explains path, balance, and continuity;
4. **settle/reaction pose:** proves consequence and prevents mechanical stopping.

For subtle acting, use gaze, breath, hands, shoulders, torso angle, and weight shift before adding large gestures. For broad action, preserve one dominant line and avoid equal motion in every part.

Check poses in silhouette and at delivery size. If the action cannot be named from the silhouette when it should be physical, redesign the pose.

## 3. Timing and spacing

Timing assigns duration; spacing determines perceived force and material. Plan both explicitly.

- Hold long enough for a pose or result to register.
- Accelerate into urgent travel or impact; avoid default symmetrical easing.
- Use a brief anticipation when it improves force, intention, or readability.
- Use overshoot and settle when material, effort, or emotion warrants it.
- Keep exact contact on a readable frame; do not hide weak contact in blur or a cut.
- Offset secondary parts instead of moving the whole body as one rigid rectangle.
- Shape pauses around thought and performance, not empty narration padding.

Review at 0.25× to expose pops, sliding, wrong anchors, and bad contact. Review at 2× to test whether the main beats remain legible without sluggish holds.

## 4. Locomotion

Do not impose one universal frame count. Choose a cycle or stepped pose family from species, speed, camera, style, and shot responsibility.

For biped walking, cover the needed phases from contact, down, passing, and up on both sides when physical walking must read. For running, distinguish flight, contact, compression, passing, and extension as needed. For quadrupeds, birds, carts, and crowds, use species- or mechanism-appropriate phases rather than mapping a human six-frame walk onto everything.

Every locomotion solution must preserve:

- authored body forward direction;
- rendered facing after instance transforms;
- travel vector;
- support/contact phases;
- foot/hoof/paw baseline or declared airborne arc;
- body rise/fall and compression;
- coherent head, chest, pelvis, feet, and gaze;
- entry, exit, and adjacent-shot continuity.

Avoid world translation that outruns the contact pattern and produces skating. Derive world speed from stride length and cadence, or choose deliberate stylized stepping and document it.

Use replacement poses when the aesthetic benefits from graphic steps. Use a rig when recurring articulated motion, continuous arcs, or repeated retiming justifies it. Do not build a rig for one rigid hop; do not use one rigid image for a hero walk that must feel physical.

## 5. Contact, impact, and recovery

For impact, carrying, lifting, grabbing, opening, sitting, handing off, or collision, review:

1. approach and anticipation;
2. exact contact point;
3. compression, balance change, or transferred load;
4. propagation through body, prop, environment, effect, and sound;
5. stable result or recovery;
6. reaction from affected characters.

Use a connected ensemble or integrated scene when independent layers cannot preserve the relationship. The engine choice is secondary to believable contact.

For collision, do not jump directly from travel to a fallen pose. Include enough compression, recoil, deformation, local effect, or sound-synchronized hold to make the causal event legible in the chosen style.

## 6. Secondary motion

Secondary motion supports the primary action and follows its force:

- sleeves, hair, ears, tail, cloth, rope, foliage, dust, and shadow lag or settle;
- props remain attached to the owning hand, body, support, or container;
- effects originate at declared causes;
- secondary motion does not reverse the perceived action direction;
- random motion remains seeded and subordinate.

Prefer one or two meaningful secondary responses over uniform motion everywhere.

## 7. Camera motion

Give every camera move a job: reveal, follow, reframe, emphasize, separate, compress time, express subjectivity, or bridge a transition.

Avoid default continuous push-ins and drifting multiplane layers. They quickly make every shot feel like the same moving poster.

Before moving the camera, prove that staging and performance read with a static camera. Then add the smallest move that improves the shot. Keep camera acceleration, stop, and settle intentional. Preserve screen direction and avoid crossing the axis without a visible re-establishment.

## 8. Motion review

Review motion in this order:

1. rough shapes or low-cost poses with no final texture;
2. silhouette playback;
3. trajectory and facing-arrow overlay;
4. foot/support/contact overlay;
5. muted 0.25×, 1×, and 2× playback;
6. final-art integration without effects;
7. effects and camera;
8. picture, sound, and captions;
9. adjacent-shot sequence playback.

Sample every motion interval at entry, early travel, midpoint, late travel, contact, settle, and exit—not only the shot's first, middle, and last frames.

Record direction, support, contact, identity, timing, and responsibility as separate findings. A passing semantic review does not waive weak locomotion or broken identity.

## 9. Engine tiers

Choose the lowest tier that can express the approved performance:

- **T0 — integrated still/tableau:** deliberate stillness or result image;
- **T1 — rigid deterministic layers:** simple prop change, reveal, camera, or stylized travel;
- **T2 — stepped complete poses:** graphic acting, pose-to-pose action, limited locomotion;
- **T3 — 2D rig or mesh:** recurring articulation, continuous arcs, reusable performance, controlled retiming;
- **T4 — pre-rendered simulation or 3D:** fragile perspective, physics, cloth, complex depth, destruction, or camera movement that cannot be proved more simply.

Do not promote a shot to a higher tier for prestige. Do not keep a hero action in a lower tier when the required weight, contact, or acting cannot read.
