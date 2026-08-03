# Visual art direction and asset quality

Use this reference for every `premium-quality-first` project and every feed-native social film. It turns “大众审美、精美、素材质量高” into reviewable decisions without reducing the film to a generic style.

## Contents

1. What broad appeal actually means
2. Design for children and adults at the same time
3. Build a visual-direction contract
4. Prove the look before production
5. Generate and curate premium assets
6. Integrate assets into one believable world
7. Review at phone size
8. Reject generic AI imagery
9. Visual gates and required records

## 1. What broad appeal actually means

Do not interpret “符合大众审美” as “copy the safest popular style.” Broad appeal is the overlap of four qualities:

1. **Immediate readability** — one focal subject, clear silhouette, legible emotion/action, and understandable depth.
2. **Sensory pleasure** — controlled value groups, harmonious color, clean edges, coherent light, and intentional rhythm.
3. **Emotional truth** — pose, gaze, spacing, light, and environment support the scene’s feeling rather than decorating it.
4. **Memorable authorship** — one recurring motif, shape language, palette behavior, or staging signature makes the episode recognizable.

Readability without finish feels cheap. Finish without readability feels like a poster. Readability and finish without a signature feel like interchangeable AI output.

Judge the frame in this order:

```text
What do I see first? → What is happening? → How should I feel? → What detail rewards another look?
```

If the first answer is “everything,” the frame has no hierarchy. If the last answer is “nothing,” the frame may be clear but not collectible.

## 2. Design for children and adults at the same time

Use a two-layer audience design rather than a childish/adult style compromise.

### Immediate layer

This layer should work for a child, a hurried viewer, or anyone watching without sound:

- large, distinct character and prop silhouettes;
- readable face, gaze, gesture, and action target;
- a small number of organized color masses;
- clear danger, desire, choice, surprise, or consequence;
- foreground/middle-ground/background separation;
- motion and sound accents tied to meaningful changes.

### Reward layer

This layer gives adults and repeat viewers a reason to stay, rewatch, or save:

- restrained material detail and culturally credible objects;
- subtle changes in posture, expression, weather, and light;
- visual metaphor that remains understandable without explanation;
- compositional echoes between opening and ending;
- historical, literary, or practical detail worth pausing on;
- a final frame or card that is useful as an image by itself.

Never make the immediate layer depend on the reward layer. A tiny symbol can enrich a scene; it cannot carry the only proof of the main action.

## 3. Build a visual-direction contract

Create `visual_direction` in the story manifest after the scratch animatic passes and before formal identity or shot assets. The contract must include:

- `audience_layers.immediate_read`: the primary action/emotion a fast viewer must read;
- `audience_layers.adult_reward`: the craft, subtext, or cultural detail that rewards attention;
- `emotional_promise`: the feeling arc the visual system must produce;
- `art_route`: a concise name for the selected visual world;
- `shape_language`: dominant shapes for heroes, threats, environments, and props;
- `value_design`: focal subject, focal order, subject/background separation, and dark/light mass policy;
- `color_script`: base palette, accent policy, and emotional change across the film;
- `line_and_texture`: line hierarchy, surface treatment, texture scale, and forbidden surface traits;
- `lighting_and_depth`: key-light direction, atmospheric-depth plan, contact-shadow policy, and shot-to-shot continuity;
- `composition`: big/medium/small mass plan, negative-space use, phone focal point, and subtitle-safe integration;
- `signature`: one specific recurring visual idea that belongs to this series or episode;
- `anti_generic`: a concrete forbidden-traits list;
- `lookdev`: route comparison, selected route, hero concept frames, and review decisions;
- `asset_policy`: candidate comparison, rejection logging, composite testing, and finish rules.

Use concrete art language. “高级国风、唯美、电影感、细节丰富” is not a contract. Prefer statements such as:

```text
The rabbit is a warm ivory oval mass against a cool gray-green field.
Threats use narrow diagonals; safety uses enclosing arcs.
Only the decision object receives vermilion.
The brightest value belongs to the face and hand-object contact.
Background detail loses contrast and edge sharpness with depth.
```

### Core frame-design principles

#### Focal hierarchy

Declare the intended first, second, and third read. Use value, scale, saturation, edge contrast, isolation, gaze, and directional lines to support that order. Do not sharpen and saturate every object.

#### Big, medium, small

Organize the frame into a few unequal masses. Avoid equal-size figures in a row, evenly distributed decorations, repeated identical trees, and symmetrical empty staging unless symmetry is the story point.

#### Value grouping

Make the frame readable in grayscale. Separate the subject from the background with value, temperature, edge, or a controlled combination. Low contrast can be beautiful, but the focal relation must survive.

#### Color behavior

Choose a restrained base family and reserve saturation for narrative emphasis. Let color change with the emotional arc. Do not use a random attractive palette independently in every shot.

