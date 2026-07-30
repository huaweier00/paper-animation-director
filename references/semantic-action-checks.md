# Semantic action checks

## General proof

Mute audio and ask: who acts, on what object, why, and what changed? If the answer depends on narration, revise staging before adding polish.

Check each event for cause visibility, actor anticipation, contact, travel or propagation, result, reaction, and final state.

Before checking motion, compare the rendered shot with its spatial contract. Verify actor start/end zones, named corridor, obstacles, camera side, direction, facing, gaze, action target, contact point, and proof area. Treat any mismatch as a staging failure even when the image is attractive.

Run a noun pass as well as a verb pass. List every narrated or plot-bearing object and verify that the rendered frame contains the correct recognizable class, not an abstract stand-in. Check real-world silhouette, proportion, material, support/attachment, and state.

## Travel and usable space

Require a continuous clear corridor from start to end with enough width for the body, costume, held prop, or shared load. Keep non-passable furniture, architecture, and other actors outside it. Confirm that the destination leaves room for the next contact and reaction.

For normal forward travel, require left-to-right motion to face right and right-to-left motion to face left. Check head, shoulders, chest, feet, and gaze, not only the image bounding box. Reject and regenerate a wrong-facing pose; do not force it into the shot because it already exists.

Require every standing subject, animal, wheel, vehicle, rooted plant, hanging object, and placed prop to name a support surface or attachment target. Inspect feet, hooves, wheels, roots, knots, bowstrings, handles, boxes, and contact shadows at first, midpoint, proof, and final frames.

## Semantic target

Require every important verb to reference a named target that supports the action. Confirm target type, reach, contact, visibility, and resulting state.

For writing, show the hand or tool reaching the declared writable surface and a visible mark remaining there. If narration says “wall,” do not redirect the action to a window merely because the generated composition placed the character nearby. Apply the same rule to sitting, opening, picking up, pouring, lighting, and handing off.

For weapons, compare construction and length against the wielder. An arrow must attach plausibly to bow, string, hand, and target direction; a long graphic line is not a weapon.

For plants, verify the visual logic relevant to the action: rooted base, stem/leaf form, hand contact, break point, and response to wind or water.

For treasure or currency, verify recognizable form, thickness, material response, container/support, scale, and ownership. Do not accept a mound or geometric icon.

For official notices and text-bearing props, verify the document form and deterministically typeset important wording. Placeholder lines or an emblem alone do not prove a proclamation.

## Command and group response

Require a visible initial state, issuing actor, gesture or spoken line, ordered propagation through the group, and a stable final state. For “lower the bows,” show aimed weapons first, the king’s command/hand, front-to-back lowering, and arrowheads remaining safely toward the ground.

Synchronize the spoken command, issuing gesture, group response, and caption. A silent visual change or a line arriving in the next scene fails the event chain.

## Shared carrying

Require one shared object, exact actor count, visible shoulder/hand contact, load deformation or sag, synchronized travel, distinct foot phases, and a stable final destination. Prefer one connected ensemble asset.

## Handoff or bucket line

Require a source, ordered owners, short hand-contact intervals, no teleport, no duplicate trailing props, a visible target, and a retired or returned empty prop. Each completed handoff must change the next actor's pose or balance.

## Taking turns

Show different actors performing the responsibility in separate time windows. Waiting, receiving, or covering for another actor may support the idea, but simultaneous rope pulling alone does not prove rotation.

## Pouring and extinguishing

For every pour, verify source tilt, mouth-anchored stream, target intersection, splash, steam or reaction, wet residue, and proportional fire reduction. Preserve fire after early pours when later pours are still narratively required.

## Ignition

Show the disturbance, object instability, fall/contact, fuel or heat path, first ignition, propagation, uncontrolled state, and actor discovery. Do not let a fire begin solely because the narration says it did.

## Breakage and impact

Show anticipation, contact, local deformation or crack start, propagation, released contents, debris or residue, and actor reaction. Keep fragments related to the original object silhouette.

## Character continuity

Check scalp, face, hands, sleeves, legs, shoes, costume, scale, light direction, and baked artifacts at every pose change. Reject a technically moving shot if identity or anatomy breaks.

Inspect the rendered MP4 at first frame, midpoint, every pose change, each occlusion entry/maximum/exit, proof time, transition boundary, and final frame. Reject any straight, rectangular, or mask-shaped cut through the scalp, face, eye line, nose, mouth, jaw, or neck. Do not accept “the foreground covers it” unless the foreground object is visible, physically placed, temporally declared, and narratively justified.

Distinguish profile from damage: a valid side/profile view keeps a coherent skull, visible facial contour, feature placement, jaw, and neck connection. A half-face caused by crop, overflow, mismatched pose canvas, or undeclared z-order is a continuity failure.

For approach or confrontation, also check camera side and orientation: head, shoulder, chest, feet, and gaze should agree with the path. Prefer a side or three-quarter side view when both actors and the contact line must be readable. A character turning back while apparently advancing toward the other actor is a semantic failure, not a minor pose issue.

For a normalized gait, check support foot, contact foot, body rise/fall, coat or sleeve lag, fixed foot baseline, and the absence of sliding. A continuous x tween without these readable phases is a position change, not a walk.
