# Motion integrity contract

Use this reference for every shot containing subject travel, locomotion, orientation change, mirroring, or contact. The contract makes asset facts, instance transforms, world travel, and rendered evidence one auditable chain.

## Contents

1. Single source of truth
2. Asset facts
3. Motion contract
4. Derived invariants
5. Mirroring
6. Proof and release
7. Commands

## 1. Single source of truth

Do not infer direction from a filename. Do not repeat independent left/right strings in the spatial plan, asset inventory, motion code, and release record without derivation.

Use:

```text
asset-facts.json
  + motion-contract.json
  → compiled-motion-track.json
  → implementation
  → rendered-motion-review.json
```

- `asset-facts.json` records observed properties of the exact hashed media.
- `motion-contract.json` records shot intent, instance transform, travel, timing, support, and proof times.
- `compiled-motion-track.json` contains derived values for the implementation; do not hand-copy them.
- `rendered-motion-review.json` binds review evidence to the final MP4 hash.

## 2. Asset facts

Start from `assets/project-template/manifests/asset-facts.example.json`.

Record:

- stable asset and identity IDs;
- local media path and SHA-256;
- kind, camera side, intrinsic facing, forward axis, head/chest/gaze observations;
- support/contact anchors and canvas baseline;
- light direction, handedness, text, held objects, costume/hair asymmetry;
- mirror policy and completed mirror-safety audit;
- orientation evidence path and review status.

The orientation review must inspect the visible artifact. A prompt, filename, previous version, or manifest label is not evidence. Replacing the file invalidates approval because its hash changes.

Use `front` only for genuinely frontal or non-directional material. A travelling actor normally requires `left` or `right`.

## 3. Motion contract

Start from `assets/project-template/manifests/motion-contract.example.json`.

For each moving actor, record:

- asset-facts path;
- implementation engine, selector, and source file;
- active time window;
- normalized start and end positions;
- locomotion semantic: `forward-travel`, `backward-travel`, or `stationary`;
- instance `scale_x`, rotation, and explicit mirror state;
- support surface and baseline/airborne policy;
- contact target and time when applicable;
- proof times covering the motion, contact, settle, and exit.

The contract owns these values. Generate the implementation track with the compiler rather than retyping x/y deltas and facing.

## 4. Derived invariants

For horizontal screen travel:

```text
travel_vector = end - start
rendered_forward = intrinsic_forward × sign(scale_x)
alignment = dot(normalize(travel_vector), normalize(rendered_forward))
```

Require:

- `forward-travel`: positive alignment;
- `backward-travel`: negative alignment plus a visible story reason;
- `stationary`: negligible travel distance;
- start/end and proof times inside frame and shot duration;
- asset hash and evidence current;
- selector unique and source present;
- mirror state consistent with `scale_x` and asset policy;
- contact time inside the active interval and near the intended end state;
- support declared for weight-bearing motion.

The contract currently treats left/right screen direction as the core hard invariant. Use engine-specific manifests for depth-axis travel, but preserve the same principle with a declared forward vector and world path.

## 5. Mirroring

Default to `forbidden`. Permit `allowed-after-audit` only when all relevant fields pass:

- costume/hair/body asymmetry;
- scars, insignia, text, and symbols;
- handedness and held-object ownership;
- light and cast-shadow direction;
- contact geometry and load direction;
- previous/next shot continuity.

Set both `instance_transform.scale_x: -1` and `mirror.applied: true`. Silent CSS or timeline mirroring is a release failure.

## 6. Proof and release

Generate review evidence from the rendered MP4 at:

- motion entry;
- early travel;
- midpoint;
- late travel;
- contact or extreme;
- settle;
- exit/final state.

Use `scripts/build_motion_review.py` to extract evidence and create a contact sheet. It initializes review statuses as `pending`. Inspect the rendered frames, then record observed facing, support, contact, and result. Do not approve from source art alone.

Run `scripts/audit_rendered_motion.py` to verify that:

- the reviewed MP4 and evidence hashes still match;
- the review shot and actor set match the bound motion contract;
- the review's expected rendered facing and travel direction are derived from, and cannot contradict, the bound contract;
- all required proof times have frames;
- every actor review passes direction, support, contact when required, identity, and result;
- review notes are non-empty;
- no stale or pending evidence can satisfy release.

## 7. Commands

Validate asset facts and the planned motion:

```bash
python3 scripts/audit_motion_contract.py \
  shots/scene-xx/motion-contract.json \
  --project . \
  --phase planning \
  --strict
```

Compile the implementation track:

```bash
python3 scripts/compile_motion_contract.py \
  shots/scene-xx/motion-contract.json \
  --project . \
  --output shots/scene-xx/compiled-motion-track.json
```

After rendering:

```bash
python3 scripts/build_motion_review.py \
  --contract shots/scene-xx/motion-contract.json \
  --project . \
  --video renders/scene-xx.mp4 \
  --output shots/scene-xx/rendered-motion-review.json
```

After recording observed review results:

```bash
python3 scripts/audit_rendered_motion.py \
  shots/scene-xx/rendered-motion-review.json \
  --project . \
  --strict
```

After all shot reviews are recorded, bind the schema-v4 release record to the exact upstream records, rendered MP4, and proof frames. Re-run this whenever any bound file changes:

```bash
python3 scripts/bind_release_evidence.py shots/scene-xx/shot-release.json
```
