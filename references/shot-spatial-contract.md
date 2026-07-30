# Shot spatial contract

Use one contract per production shot. Treat each manifest `scene` as one shot unless the project explicitly subdivides it. Approve this contract before generating any background, pose, gait, prop, effect, ensemble, or full-scene plate.

## Coordinate system

Use normalized screen coordinates from `0.0` to `1.0`. Represent a rectangular zone as `[left, top, right, bottom]`, where `left < right` and `top < bottom`. Name every corridor, obstacle, surface, prop, and action target.

Record:

- camera view, continuity axis, floor line, light direction, and entry/exit sides;
- actor start/end zones, travel direction, facing, gaze, locomotion, and minimum clearance;
- clear motion corridors and non-passable obstacles;
- declared support surfaces for feet, hooves, wheels, seated bodies, hanging objects, plants, documents, and placed props;
- foreground/midground occluders, their depth order, and whether they may cover a character;
- surfaces and props with the actions they physically and semantically support;
- critical-prop class, silhouette, scale reference, material, attachment/contact, state sequence, proof time, and forbidden substitutes;
- protected head/face regions, proof area, and subtitle-safe zones.

## Feasibility gate

Reject the spatial plan before generation when any condition fails:

1. An actor start or end zone falls outside the named motion corridor.
2. A motion corridor intersects a non-passable obstacle or is narrower than the actor/shared load requires.
3. The travel vector conflicts with facing, feet, torso, gaze, entry, or exit without an explicit story-motivated exception.
4. The action target does not exist, does not support the action, is unreachable, or is hidden at the proof moment.
5. Furniture or decoration consumes the space needed for travel, contact, reaction, or subtitles.
6. The camera cannot show actor, contact, target, and result in a semantically readable composition.
7. Adjacent shots reverse screen direction or cross the continuity axis without a visible turn or re-establishing shot.
8. A frame edge, container, crop, mask, matte, or undeclared occluder can cut through the head or face at a required review time.
9. A standing actor, animal, wheel, vehicle, plant, notice, treasure container, weapon, or placed prop lacks a named support or attachment surface.
10. A critical prop can satisfy the narration only as an abstract line, icon, mound, color patch, or unexplained floating shape.
11. A collective command has no readable initial state, command/gesture, response state, and final result.

Fix the layout, camera, action, or shot division before generating assets. Do not solve a failed spatial plan by shrinking the actor, passing through objects, or selecting an unrelated target.

## Head, face, and occlusion contract

Add a `review_contract` to every shot. Protect at least `head`, `face`, `hands`, `feet`, and `action-contact`. Set edge clipping and unplanned occlusion to `reject`.

Differentiate:

- **natural profile**: the skull, facial contour, visible eye/nose/mouth, neck connection, and pose remain anatomically coherent;
- **planned physical occlusion**: a visible doorframe, curtain, plant, person, or foreground layer crosses the character with a declared depth order and time window;
- **clipping failure**: a straight or container-shaped boundary removes half the face, scalp, eye line, nose, mouth, jaw, or neck without a believable occluding object.

For every planned face/head occlusion, declare actor, occluder, start/end, narrative reason, and an `identity_proof_time` outside the occlusion interval. Review the frame immediately before entry, the most-covered frame, and immediately after exit. Keep the proof frame and any dialogue close-up unobstructed unless the obstruction itself is the approved story event.

Reject and fix:

- `overflow: hidden` or a scene-host rectangle slicing a moving head;
- an alpha crop, mask, matte, foreground edge, subtitle, watermark, or transition covering identity-critical facial features;
- a pose swap whose canvases have different head padding and create a temporary amputation;
- a z-order change that places architecture across the face without a declared pass-behind action;
- a crop that removes the scalp or half the face while pretending to be a close-up.

Fix the source asset, canvas padding, host overflow, mask path, z-order, actor path, camera, crop, or foreground design. Do not conceal the defect with motion blur, fast timing, grain, or another overlay.

## Direction contract

For normal forward travel:

- `left-to-right` requires the end zone to be right of the start zone and `facing: right`;
- `right-to-left` requires the end zone to be left of the start zone and `facing: left`;
- `stationary` requires materially identical start/end centers and may use `facing: front`, `left`, or `right`.

Use `locomotion: backward-walk` plus a non-empty `exception_reason` only when the story visibly requires retreat. Otherwise reject a facing mismatch. Do not rotate or mirror a wrong-facing result by default.

## Semantic targets

Give every story action an exact target ID. The target must list the action in `supports_actions`.

Examples:

- `write-on` targets a writable `wall`, board, paper, or equivalent surface;
- `sit-on` targets a stable seat or platform at a reachable height;
- `open` targets a door, lid, window sash, or container with a visible contact point;
- `pick-up` targets a visible movable prop;
- `pour-into` targets a container or area that can visibly receive a stream.