#### Edge hierarchy

Keep the focal face, gesture, or critical object clean. Let distant or atmospheric edges soften. Do not apply the same generated sharpness, outline weight, or texture noise everywhere.

#### Spatial depth

Use overlap, scale, perspective, atmospheric contrast, controlled blur, and contact shadow to integrate layers. Parallax is useful only when the underlying depth design is coherent.

#### Character appeal

“Cute” is not the only form of appeal. Require a recognizable silhouette, clear age and temperament, expressive eyes/gaze, appealing proportion rhythm, complete anatomy, and poses that show intention. Avoid neutral standing figures used as placeholders for acting.

## 4. Prove the look before production

Do not let the first plausible generated image silently define the project.

### V0 — visual audience brief

Write the two audience layers, emotional promise, expected collectible frame, and undesirable audience impression. Examples of undesirable impressions include “AI children’s picture book,” “museum educational slide,” “cheap cutout,” “muddy antique filter,” or “mobile game ad.”

### V1 — three materially different routes

Develop at least three reference-only art routes. Change the design logic, not merely hue:

- route A may use soft gongbi lines, shallow depth, and mineral accents;
- route B may use bold cut silhouettes, theatrical light, and sparse texture;
- route C may use watercolor atmosphere, graphic shapes, and selective ink detail.

Record each route’s differentiator, strengths, risks, and likely audience impression. References may guide medium, composition, period detail, or color separately; do not copy one living artist’s signature style.

### V2 — hero look-development triad

For each viable route, make low-cost, reference-only concept frames for:

1. opening pressure or anomaly;
2. central choice/conflict/contact;
3. consequence or final collectible image.

Use approved scratch compositions as seeds. These are non-deliverable look-development references, not production backgrounds or character poses, and must be marked `reference_only: true`. This preserves the shot-specific asset rule.

Compare routes on the same criteria and viewing sizes. Select one route with a written rationale; never select only because it was generated first or cost more.

### V3 — character/environment integration benchmark

Before producing the film, create one reference-only composite that places a representative character, prop, and environment in the selected world. Prove:

- the face and silhouette survive the background;
- character and environment share perspective, light, edge treatment, texture scale, and color atmosphere;
- feet/contact points and cast/contact shadows belong to the surface;
- foreground and depth effects do not look pasted on;
- the frame still works at intended phone size.

The identity reference remains neutral and reference-only. The benchmark is an art-integration proof, not a reusable shot asset.

### V4 — style lock

Approve the selected route, hero triad, integration benchmark, phone-size review, grayscale review, blur/focal review, and anti-generic list before formal identity generation or shot assets.

If the look fails, revise the art route. Do not try to fix a weak visual system by generating more shots.

## 5. Generate and curate premium assets

Asset quality has four stages:

```text
source quality → selection quality → composite integration → motion performance
```

A beautiful isolated PNG can still produce a poor frame. Review the final intended use, not only the source file.

### Prompt from the locked system

Every asset prompt must inherit the approved shape, value, palette, line/texture, light, depth, and forbidden-trait blocks in addition to the shot’s spatial and semantic contract. “Same style” is not sufficient.

### Compare candidates

For every hero character pose, hero background, close-up prop, cover, save frame, and other visually dominant asset:

- generate or construct multiple materially useful candidates;
- compare them side by side at the same crop and intended display scale;
- record the selected candidate and concise rejection reasons;
- reject the first plausible result unless it genuinely wins the comparison;
- avoid candidate inflation when deterministic drawing, typography, or compositing is the better tool.

Candidate count is a production judgment except for the three-route look-development gate. The requirement is a real comparison, not an arbitrary quota.

### Selection rubric

Review candidates in this order:

1. **semantic fit** — correct person, object, action, emotion, period, and story function;
2. **silhouette and pose** — clear at intended size, with readable direction and intent;
3. **identity and anatomy** — stable face/body/costume, complete connected forms, credible hands/feet/contact;
4. **composition fit** — correct camera, crop, negative space, focal order, and subtitle space;
5. **value and color fit** — subject separation and palette role match the selected route;
6. **light and depth fit** — shared light axis, perspective, atmosphere, and support surface;
7. **finish** — clean edges, controlled texture, no artifacts, enough resolution for the intended maximum scale;
8. **distinctiveness** — supports the project signature rather than default AI prettiness.

Beauty cannot rescue failure in an earlier category.

### Record intended display scale

For each approved asset, record its intended maximum fraction of the frame and source pixel dimensions. A distant figure may be acceptable at modest resolution; a face close-up, cover subject, or final save image needs more source detail. Do not upscale before the composition and crop are approved. Upscaling cannot restore malformed anatomy, incoherent line work, or fake detail.

### Reject before animation

Reject:

