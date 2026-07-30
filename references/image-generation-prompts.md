# Image-generation prompt contracts

Use the `imagegen` skill for all generated or edited raster assets. Inspect every referenced image before editing it.

## Shared style block

Define animation method, visible medium, line quality, palette, edge treatment, lighting, and depth once. Reuse it across backgrounds, characters, props, and effects. Keep story identity separate from the style block.

Do not infer visible paper texture from the phrase “paper animation.” Paper animation may describe complete 2D layers and controlled state changes while the visible surface remains smooth gongbi painting, silk-like color, mural mineral pigment, watercolor, or another user-approved medium.

Example soft-gongbi style block:

```text
soft hand-painted gongbi color, fine controlled ink line,
silk-like smooth ground, thin mineral-pigment washes,
gentle low-contrast atmosphere, restrained contact shadow,
no heavy paper fiber, no torn white cut edge, no cardboard thickness,
no embossed relief, no curled paper, no pulp grain, no vector gloss
```

When the user explicitly requests fibrous xuan paper or cut-paper edges, describe those instead. Keep an explicit `surface_forbidden` list so a rejected surface style does not return in later shots.

Lock only this global style block and the approved frontal identity references before shot production. Do not pre-generate backgrounds, props, effects, poses, gait atlases, ensembles, or full-scene plates.

## Frontal identity-reference prompt

Generate one person only, front-facing, neutral, preferably full-body, with an unobstructed face, complete costume silhouette, natural proportions, and plain non-narrative background. Exclude walking, gesturing, emotional acting, scenery, interaction, story props, text, watermark, chroma-key production requirements, and alternate views.

Record the result as reference-only generation conditioning. Do not treat it as an animation-ready character cutout.

## Shot contract input

Do not write an asset prompt until the active shot has `asset_plan.space_approved: true`. Copy these constraints from `spatial_contract` into every relevant prompt:

- shot ID, camera view, floor line, scale, and light direction;
- actor start/end zones, screen travel direction, facing, gaze, and locomotion mode;
- named motion corridor, obstacles, and minimum clearance;
- exact action type, semantic target ID/type, contact point, and proof state;
- entry/exit continuity, foreground occluders, subtitle-safe zones, and forbidden substitutions.

## Background prompt

Require:

- no characters;
- no text or watermark;
- no story-critical moving props or effects baked in;
- clear foreground, middle ground, and distance;
- staging space for the planned actor path;
- explicit light direction and time of day;
- extra bleed beyond the frame for camera movement.

Before writing the prompt, attach the approved spatial contract: period and room function, camera side, floor line, actor paths, minimum clearances, obstacles, semantic targets, light axis, foreground occluders, and subtitle-safe zones. Reserve the named actor corridor and target area; do not fill them with decorative furniture. Historical prompts must include both evidence-derived features to adopt and later-period elements to exclude; “ancient palace” alone is not a usable brief.

Also reserve declared support surfaces. A road must remain visible beneath the guide, soldiers, hooves, and wheels; a riverbank plant needs a visible root point; a wall notice needs a physical wall or posting board.

## Character atlas prompt

Require:

- the same referenced person in every cell;
- exact grid dimensions and exact pose count;
- full scalp, hands, legs, and shoes;
- identical costume, palette, proportions, and facial identity;
- no crop and generous margin in each cell;
- flat chroma or transparent background;
- no text, watermark, fire, scenery, or unrequested props;
- no pose crossing a cell boundary.

Also require the active shot’s exact camera side, screen travel direction, facing, gaze, action target, and light direction. Use the frontal identity image only to preserve identity; do not copy its front-facing neutral pose into the action.

## Ensemble prompt

Describe one complete physical unit. State exact actor count, shared object count, contact points, load direction, pose phase, and forbidden duplicates. Ask for the same ensemble across several gait or effort phases rather than generating each actor separately.

## Prop and effect prompt

Generate a clean isolated prop only when it needs independent motion. Specify useful anchor points such as bucket mouth, rope attachment, hinge, handle, impact edge, water line, or flame origin. Avoid baked shadows when the prop will travel; generate or animate its contact shadow separately.

For every story-critical prop, write a recognizability contract before prompting:

- real-world or historical class;
- silhouette and construction;
- size relative to a hand, forearm, body, vehicle, or architecture;
- material cues such as thickness, grain, specular highlight, fold, seal, or root;
- support or attachment point;
- required state sequence;
- proof time;
- forbidden abstract substitutes.

Examples:

- An arrow must visibly relate to the bow, string, hand, and body scale. A cross-frame direction line is not an arrow.
- Riverbank sedge must show roots or a rooted clump, narrow leaves, hand contact, and a physically credible break point. A floating green ribbon is not water grass.
- Gold must use a period-appropriate recognizable object form with thickness, metallic highlights, container/support, and stable scale. A red mound, triangle, or flat yellow circle is not treasure.
- A vow thread must be tied, held, worn, tightened, cut, or broken at a visible attachment point. A long line entering from offscreen is not a readable oath.

## Text-bearing props

Do not rely on an image model to improvise important proclamations, notices, maps, labels, seals, prices, or reward amounts. When textual meaning is story-critical:

1. generate a historically credible blank scroll, board, tablet, or paper base;
2. typeset verified text deterministically as a separate editable layer;
3. add seals and hierarchy only after checking period, direction, contrast, and readability;
4. review the finished prop at its actual on-screen size.

Reject placeholder horizontal lines, generic animal icons, emoji-like symbols, or modern infographic shorthand when the story requires an official document.

## Re-roll policy

Re-roll weak assets before animation. Reject identity drift, missing body parts, accidental scenery, unintended embedded text, baked fire/water, inconsistent light, wrong actor count, cropped feet, duplicate props, or contact that cannot support the planned action.

Also reject an asset that is beautiful but unsuitable for the current room, period, camera side, scale, light direction, travel vector, facing, target, or action. A generated person moving left when the approved shot requires movement right is a failed asset. A window cannot replace a wall that narration identifies as the writing surface.

Reject a prop that is semantically present but visually unrecognizable, physically unsupported, implausibly scaled, or only readable after narration explains it. Compare weapons, plants, currency, official documents, vehicles, tools, containers, and food against at least one concrete structural reference before approval.

Treat every existing asset as an unapproved candidate until it passes the current shot contract. Do not force-fit it because generation was expensive. Do not mirror by default; permit mirroring only after an explicit audit of asymmetry, text, handedness, props, light, contact, and adjacent-shot continuity.
