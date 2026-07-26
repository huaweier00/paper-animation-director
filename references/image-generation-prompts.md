# Image-generation prompt contracts

Use the `imagegen` skill for all generated or edited raster assets. Inspect every referenced image before editing it.

## Shared style block

Define medium, paper, line quality, palette, edge treatment, lighting, and depth once. Reuse it across backgrounds, characters, props, and effects. Keep story identity separate from the style block.

Example dimensions to specify: hand-painted watercolor and ink, fibrous xuan paper, warm off-white cut edge, restrained pigment bloom, soft contact shadow, no digital vector gloss.

## Background prompt

Require:

- no characters;
- no text or watermark;
- no story-critical moving props or effects baked in;
- clear foreground, middle ground, and distance;
- staging space for the planned actor path;
- explicit light direction and time of day;
- extra bleed beyond the frame for camera movement.

Before writing the prompt, attach a spatial-plan note: period and room function, camera side, floor line, actor paths, light axis, foreground occluders, and subtitle-safe zones. Historical prompts must include both evidence-derived features to adopt and later-period elements to exclude; “ancient palace” alone is not a usable brief.

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

## Ensemble prompt

Describe one complete physical unit. State exact actor count, shared object count, contact points, load direction, pose phase, and forbidden duplicates. Ask for the same ensemble across several gait or effort phases rather than generating each actor separately.

## Prop and effect prompt

Generate a clean isolated prop only when it needs independent motion. Specify useful anchor points such as bucket mouth, rope attachment, hinge, handle, impact edge, water line, or flame origin. Avoid baked shadows when the prop will travel; generate or animate its contact shadow separately.

## Re-roll policy

Re-roll weak assets before animation. Reject identity drift, missing body parts, accidental scenery, embedded text, baked fire/water, inconsistent light, wrong actor count, cropped feet, duplicate props, or contact that cannot support the planned action.

Also reject an asset that is beautiful but unsuitable for the current room, period, camera side, scale, light direction, or action. Reuse is subordinate to spatial and semantic fit.
