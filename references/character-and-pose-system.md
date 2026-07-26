# Character and pose system

## Identity bible

Approve one identity reference per recurring character before generating pose volume. Record face shape, age, body proportions, hair, costume silhouette, palette, footwear, signature prop, and forbidden changes.

Use the approved image as the visual reference for every later atlas. Do not describe identity from memory after the first generation.

## Complete-pose default

Generate complete connected bodies with full scalp, hands, sleeves, legs, and shoes. Keep safety margin around every atlas cell. Avoid anatomy seams even when that reduces local rig freedom.

Minimum recurring-character set:

- neutral three-quarter stance;
- left and right walk contacts;
- one or two passing poses;
- listen/look reaction;
- speak/point reaction;
- surprise, concern, or setback;
- story-specific action;
- calm final pose.

Use more poses only when a visible state change needs them.

For travel, use a normalized six-frame gait cycle: `weight-bearing → lift → contact → transition → opposite contact → settle`. Keep every frame on one canvas with the same character center, foot baseline, transparent padding, scale, and facing direction. A parent world-space track may carry the cycle across the floor; translation-only tweens do not count as walking.

When the contact problem is harder than the motion problem, step back from a cutout atlas and generate a full-scene multi-frame state instead. Bed + body + bedding + canopy, lamp + flame, and similar causal units should remain together when separating them would make perspective or contact ambiguous.

## Ensemble poses

Generate actors as one connected ensemble when they share a load, contact, or precise spatial relationship. Include the common load and its attachment points in the same atlas cell when separating them would create gaps.

Examples: two people carrying one pole, lifting a table, embracing, supporting an injured person, pulling one rope together, or passing a heavy bucket hand-to-hand.

Require every ensemble cell to contain the exact actor count, one continuous shared object, valid contact points, and no extra limbs or duplicate props.

## Atlas production

Prefer a 2×2 or 3×2 grid on a high-purity chroma background when transparent generation is unreliable. Keep each pose inside one cell; disconnected held items must remain inside that cell.

After keying and splitting, audit alpha, edge contact, empty cells, crop safety, and accidental baked effects. Do not patch a missing head with an unrelated generated head unless identity and neck contact can be proven; regenerate the pose first.