- face, costume, age, species, or proportion drift;
- dead eyes, neutral placeholder acting, stiff symmetric poses, or unclear gaze;
- extra/missing digits or limbs, fused contacts, broken object construction;
- muddy low contrast, uncontrolled saturation, texture soup, or haloed edges;
- baked text, watermarks, lighting, shadows, or effects that conflict with the shot plan;
- perspective, camera side, scale, crop, light, or direction mismatch;
- detail that disappears at phone size or competes with the focal subject;
- a generic result that ignores the locked signature.

Keep a rejection log. Repeated rejection reasons must update the prompt block, reference conditioning, or generation method before another batch.

## 6. Integrate assets into one believable world

The final composite, not the asset folder, is the real artwork.

### Match five joins

For each character/prop/background join, check:

1. **perspective join** — horizon, camera height, foreshortening, and ground plane agree;
2. **light join** — direction, softness, value range, color temperature, and shadow behavior agree;
3. **edge join** — outline weight, sharpness, alpha treatment, and atmospheric falloff agree;
4. **material join** — texture scale and surface response belong to the same medium;
5. **contact join** — feet, hands, roots, wheels, props, shadows, and occlusion prove shared space.

If several assets require contradictory correction to coexist, regenerate the weakest source rather than stacking filters over the whole frame.

### Use selective finishing

Polish the focal area more than the periphery. Use deterministic paint-over, inpainting, masking, typesetting, color matching, edge cleanup, and shadow construction where they solve a specific defect. Avoid one global “cinematic” LUT that crushes faces, muddies mineral colors, or hides mismatched sources.

### Keep motion inside the art direction

Motion changes the perceived quality of the art. Preserve pose appeal, silhouette, line quality, and contact during movement. Do not deform a beautiful source through rubbery easing, scale pulsing, uncontrolled mesh warping, or continuous camera drift. Use stillness when it protects the image; use local motion when it strengthens attention or emotion.

## 7. Review at phone size

Review the selected route, cover, hero frames, every shot release, and final film under real viewing conditions.

### Phone-size test

Display the frame at its intended physical feed size with platform UI and captions. Confirm the primary face/action/object can be identified immediately. Do not approve only on a large desktop monitor.

### Grayscale test

Remove color temporarily. Confirm focal order, subject/background separation, depth, and text readability. Restore color after the check; grayscale is a diagnostic, not the intended delivery.

### Blur/squint test

Blur or view the frame very small. The major masses and intended focal point should remain. If decorative detail becomes the strongest mass, simplify or rebalance.

### Silhouette test

Check the primary character/action as a dark shape. Limb direction, gaze, held object, and contact should remain understandable where the shot depends on them.

### Three-distance test

Review:

- thumbnail/cover size for promise and subject;
- normal phone feed size for action, emotion, caption, and value hierarchy;
- enlarged crop for face, anatomy, line work, texture, edge, and compression defects.

All three must pass. A frame can be attractive enlarged and fail in the feed, or read well small and fall apart under inspection.

## 8. Reject generic AI imagery

Common generic failure patterns include:

- beige/teal antique grading applied to every story;
- symmetrical centered characters with decorative empty scenery;
- uniformly sharp, uniformly detailed “texture soup”;
- attractive but emotionally neutral faces and mannequin poses;
- random floating petals, dust, ink, or light leaks used as false richness;
- incompatible painting styles between character, prop, and background;
- fake handwritten text or ornamental pseudo-history;
- default cute proportions that erase age, role, danger, or cultural specificity;
- repeated background formulas and camera pushes across every episode.

The `anti_generic.forbidden_traits` list must be project-specific. Add a failure when it appears; remove nothing merely because the generator often produces it.

## 9. Visual gates and required records

Use this order for `premium-quality-first` work:

- **V0** — audience layers, emotional promise, collectible-frame goal, undesirable impression;
- **V1** — three materially different art routes with strengths and risks;
- **V2** — reference-only opening/conflict/consequence hero frames and written selection;
- **V3** — reference-only character/prop/environment integration benchmark;
- **V4** — approved style lock after phone, grayscale, blur/focal, and anti-generic review;
- **A1** — shot-specific candidate comparison and rejection record for dominant assets;
- **A2** — approved composite test at intended crop and maximum display scale;
- **A3** — shot release passes art-direction match, focal hierarchy, value separation, color/light coherence, character/environment integration, asset finish, and phone readability.

Required records:

- `story-manifest.json.visual_direction`;
- reference board or source ledger with the purpose of each reference;
- route comparison and reference-only hero frames;
- reference-only integration benchmark;
- per-asset selection/rejection records for dominant assets;
- per-shot release checks from rendered MP4 frames;
- final feed, cover, and save-frame reviews.

When a visual review fails, return to the earliest responsible layer: art route, composition, source asset, integration, motion, caption, or encode. Do not hide a source failure with grain, blur, bloom, camera movement, or music.
