# Character and pose system

## Identity bible

Approve exactly one neutral frontal identity reference per recurring character before any shot asset generation. Prefer a full-body frame that clearly records face shape, age, body proportions, hair, costume silhouette, palette, footwear, and signature identity details. Keep the background plain and exclude story action, interaction, expressive posing, and scene-specific props.

Mark it `purpose: identity-consistency-reference-only` and `animation_use: false`. Use it as visual conditioning for every later shot-specific generation. Never key, animate, place, or deliver the frontal reference as a shot asset. Do not describe identity from memory after approval.

Do not create side views, turnarounds, expression sheets, gait cycles, or a general pose library during identity lock. Global style rules may be fixed early; all concrete character poses are designed only after the active shot’s semantic and spatial contracts are approved.

## Complete-pose default

Derive the minimum complete connected poses from the active shot only. Generate full scalp, hands, sleeves, legs, and shoes with safety margin around every atlas cell. Avoid anatomy seams even when that reduces local rig freedom. Do not generate a pose merely because it may become useful later.

When an approved shot visibly requires travel, generate a normalized six-frame gait cycle for its exact camera side and facing direction: `weight-bearing → lift → contact → transition → opposite contact → settle`. Keep every frame on one canvas with the same character center, foot baseline, transparent padding, scale, light, and facing. A parent world-space track may carry the cycle across the approved corridor; translation-only tweens do not count as walking.

Reject a gait whose travel vector conflicts with head, shoulders, chest, feet, or gaze. Regenerate it instead of rotating, mirroring, or force-fitting it. Permit mirroring only after documenting that costume, hair, held objects, text, handedness, light, contact, and adjacent-shot continuity remain valid.

When the contact problem is harder than the motion problem, step back from a cutout atlas and generate a full-scene multi-frame state instead. Bed + body + bedding + canopy, lamp + flame, and similar causal units should remain together when separating them would make perspective or contact ambiguous.

## Ensemble poses

Generate actors as one connected ensemble when they share a load, contact, or precise spatial relationship. Include the common load and its attachment points in the same atlas cell when separating them would create gaps.

Examples: two people carrying one pole, lifting a table, embracing, supporting an injured person, pulling one rope together, or passing a heavy bucket hand-to-hand.

Require every ensemble cell to contain the exact actor count, one continuous shared object, valid contact points, and no extra limbs or duplicate props.

## Atlas production

Prefer a 2×2 or 3×2 grid on a high-purity chroma background when transparent generation is unreliable. Build it inside the active shot directory and record the shot ID, identity reference, camera side, screen direction, facing, light direction, and required action. Keep each pose inside one cell; disconnected held items must remain inside that cell.

After keying and splitting, audit alpha, edge contact, empty cells, crop safety, and accidental baked effects. Do not patch a missing head with an unrelated generated head unless identity and neck contact can be proven; regenerate the pose first.
