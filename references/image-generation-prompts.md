# Image-generation prompt contracts

Use the `imagegen` skill for all generated or edited raster assets. Inspect every referenced image before editing it.

For `premium-quality-first` work, read `visual-art-direction-and-asset-quality.md` before identity or shot asset generation. An asset prompt must inherit the approved visual-direction blocks and the shot contract; adjectives such as “高级、唯美、电影感、8K” do not replace shape, value, palette, line, texture, light, depth, composition, and forbidden-trait decisions.

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

After the complete animatic and visual route pass, lock this global style block, the approved frontal identity anchors, and the minimum controlled reference-only model packs justified by the sequence layout. Do not pre-generate final backgrounds, props, effects, action poses, gait atlases, ensembles, or full-scene plates.

## Frontal identity-reference prompt

Generate one person only, front-facing, neutral, preferably full-body, with an unobstructed face, complete costume silhouette, natural proportions, and plain non-narrative background. Exclude walking, gesturing, emotional acting, scenery, interaction, story props, text, watermark, chroma-key production requirements, and alternate views.

Record the result as reference-only generation conditioning. Do not treat it as an animation-ready character cutout.

## Controlled model-pack prompts

After sequence layout establishes the required camera sides, generate only the recurring character's needed left profile, right profile, and useful three-quarter construction views. Condition every view from the canonical frontal anchor. Keep the same neutral construction, grounded baseline, body-height scale, light-neutral presentation, costume logic, and identity; exclude story action and final-shot staging.

Record view name, scale reference, asymmetry, expression range, attachment points, forbidden variations, and approval. Mark every model-pack image `reference_only: true` and `animation_use: false`. The pack removes construction ambiguity; it is not a production atlas or a generic pose library.

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

Also require the active shot’s exact camera side, screen travel direction, facing, gaze, action target, and light direction. Use the canonical anchor for identity and the approved model-pack view for side-correct construction; do not copy either neutral reference pose into the action.

After extraction, register each production file in `asset-facts.json` from observed pixels. Record its SHA-256, intrinsic facing, forward axis, observed head/chest/gaze, support/contact evidence, mirror policy, and orientation-evidence frame. A prompt or filename is not orientation evidence.

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

Re-roll weak assets before animation. For every visually dominant asset, compare materially useful candidates at the same crop and intended display scale, record the selected candidate and rejection reasons, then test the selection in the real composite. Never auto-approve the first plausible output. Prefer deterministic drawing, typography, or compositing when additional generations would not solve the defect.

Record the intended maximum frame fraction, source pixel dimensions, close-up suitability, art-direction match, and composite-test result for every approved dominant asset. Upscale only after composition and crop approval; upscaling does not repair anatomy, line, light, perspective, or generic design.

Reject identity drift, missing body parts, accidental scenery, unintended embedded text, baked fire/water, inconsistent light, wrong actor count, cropped feet, duplicate props, or contact that cannot support the planned action.

Also reject an asset that is beautiful but unsuitable for the current room, period, camera side, scale, light direction, travel vector, facing, target, or action. A generated person moving left when the approved shot requires movement right is a failed asset. A window cannot replace a wall that narration identifies as the writing surface.

Reject a prop that is semantically present but visually unrecognizable, physically unsupported, implausibly scaled, or only readable after narration explains it. Compare weapons, plants, currency, official documents, vehicles, tools, containers, and food against at least one concrete structural reference before approval.

Treat every existing asset as an unapproved candidate until it passes the current shot contract. Do not force-fit it because generation was expensive. Do not mirror by default; permit mirroring only after an explicit audit of asymmetry, text, handedness, props, light, contact, and adjacent-shot continuity.

Also reject a technically correct asset that fails the selected visual world: unclear focal hierarchy, muddy value separation, random saturation, dead-eyed or neutral acting, stiff symmetry, incompatible edge/texture scale, pasted-on lighting, generic AI ornament, or a silhouette that disappears at phone size.
