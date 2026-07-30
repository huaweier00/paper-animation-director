# Animation direction framework

Use this reference before generating shot assets and again when reviewing the rendered MP4. Its purpose is to keep the production from drifting into generic moving illustrations while preserving the director’s freedom to choose stillness, continuous tableaux, selective motion, layered paper actors, connected ensembles, or full-scene state changes.

This is a judgment framework, not a duration, layer, pose, state, or cut-count specification.

## 1. Begin with the shot’s responsibility

Write one plain-language sentence:

> This shot is responsible for making the audience perceive ______.

The answer may be an action, relationship, reaction, space, reveal, atmosphere, duration, pause, consequence, memory, or transition. Do not automatically turn every narrated verb into a literal animated action. Decide what this particular shot must carry and what may be carried by an adjacent shot, sound, narration, or deliberate omission.

Useful questions:

- What new understanding or feeling must exist when the shot ends?
- Does the audience need to witness an unfolding change, or only understand a condition, result, reaction, or place?
- Which spatial or physical relationship is essential?
- Would stillness strengthen the moment?
- Would cutting destroy continuity or performance?
- Is the action intentionally elliptical or off-screen? If so, where is its cause or consequence made legible?

## 2. Describe required visible change without prescribing quantity

If the shot is responsible for showing a plot-bearing action, name the visible evidence that would make that action readable. Evidence may be:

- one decisive local gesture;
- a connected ensemble changing balance, support, or contact;
- a prop changing owner, position, state, or effect;
- a subject moving through the scene;
- a full-scene before/after or continuous state change;
- an occlusion, shadow, residue, reaction, or environmental response;
- another visual change appropriate to the chosen style.

There is no universal minimum number of layers, states, poses, or simultaneous responsibilities. One exact change can be stronger than many decorative motions. Conversely, a complex event may need several linked changes. The director must explain why the chosen evidence is sufficient for this shot.

If the shot is not responsible for showing an unfolding action, visible change may be minimal or absent. A long or short still tableau can be valid for contemplation, dread, revelation, ritual, grief, icon-like illustration, spatial establishment, or a deliberate pause. Duration must be judged from pacing, performance, voice, sound, and surrounding shots—not from a universal limit.

## 3. Choose an architecture from the shot, not from a template

The following are options, not mandatory modes or a ranking:

- **Independent paper layers** — useful when a character, prop, foreground element, or effect needs its own change.
- **Connected ensemble** — useful when separating characters and a shared load would damage contact, anatomy, or balance.
- **Full-scene state change** — useful when perspective, light, crowd structure, bedding, architecture, or physical contact is fragile.
- **Single tableau with selective local motion** — useful when the composition should remain integrated but one or more local cues need to breathe or change.
- **Deliberate still tableau** — useful when stillness itself serves the dramatic responsibility.
- **Hybrid construction** — useful when the shot benefits from a stable integrated base plus a few independent subjects, masks, effects, or replacements.

Do not choose an architecture merely because a generator or template already exists. Do not split connected subjects merely to increase layer count. Do not keep everything merged merely to save production time when the shot needs a readable local change.

For the chosen architecture, record:

- what remains merged and why;
- what changes independently and why;
- which contact, perspective, identity, or occlusion risks shape the decision;
- which simpler and more complex alternatives were considered;
- why the selected option best serves the shot.

## 4. Camera and presentation motion are legitimate tools

Pushes, pans, zooms, reframing, parallax, focus changes, grain, text, light shifts, and graphic marks are not inherently inferior. They may carry attention, reveal, subjectivity, atmosphere, duration, transition, or a designed illustrated rhythm.

The failure occurs only when the production claims that these devices prove a plot-bearing physical action that never becomes visible.

Examples:

- A slow push into a father’s still face after his son is spared may fully serve a reaction shot.
- A long still view of an empty stable with sound carrying the escape may be a strong elliptical choice if the surrounding film makes cause and result clear.
- A camera pan across a finished battle aftermath may establish consequence without animating the battle.
- A zoom over a rider frozen mid-fall does not, by itself, show the fall if this shot is responsible for depicting the fall.

The same technique can therefore pass or fail depending on the declared responsibility and surrounding edit.

## 5. Decide whether to split or sustain

Do not split shots by counting verbs, locations, seconds, or states. Consider a split when:

- one composition cannot keep the important change readable;
- different moments require incompatible camera axes, scale, or staging;
- a contact event and its consequence compete for attention;
- the proposed shot becomes a generic tableau that merely summarizes several events;
- the rhythm benefits from distinct beats.

Consider a continuous shot when:

- uninterrupted space or time is dramatically important;
- contact, performance, suspense, ritual, or stillness gains power from duration;
- a full-scene transition can carry the event clearly;
- cutting would make the action more mechanical or less credible.

Record the reason either way. “One manifest scene equals one production shot” and “every verb needs a new shot” are both invalid defaults.

## 6. Compare to a benchmark intelligently

A benchmark proves a quality bar and a production method under a particular narrative demand. It is not a complexity quota.

Compare shots only where their demands are genuinely similar:

- action clarity;
- contact fragility;
- identity continuity;
- physical support and scale;
- depth and occlusion;
- emotional subtlety;
- style and finish.

A quiet reaction may need less motion than an escape. A ritual tableau may intentionally be flatter than a chase. Flag a downgrade only when a later shot with comparable demands loses clarity or craft without a directing reason.

## 7. Required `animation-decision.json`

Create one sidecar per production shot. Use free text where artistic judgment matters.