Treat nearby visual similarity as insufficient. If narration says “write on the wall,” a window with no writing affordance is a forbidden substitute.

## Support and grounding contract

Give every subject that carries weight a `support_surface` or `attachment_target`.

Review:

- feet and hooves against the visible road/floor line;
- wheels against the same perspective plane as the animals and guide;
- seated bodies against seat height and contact;
- hanging notices against a hook, cord, frame, or wall;
- boxes, lamps, gold, and vessels against a hand, table, platform, or ground;
- rooted plants against soil, bank, cracks, or waterbed;
- arrows against the bow hand, bow body, and string;
- thread, rope, and jewelry against a visible knot, wrist, handle, anchor, or load.

Contact shadows help confirm support but cannot compensate for impossible scale or perspective. Reject a guide who is compositionally “ahead” but whose feet float above the road, cross a horse, or share the vehicle’s wrong scale track.

## Critical-prop recognizability contract

For each narrated or plot-bearing prop, add:

```yaml
critical_props:
  - id: reward-gold
    class: period-appropriate-gold-object
    silhouette: thick gold cakes inside an open dark box
    scale_reference: palm-sized pieces
    material_cues: warm metallic highlight, visible thickness, stamped center
    support_or_attachment: inside reward-box on platform
    state_sequence: [closed, opened-and-readable, withdrawn-from-betrayer]
    proof_time: 6.2
    forbidden_substitutions: [soil-pile, red-mound, triangle-icon, flat-yellow-circles]
```

Review the object at the size it occupies in the rendered MP4. If a reviewer can only call it “a shape,” “a pile,” or “a line,” it fails even when the prompt named it correctly.

For text-bearing props, generate the physical base separately and composite verified text deterministically. The finished notice must look like a real document from the story world, not a UI placeholder.

## Command-state contract

For orders that alter a group state, declare:

```yaml
command_state:
  initial: bows aimed at the deer
  command: king raises one hand and issues the order
  propagation: front rank lowers first, rear ranks follow
  final: arrowheads point to the ground and remain there
  audio_line_id: scene-08-narrator-lower-bows
  proof_time: 8.4
```

The spoken line, issuing gesture, propagated response, and final state must occupy one coherent time window. Do not let narration claim the order happened before or after the visible response.

## Shot asset gate

After the contract passes, set `asset_plan.generation_policy: shot-just-in-time` and `asset_plan.space_approved: true`. List only the assets needed to prove this shot. For every character asset, record `actor_id`, the approved identity-reference ID, camera side, facing, screen direction, light direction, action, and target.

Reject generated or reused assets when any hard field differs. Existing availability never overrides shot fit.

Permit horizontal mirroring only after recording that all of these remain valid:

- costume, hair, scars, insignia, and other asymmetry;
- written text and directional symbols;
- handedness and held-object ownership;
- light and cast-shadow direction;
- contact geometry and load direction;
- entry/exit and adjacent-shot continuity.

## Example: walk right and write on a wall

```yaml
spatial_contract:
  coordinate_system: normalized-screen
  camera:
    view: three-quarter-side
    axis: locked
    floor_line: 0.82
    light_direction: left-to-right
  surfaces:
    - id: writing-wall
      type: wall
      zone: [0.70, 0.14, 0.96, 0.75]
      supports_actions: [write-on]
    - id: window
      type: window
      zone: [0.08, 0.12, 0.32, 0.70]
      supports_actions: []
      forbidden_actions: [write-on]
  obstacles:
    - id: low-table
      zone: [0.38, 0.66, 0.50, 0.80]
      passable: false
  occluders:
    - id: foreground-curtain
      zone: [0.00, 0.08, 0.07, 0.96]
      depth: foreground
      may_cover_characters: false
  reserved_zones:
    - id: actor-corridor
      zone: [0.08, 0.44, 0.78, 0.90]
      purpose: actor-motion
      must_remain_clear: true
  actors:
    - id: artisan
      start_zone: [0.10, 0.52, 0.22, 0.84]
      end_zone: [0.60, 0.50, 0.72, 0.84]
      travel:
        direction: left-to-right
        facing: right
        locomotion: forward-walk
        path_zone: actor-corridor
        minimum_clearance_actor_widths: 1.25
      action:
        type: write-on
        target: writing-wall
        contact: right-hand-with-brush
        proof: brush touches the blank wall and visible marks remain
      support_surface: ground
asset_plan:
  generation_policy: shot-just-in-time
  space_approved: true
review_contract:
  protected_regions: [head, face, hands, feet, action-contact]
  edge_clipping: reject
  unplanned_occlusion: reject
  review_times: [0.0, 2.0, 4.0]
  intentional_occlusions: []
```
