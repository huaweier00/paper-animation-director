# Performance grammar

Use this reference for every shot in which a character, animal, group, prop, or environment changes meaningfully. Design the performance before selecting an engine or generating final assets.

## Contents

1. Performance hierarchy
2. Action phrase
3. Controls and support
4. Timing and spacing
5. Acting and reaction
6. Locomotion and interaction
7. Earned stillness
8. Performance contract and review

## 1. Performance hierarchy

Separate four channels:

1. **performance** — gaze, pose, balance, gesture, articulation, locomotion, interaction;
2. **physical response** — recoil, drag, sag, splash, debris, shadow, residue;
3. **presentation** — camera, parallax, focus, captions, transitions, graphic marks;
4. **surface** — grain, fiber, dust, flicker, decorative loops.

Only the first two can prove a plot-bearing physical action. Presentation and surface motion may support attention, mood, time, or transition.

## 2. Action phrase

Build the smallest complete phrase that fulfils the shot:

```text
objective/attention
→ preparation or thought
→ anticipation
→ primary action
→ contact/change or exact hold
→ settle/recovery
→ affected-character reaction
→ new objective or cut
```

Not every phrase needs every phase. Every included phase must create a visible or audible difference. Do not invent busy motion to satisfy a list.

For every shot, name:

- immediate objective;
- initial and final attention;
- lead body part/control/state;
- support or airborne condition;
- strongest silhouette;
- contact/change and affected subject;
- result held long enough to read;
- final thought or state.

## 3. Controls and support

Select a performance mode:

- `articulated-rig` — named local controls/joints drive continuous or stepped action;
- `pose-replacement` — authored complete poses/states replace one another;
- `connected-ensemble` — interacting actors/props share exact state frames;
- `full-scene-state` — integrated scene states protect contact, perspective, or light;
- `selective-local-motion` — a stable painting/tableau changes only approved local regions;
- `deliberate-still` — no actor motion, with earned-stillness evidence.

Root translation, root rotation, root scale, opacity, camera, background, particles, and text are not performance modes.

For articulated performers, declare root, pivots, ranges, draw order, overlaps, attachments, and local controls. For pose/state performers, declare semantic state, shared canvas/baseline, identity continuity, direction, and transition method.

Keep feet, wheels, bodies, and placed props attached to support surfaces. A shadow-screen route may use a screen line rather than a ground plane, but balance and contact remain authored.

## 4. Timing and spacing

Avoid default symmetric easing. Shape timing from thought, force, material, and sound:

- hold long enough for intention/result to register;
- compress time into urgent actions;
- use brief anticipation where it clarifies direction or force;
- stop exactly on important silhouettes, contacts, substitutions, and sound accents;
- offset secondary parts from the primary control;
- use overshoot/settle only when material or emotion warrants it;
- cut after the beat lands unless thought, suspense, ritual, observation, or sound sustains the hold.

Review at 0.25× for pops, seams, sliding, bad anchors, and contact; at 1× for performance; at 2× for beat clarity.

## 5. Acting and reaction

Face attractiveness cannot rescue a neutral body. Design pose and state from line of action, asymmetry, negative space, weight, gaze, and relationship.

Subtle acting may use:

- gaze and head direction;
- breath or torso compression;
- shoulder tension;
- hand openness/closure;
- distance and orientation to another actor;
- delayed response before action.

Broad action preserves one dominant line and one lead control. Do not move every part equally.

Every important action identifies an affected subject and reaction unless the absence of reaction is the story point. A threat without recoil, attention change, resistance, or environmental consequence remains an isolated gesture.

## 6. Locomotion and interaction

Choose route-, species-, mechanism-, speed-, camera-, and story-appropriate locomotion. Preserve authored facing, travel vector, support phases, body rise/fall or chosen stylization, and entry/exit continuity.

Reject world translation that outruns support and produces skating. Derive speed from stride/cadence, use graphic stepped poses, or use a connected travelling state; document the choice.

For grab, lift, carry, sit, open, handoff, embrace, restraint, weapon, mount, or collision, review:

1. approach/preparation;
2. exact contact;
3. balance, compression, or transferred load;
4. propagation through actor, prop, environment, effect, and sound;
5. stable result/recovery;
6. reaction.

Use a connected ensemble or integrated state when independent layers cannot preserve the relationship.

## 7. Earned stillness

A deliberate still must declare:

- what cause or previous action created it;
- what present condition, result, relationship, ritual, or thought the audience reads;
- what visual composition, gaze, light, sound, or silence sustains tension;
- why local actor motion would weaken the beat;
- what ends the hold: a new thought, sound, cut, reveal, or action.

Reject stillness when it merely saves asset work, spans incompatible intentions, or leaves narrated actions unseen. A still cannot be approved solely by writing “intentional.”

## 8. Performance contract and review

Create `performance-contract.json` per shot before final assets. At planning, verify the selected mode and phrase can prove the shot. At release, verify the rendered MP4 rather than the timeline declaration.

Inspect these proof moments when applicable:

- initial attention/support;
- preparation/anticipation;
- early and peak action;
- exact contact/change/hold;
- settle/recovery;
- affected-subject reaction;
- final state/exit.

Reject when action evidence is only a whole-layer transform, camera move, opacity, particles, text, or sound with no intentional off-screen treatment. Reject repeated asset hashes across incompatible objectives or performance states.
