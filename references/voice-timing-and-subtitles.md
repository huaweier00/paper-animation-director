# Voice, timing, and subtitles

## Audition before volume generation

For Douyin or another feed-native social project, approve the 0–3 second hook animatic and complete scratch animatic before formal market search, final casting, or full-quality synthesis. Use disposable scratch voice for editorial testing. This keeps an expensive or emotionally strong performance from locking a weak opening, redundant script, or overlong structure.

Generate 3–5 auditions from one representative paragraph containing calm narration, action, and emotional punctuation. Compare identity, warmth, intelligibility, energy, sentence endings, and suitability for the audience.

Lock provider, voice/reference ID, model, a voice-specific audition baseline, and the policy for contextual per-line or per-beat prosody after approval. A baseline is a comparison anchor, not one speed copied across the film. Store parameters and public IDs, never tokens or API keys.

Treat accent as a first-class audition dimension. “Deep”, “authoritative”, or “cinematic” labels do not guarantee standard Mandarin or a period-appropriate voice. Keep a rejection log for dialect, modern commercial delivery, character overlap, and unclear consonants.

When the user requests Fish Audio, search the public model marketplace rather than accepting the first plausible voice. Keep a broad metadata pool, shortlist several candidates per role, and synthesize the same test line for each candidate. Preserve:

- model name, public model ID, and marketplace URL;
- raw test text, annotated test text, contextual speed, and the reason for each direction;
- audition file and measured duration;
- diction, accent, emotional range, pause, emphasis, and speed-response notes;
- technical notes such as speaking rate, loudness, and true peak;
- selection reason and rejected alternatives.

Exclude unlicensed private clones, celebrity imitation, obvious anime/game caricature, dialect drift, exaggerated advertising cadence, or models whose public provenance cannot be recorded.

When using Fish Audio S2.1 Pro, read `fish-audio-s2.1-pro-production.md`.
Do not copy the fixed English cue stacks or sampling values from an older
project. Test each candidate with an untagged baseline, one concise contextual
direction, and one justified combined-cue version.

## Generate by scene

Generate one file per scene or beat so timing can change without regenerating the entire film. Use the same speaker identity throughout. Adjust temperature or expressive direction by scene when supported, but avoid character drift.

Do not prefill every request with `speed: 1`, and do not vary speed merely to
create artificial diversity. Determine speed from the current semantic beat,
the previous and following lines, information density, physical condition,
emotional transition, focus words, and the scene's dramatic function. It is
valid for a line to retain the audition baseline when that is the best
delivery.

Use this control order:

1. write speakable text and punctuation;
2. choose the line or beat's request-level speed relative to the approved
   voice baseline;
3. use concise inline direction for a local change in pace or delivery;
4. split the request when one line contains a material speed or emotional
   transition;
5. insert measured silence in post when an exact pause duration is required.

Do not time-stretch an approved performance to rescue a picture edit; fit
picture to measured voice. If a platform target requires a shorter film,
rewrite or recut before globally accelerating speech.

Write a speaker field for every line and mix narrator, character, and atmosphere as inspectable stems. During review, audition the voice-only sequence to catch wrong-speaker reads and overlapping lines before judging the picture.

Maintain a voice ledger with stable line ID, speaker, exact text, source path, start, measured duration, gain, required/optional status, and revision. Keep original dry files even after they enter a mix.

For synthesized speech, also preserve raw text, annotated text, direction
rationale, voice baseline, selected request-level speed, inline cues, pause
strategy, model, sampling parameters, candidate take, and rejection reason.

## Timeline policy

- Trim only accidental leading/trailing silence, not natural pauses.
- Measure every delivered file with `probe_voice_timing.py`.
- Keep audio as direct children of the top-level HyperFrames root.
- Use J-cuts and continuous action to bridge scene changes.
- Let danger scenes accelerate through writing and performance, not global speed-up.
- Let reflection, surprise, hesitation, and consequence alter pace where they occur; do not slow an entire role because one scene is contemplative.
- Use the selected voice take's measured duration, not the requested speed value, as the timing authority.
- Keep a voice-only reference mix aligned to the final timeline.
- Keep music/atmosphere separate from narration and dialogue until the final mix.
- Before every final encode, compare the expected-line ledger with the rendered timeline and confirm every required line is audible.
- Preserve the approved editorial promise when fitting picture to final measured voice. If the final performance pushes the first proof too late, rewrite, split, or recut; do not silently weaken the hook contract.
- For social projects, review the opening with sound on and muted. The first spoken line must add question, cost, choice, character thought, or hidden causality rather than narrate a visible establishing image.

## Captions

Keep Chinese primary and English secondary when bilingual mode is selected. Use a smaller, lower-contrast English line without reducing readability. End the previous caption before the next becomes readable; avoid stacked crossfades in the same box.

Do not add an English chapter title merely because subtitles are bilingual. Do not display “paper,” “纸片,” progress dots, or slide indices unless they belong to the story or user request.

For Chinese single-language delivery, default to bottom-center alignment with a safe margin. Keep hands, feet, lamp bases, curtain edges, shadow contours, and contact points clear. Check every caption at the widest font size and at the render’s actual aspect ratio; a caption that is centered in CSS but clipped by a foreground layer still fails.

For feed-native delivery, also inspect captions in a real-size vertical-feed simulation with right-side controls and bottom metadata exclusion zones. Test the ending save object independently from normal subtitles; when the viewer must read several lines, pause narration, reduce the text, split the card, or lengthen the approved hold rather than shrinking type.

## Audio modes

Support `dialogue-only`, `full-mix`, and `stems`. Do not add music or effects when the user asks for dialogue only. Preserve approved voice files unchanged in every delivery mode.

## Missing-narration recovery

If a supplied video keeps the original picture duration and music but loses narration:

1. compare duration, scene boundaries, and subtitle timing with the approved timeline;
2. use the saved voice ledger and dry stems, not newly generated replacement performances;
3. place each line at its locked start and natural duration;
4. duck music under speech without changing the picture duration;
5. render a new file and preserve the supplied source;
6. perform voice-only, full-mix, subtitle-sync, loudness, full-decode, and expected-line checks.

Do not infer that “an audio stream exists” means narration exists. A music-only AAC stream can pass FFprobe. Verify required speech content against the ledger or voice-only reference mix.
