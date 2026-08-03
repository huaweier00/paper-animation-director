# Shadow-theatre route

Use this route only when the film claims Chinese shadow-puppet, 皮影, rear-lit screen, translucent carved skin/paper, rod/joint manipulation, or a deliberate digital translation of those systems.

## Contents

1. Medium truth
2. Performer construction
3. Screen, light, and depth
4. Performance language
5. Sound and ensemble
6. Asset and engine rules
7. Benchmark and release gates

## 1. Medium truth

Treat shadow theatre as a complete theatre system, not a texture preset:

```text
carved or cut leather/paper performer
× articulated control
× illuminated screen
× stylized action phrases
× singing/music/percussion
× coordinated staging
```

Declare one regional or newly authored visual grammar. Record the role of silhouette, profile/five-sevenths face, line, openwork, color transmission or opacity, costume pattern, and role coding. Leather and paper, translucent colour and opaque silhouette are route variants; the declared material behavior must remain consistent. Do not combine unrelated regional traits under a generic “ancient Chinese” label.

Reject:

- opaque painterly full-body PNGs described as shadow puppets;
- a paper-fiber overlay used as proof of leather, screen, or transmitted light;
- drop shadows used as the only shadow-theatre optical behavior;
- unrestricted 3D staging that contradicts the declared screen-plane language;
- realistic neutral figures whose silhouette cannot carry role or action.

## 2. Performer construction

Create `puppet-model.json` for every recurring hero. Record:

- body parts and overlap beneath joints;
- joints, pivots, ranges, draw order, interchangeable parts, and attachment points;
- central/root control, hand controls, and optional weapon/mount/prop controls;
- authored screen-facing side and turn/substitution policy;
- support behavior, balance, and contact points;
- signature action phrases and forbidden deformations;
- translucent material regions, openwork, opaque accents, and maximum display scale.

The digital performer need not copy one historical joint count, but every declared joint must serve a visible action. UNESCO's Chinese shadow-puppetry description notes that many traditional figures have roughly twelve to twenty-four movable joints; treat that as evidence of performance capacity, not a numeric target. Do not add bones merely to increase sophistication. A connected replacement state is preferable when a rig exposes seams or cannot preserve contact.

## 3. Screen, light, and depth

Declare the light-screen geometry:

- light source position, size, softness, color, and flicker policy;
- screen plane, safe performance window, entry/exit channels, and occlusion rules;
- performer-to-screen distance and its effect on scale, edge softness, transmission, and focus;
- background/scenery relationship to the screen;
- whether rods are invisible, faintly visible, or intentionally shown.

Use screen distance as an authored dramatic control, not random scale pulsing. A close-to-screen pose can be crisp and authoritative; a controlled retreat may enlarge and soften the image. Preserve character identity and continuity through the change.

## 4. Performance language

Build action from economical, readable phrases:

```text
prepare → enter → strike/gesture/contact → exact hold → recover/react → exit or new pose
```

Use the central/root control to establish balance and travel. Let hand, sleeve, weapon, head, mount, or prop controls lead specific actions. Avoid moving all parts equally.

Prefer graphic rhythm over generic interpolation:

- swift entries and exits;
- clear stopped poses;
- asymmetrical preparation;
- decisive gesture/contact frames;
- controlled substitutions for turns, transformations, wounds, costume, scale, or state;
- reaction chains from the affected performer or environment.

Whole-performer translation may carry the root through screen space only while articulated support, gesture, rhythm, and route-specific staging make the action read. It cannot substitute for walking, fighting, threatening, comforting, carrying, or emotional change.

## 5. Sound and ensemble

Shadow-theatre production requires an audio posture that includes performance sound. Create measured cues for:

- spoken/sung lines;
- character or role motifs;
- percussion accents for entry, contact, substitution, hold, and exit;
- continuous musical pulse where appropriate;
- intentional silence and the action it frames.

Coordinate multiple performers as one composite movement. Record ownership of shared props, mounts, weapons, and procession elements. A crowd PNG sliding as one plate is not simultaneous puppet manipulation.

## 6. Asset and engine rules

Choose one of these performer architectures per shot:

- articulated 2D rig with route-authored joints and controls;
- stepped complete-pose replacement;
- connected performer/prop or performer/mount ensemble states;
- full-screen state replacement for fragile battle, procession, or transformation contact;
- deliberate still display with earned-stillness evidence.

Rive, DOM/SVG, canvas, or another seek-safe engine may drive the performer. Engine prestige is irrelevant. The release must prove joint/state behavior, silhouette, light-screen response, action timing, and sound synchronization.

## 7. Benchmark and release gates

The shadow benchmark must prove all of these from the rendered MP4:

1. one performer changes intention through articulated or authored state motion;
2. one interaction produces a readable reaction;
3. one exact hold lands with a sound cue;
4. declared openwork, colour-transmission or opaque-silhouette behavior and screen-edge behavior are visible;
5. entry, exit, or substitution preserves screen continuity;
6. the scene remains readable muted and gains identity/weight with audio;
7. a static camera still reveals the performance.

Reject release when:

- hero action is only root translation, rotation, scale, opacity, or camera movement;
- the same fixed pose carries incompatible intentions;
- no puppet model or performance contract exists;
- the screen/light/material claim is absent from the render;
- the audio is silent or music-only;
- title, prompt, filename, or CSS class is the only evidence that an asset is a puppet.

## Evidence anchor

The route definition is grounded in [UNESCO's Chinese shadow puppetry record](https://ich.unesco.org/en/RL/chinese-shadow-puppetry-00421): leather or paper figures, rod manipulation, a translucent back-lit cloth screen, music and singing, simultaneous manipulation, and—in many carved figures—multiple movable joints. The digital workflow translates those interacting systems; it does not treat any one decorative surface as sufficient proof.
