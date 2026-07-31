# Fish Audio S2.1 Pro production direction

Use this reference whenever a paper-animation project selects Fish Audio
`s2.1-pro` or `s2.1-pro-free`.

## Contents

- [Capability contract](#capability-contract)
- [Context analysis before cues](#context-analysis-before-cues)
- [Cue writing and placement](#cue-writing-and-placement)
- [Combining cues](#combining-cues)
- [Pause policy](#pause-policy)
- [Contextual speed policy](#contextual-speed-policy)
- [Casting and audition matrix](#casting-and-audition-matrix)
- [Synthesis and variant selection](#synthesis-and-variant-selection)
- [API production baseline](#api-production-baseline)
- [Acceptance gates](#acceptance-gates)
- [Storytelling examples](#storytelling-examples)
- [Official sources](#official-sources)

## Capability contract

- Use square brackets for S2.1 Pro inline cues. Do not use S1 parentheses in
  direct API text.
- Treat bracket content as natural-language performance direction, not as a
  fixed emotion-token vocabulary.
- Allow concise cues in the script language, including Chinese.
- Place a cue immediately before the word, phrase, clause, or sentence where
  its effect should begin.
- Assume a cue influences following speech until another cue or the sentence
  boundary changes the direction; verify the audible scope in the actual take.
- Use familiar cues such as `[pause]`, `[long pause]`, `[sigh]`,
  `[whispering]`, or `[emphasis]` as stable starting points, not as a whitelist.
- Treat the model as generative. A cue expresses intent; it does not guarantee
  an exact acoustic value or duration.

Use `s2.1-pro-free` for broad auditioning when service guarantees are not
needed. Use `s2.1-pro` for production workloads that require Fish Audio's
production TTFA/DPA posture. Official documentation states that both have the
same model quality and language coverage.

## Context analysis before cues

Before writing annotated text, determine for every line:

- speaker and addressee;
- what the speaker knows at this moment;
- what changed since the previous line;
- narrative function: establish, reveal, interrupt, escalate, react, decide,
  reflect, or close;
- subtext and attitude toward the character;
- one primary emotional direction and its intensity;
- information density and focus words;
- expected pace at entry, middle, and exit;
- the physical state: resting, working, running, injured, whispering, holding
  back tears, or recovering breath;
- the reason for any pause;
- forbidden delivery such as ridicule, sales cadence, newsreader cadence,
  melodrama, dialect drift, or moralizing.

Store this analysis separately from the TTS text. Compress only the audible
instruction into the bracket cue.

## Cue writing and placement

Write cues as short actor directions:

```text
[意外而克制的惊喜]
[强装平静，其实仍有些不安]
[温和反思，不带嘲讽]
[短暂停顿，然后轻声继续]
```

Avoid both extremes:

```text
[平静]
```

when it loses essential subtext, and:

```text
[Explain the full plot, camera movement, moral argument, and every imagined
internal thought in a paragraph-long instruction]
```

when non-acoustic detail competes with the line.

For sentence-level direction, place the cue at the sentence start. For a local
shift, put it immediately before the affected phrase:

```text
他把一次[强调]偶然，当成了每天都会重来的规律。
```

Do not place every cue at the start by habit.

## Combining cues

Consecutive cues are supported. Combine them when each has a distinct job:

```text
[叹气][失落但克制]他又等了一天。
[短暂停顿][轻微错愕]兔子竟撞在了树桩上。
[低声说][仍有些不安]这真的是好运吗？
```

Prefer combinations such as:

```text
physical reaction + primary emotion
pause + changed mental state
voice style + primary emotion
local emphasis + following phrase
```

Begin with one primary direction. Add a second or third control only when an
audition proves that the simpler version is insufficient. As a production
default, keep one location to no more than two or three useful controls.
Do not stack synonyms, contradictory emotions, or decorative tags.

## Pause policy

Use punctuation first. Add `[short pause]`, `[pause]`, or `[long pause]` when
the performance needs an audible beat. `[break]` and `[long-break]` also
appear in Fish Audio documentation, but do not mix vocabularies without a
reason.

Do not assume:

```text
[pause][pause][pause]
```

has a stable, additive, or linearly measurable duration. It may be auditioned
as an experimental variant, but it cannot be the release timing contract.

When the story needs expressive silence but not an exact length, audition:

```text
[long pause]
[停得更久一些，再轻声继续]
[long pause, then quietly]
```

When the picture, subtitle, impact, or music cue requires an exact pause:

1. end the first synthesis segment at the pause;
2. generate the following segment separately;
3. insert the specified silence on the audio timeline;
4. store its measured duration in the voice ledger;
5. review the joined result for breath, room tone, and emotional continuity.

## Contextual speed policy

Never use one numeric speed for the whole film or automatically set every line
to `1`. Establish a voice-specific baseline during casting, then select a
request-level speed for each line or semantic beat.

Analyze these factors:

- urgency and physical action;
- information density and pronunciation difficulty;
- emotional arousal versus restraint;
- whether the line discovers, reacts, explains, decides, or reflects;
- the pace established by adjacent lines;
- focus words and intended silence;
- the selected voice's natural cadence and response to speed control.

Typical directing tendencies are contextual, not fixed mappings:

- keep clear exposition near the approved voice baseline;
- allow action escalation or interruption to move faster when intelligibility
  remains intact;
- let surprise change pace at the moment of discovery rather than speeding
  the whole sentence;
- let hesitation, loss, consequence, or reflection slow locally without
  turning the whole role solemn;
- slow dense or unfamiliar information enough to remain clear;
- avoid solving a duration problem by globally accelerating every line.

Use request-level `prosody.speed` for the current segment's baseline. Use an
inline cue for a local pace change. Split the request when the intended change
is material:

```text
segment A: ordinary work rhythm
segment B: sudden interruption
segment C: slower realization
```

For each important beat, audition at least:

```text
A: voice baseline, no cue
B: contextual speed, one concise cue
C: contextual speed, one justified local or combined cue
```

Do not force numerical variation when the baseline is already correct. The
rule is contextual selection, not mandatory difference.

## Casting and audition matrix

Search the public Fish Audio model market broadly. Preserve each public model
ID, title, market URL, author/provenance metadata, and audition file. Reject
unlicensed private clones, celebrity imitation, unclear provenance, dialect
drift, advertising cadence, and character overlap.

Test every shortlisted voice with the same matrix:

1. neutral narration without cues;
2. one context-derived emotional direction;
3. a sentence-internal shift;
4. local emphasis;
5. short and long pause behavior;
6. a restrained ending;
7. baseline, slightly quicker, and slightly slower segment-level delivery;
8. difficult names, polyphonic characters, numbers, and sentence endings.

Score voice identity and direction-following separately. If a cue repeatedly
fails, compare another voice before making the instruction longer.

## Synthesis and variant selection

Generate by scene or semantic beat. Split a line when it contains a major
speed, emotional, or pause transition. Keep enough surrounding context to
preserve natural entry and sentence endings.

Preserve for every take:

- stable line and variant ID;
- speaker and voice/reference ID;
- raw and annotated text;
- context analysis and forbidden delivery;
- model and public market URL;
- request-level speed and rationale;
- inline cues and placement;
- pause strategy;
- temperature, top-p, normalization, latency, chunking, and repetition
  settings;
- output path, measured duration, loudness, and timestamp alignment;
- approval or rejection reason.

Do not select from filenames alone. Listen in three contexts:

1. isolated line;
2. voice-only sequence with adjacent lines;
3. picture, subtitle, effects, and music.

## API production baseline

Start evaluation from documented API defaults rather than copying a previous
project's tuned values:

```json
{
  "model_header": "s2.1-pro-free",
  "temperature": 0.7,
  "top_p": 0.7,
  "prosody": {
    "speed": "voice-and-context-specific",
    "volume": 0,
    "normalize_loudness": true
  },
  "chunk_length": 300,
  "normalize": true,
  "format": "wav",
  "sample_rate": 44100,
  "latency": "normal",
  "repetition_penalty": 1.2,
  "condition_on_previous_chunks": true
}
```

The string value above documents policy; replace it with the selected numeric
speed before sending a real request.

Use WAV or PCM for approved dry stems and MP3 only when audition convenience
outweighs edit quality. Prefer `latency: normal` for offline final production.
Change one sampling variable at a time so the cause of a result remains
auditable.

## Acceptance gates

Reject a take when:

- a cue is spoken as text or produces an artifact;
- the intended emotion, pace, emphasis, or pause is absent;
- the voice changes identity, age, accent, or distance unexpectedly;
- adjacent lines jump in speed without a story reason;
- the delivery becomes advertising, newsreader, theatrical, sarcastic, or
  moralizing against the directing contract;
- words, names, or sentence endings become unclear;
- an exact pause is delegated to the model instead of the timeline;
- the selected result has no recorded text, parameters, duration, or reason.

Approve only after the voice-only and combined reviews pass.

## Storytelling examples

Examples illustrate reasoning; never copy them as a preset library.

```text
[温暖而朴素的故事讲述]宋国有一个农夫，每天都在田里耕作。
```

```text
一天，他正在田里干活。忽然，一只兔子飞奔而来，
[短暂停顿][轻微错愕]一头撞在了树桩上。
```

```text
[起初不敢相信，随后浮出朴素的惊喜]
他没费一点力气，便捡到了一只兔子。
```

```text
[仍抱着期待]他等了一天。[long pause][期待渐渐落空]
又等了一天。
```

For an exact two-beat silence, synthesize the two clauses separately and join
them with measured silence instead of repeating pause cues.

```text
[温和反思，不带嘲讽]
他把一次[强调]偶然，当成了不会改变的规律。
```

## Official sources

- Models and S2.1 Pro natural-language control:
  <https://docs.fish.audio/developer-guide/models-pricing/models-overview>
- S2 emotion placement, combinations, and best practices:
  <https://docs.fish.audio/developer-guide/core-features/emotions>
- S2 inline tags, scope, pauses, voice dependence, and layering:
  <https://fish.audio/blog/fish-audio-s2-fine-grained-ai-voice-control-at-the-word-level/>
- TTS endpoint and request parameters:
  <https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech>
- Timestamped TTS:
  <https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech-stream-with-timestamps>