```json
{
  "shot_id": "scene-05b-gate",
  "shot_function": "contrast departure with the injured son's stillness",
  "narrative_responsibility": "the audience must understand that other young men leave for war while the injured son remains with his father",
  "responsibility_requires_visible_action": true,
  "required_visible_changes": [
    "the departing group crosses the gate or otherwise changes from present to gone",
    "the father and son remain spatially inside"
  ],
  "evidence_is_presentation_only": false,
  "intentional_ellipsis_or_offscreen_action": false,
  "ellipsis_rationale": "",
  "action_carried_elsewhere": [],
  "architecture_choice": "hybrid full-scene base with a connected father-son ensemble and a departing group layer",
  "merged_elements": [
    "father and son remain connected because balance and support are fragile"
  ],
  "independent_elements": [
    "departing group changes position relative to the gate"
  ],
  "camera_and_presentation_role": "a restrained push strengthens separation but is not the evidence of departure",
  "why_this_choice": "the gate supplies a clear threshold while the connected ensemble protects the son's injured balance",
  "alternatives_considered": [
    "a fully merged tableau was rejected because it could not show the group leaving",
    "separate father and son rigs were rejected because hand and shoulder contact became fragile"
  ],
  "risk_flags": [
    "gatepost occlusion",
    "ground contact for departing feet"
  ],
  "proof_plan": [
    "review a frame before threshold crossing",
    "review a frame during crossing",
    "review the end state with father and son still inside"
  ],
  "rendered_review": {
    "mp4": "renders/scene-05b-review.mp4",
    "observed_visible_changes": [
      "departing group crosses behind the gatepost and exits",
      "father-son ensemble remains inside with stable support"
    ],
    "observed_evidence_is_presentation_only": false,
    "responsibility_fulfilled": true,
    "review_notes": "Departure reads muted; the camera push adds emphasis but is not needed to understand the event."
  }
}
```

A deliberate tableau may instead state:

```json
{
  "shot_id": "scene-05c-empty-stable",
  "shot_function": "let the absence of the horse register",
  "narrative_responsibility": "the audience should feel and understand the empty stable after the escape",
  "responsibility_requires_visible_action": false,
  "required_visible_changes": [],
  "evidence_is_presentation_only": true,
  "intentional_ellipsis_or_offscreen_action": true,
  "ellipsis_rationale": "the escape was established by sound and the previous rope-release shot; this shot is the consequence and pause",
  "action_carried_elsewhere": [
    "previous shot: rope releases",
    "sound: receding hoofbeats"
  ],
  "architecture_choice": "single integrated tableau with optional restrained camera drift",
  "merged_elements": [
    "stable, rope, trough, and light remain one perspective-locked scene"
  ],
  "independent_elements": [],
  "camera_and_presentation_role": "slow drift lets the empty space register",
  "why_this_choice": "additional local motion would weaken the emptiness",
  "alternatives_considered": [
    "moving hay and dust were rejected as decorative distraction"
  ],
  "risk_flags": [],
  "proof_plan": [
    "review whether the empty stall is immediately legible without captions"
  ],
  "rendered_review": {
    "mp4": "renders/scene-05c-review.mp4",
    "observed_visible_changes": [],
    "observed_evidence_is_presentation_only": true,
    "responsibility_fulfilled": true,
    "review_notes": "The extended stillness is intentional and supported by hoofbeat sound and the preceding action."
  }
}
```

The sidecar does not need to mimic these examples. It must make the directing logic inspectable.

## 8. Planning review

Run:

```bash
python3 scripts/review_animation_decision.py shots/scene-xx/animation-decision.json --phase planning
```

The review should fail only for missing or contradictory logic, such as:

- a shot says it must show an unfolding action but names no visible evidence;
- a plan lists only camera, text, or decorative changes as proof of that physical action and provides no intentional elliptical treatment;
- an intentional off-screen or still treatment gives no rationale and identifies no adjacent image or sound that carries the missing information;
- an architecture choice has no shot-specific reason;
- the proof plan cannot test the declared responsibility.

It may warn about risks without rejecting an artistic choice. Warnings should prompt review, not become hidden quotas.

## 9. Rendered responsibility review

Run after rendering:

```bash
python3 scripts/review_animation_decision.py shots/scene-xx/animation-decision.json --phase release
```

Review the MP4, not merely source assets or a Studio screenshot:

1. Restate the declared responsibility.
2. Identify what actually changed—or confirm the intended stillness.
3. Decide whether the audience can perceive the intended action, condition, reaction, place, or pause.
4. Check whether camera and presentation motion support the shot or disguise missing evidence.
5. Check physical support, contact, identity, direction, scale, and occlusion wherever relevant.
6. Record whether the shot fulfilled its responsibility and explain why.

Do not reject a shot for being quiet, still, long, single-plate, minimally layered, or structurally different from the benchmark. Reject it when the rendered result does not fulfil its own declared narrative responsibility or when its explanation contradicts the visible evidence.

## 10. Failure pattern learned from over-correction

“Moving poster” is a real failure mode, but replacing it with numerical rules is another failure mode:

- a duration limit can destroy a necessary pause;
- a layer quota encourages pointless separation and anatomy seams;
- a state quota encourages busy, mechanical acting;
- a category quota adds decorative reactions that compete with the story;
- a mandatory split can break spatial continuity and emotional duration;
- benchmark-complexity parity can make every shot equally loud.

Use hard validation for objective contradictions and technical integrity. Use documented judgment and rendered review for directing choices.
