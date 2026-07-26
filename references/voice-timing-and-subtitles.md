# Voice, timing, and subtitles

## Audition before volume generation

Generate 3–5 auditions from one representative paragraph containing calm narration, action, and emotional punctuation. Compare identity, warmth, intelligibility, energy, sentence endings, and suitability for the audience.

Lock provider, voice/reference ID, model, natural speed, and per-scene prosody after approval. Store parameters and public IDs, never tokens or API keys.

Treat accent as a first-class audition dimension. “Deep”, “authoritative”, or “cinematic” labels do not guarantee standard Mandarin or a period-appropriate voice. Keep a rejection log for dialect, modern commercial delivery, character overlap, and unclear consonants.

## Generate by scene

Generate one file per scene or beat so timing can change without regenerating the entire film. Use the same speaker identity throughout. Adjust temperature or expressive direction by scene when supported, but avoid character drift.

Use 1× playback unless the user explicitly approves another speed. Do not time-stretch approved speech to rescue a picture edit; fit picture to measured voice.

Write a speaker field for every line and mix narrator, character, and atmosphere as inspectable stems. During review, audition the voice-only sequence to catch wrong-speaker reads and overlapping lines before judging the picture.

Write a speaker field for every line and mix narrator, character, and atmosphere as inspectable stems. During review, audition the voice-only sequence to catch wrong-speaker reads and overlapping lines before judging the picture.

## Timeline policy

- Trim only accidental leading/trailing silence, not natural pauses.
- Measure every delivered file with `probe_voice_timing.py`.
- Keep audio as direct children of the top-level HyperFrames root.
- Use J-cuts and continuous action to bridge scene changes.
- Let danger scenes accelerate through writing and performance, not global speed-up.

## Captions

Keep Chinese primary and English secondary when bilingual mode is selected. Use a smaller, lower-contrast English line without reducing readability. End the previous caption before the next becomes readable; avoid stacked crossfades in the same box.

Do not add an English chapter title merely because subtitles are bilingual. Do not display “paper,” “纸片,” progress dots, or slide indices unless they belong to the story or user request.

For Chinese single-language delivery, default to bottom-center alignment with a safe margin. Keep hands, feet, lamp bases, curtain edges, shadow contours, and contact points clear. Check every caption at the widest font size and at the render’s actual aspect ratio; a caption that is centered in CSS but clipped by a foreground layer still fails.

For Chinese single-language delivery, default to bottom-center alignment with a safe margin. Keep hands, feet, lamp bases, curtain edges, shadow contours, and contact points clear. Check every caption at the widest font size and at the render’s actual aspect ratio; a caption that is centered in CSS but clipped by a foreground layer still fails.

## Audio modes

Support `dialogue-only`, `full-mix`, and `stems`. Do not add music or effects when the user asks for dialogue only. Preserve approved voice files unchanged in every delivery mode.
