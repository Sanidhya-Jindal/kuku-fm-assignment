# Problem 3: Dub-Fit: will each dubbed line fit its shot?

<div class="meta">Sanidhya Jindal · Roll 123MM0666 · Metallurgical & Materials Engineering, NIT Rourkela<br>
Prototype: [link] · Raw outputs: [link] · Walkthrough: [link]</div>

## The problem, and why it's real

**Who:** the localisation/dubbing editor adapting a show into another language. **The step:** fitting each translated line into the time slot of the original shot. When a translation runs longer than the slot, the voice keeps talking after the mouth stops, or the TTS gets sped up and sounds robotic.

- **Kuku works in many languages, at volume.** Kuku TV offers shows in Hindi, Tamil, Telugu, Malayalam, English, Kannada and Bangla, has launched in the US, and makes hundreds of shows a month with a target of 1,000+.
- **Translators hit this all the time.** An engineering write-up on short-drama localisation says almost every team runs into dubbed audio overrunning the picture, because translated text expands by 30–75% (Chinese to English or Spanish).
- **Viewers notice.** A study of 1–3★ reviews of the top short-drama apps lists "stilted machine dubbing" among the repeated complaints.
- **The input pack shows how little room there is.** The median dialogue slot is only 2.2 s. **34% of lines have less than 30% room**, so a translation that is 30% longer would not fit in about a third of the lines.

**Why this over Problems 1 and 2:** a promo is about 10 decisions per show. Dub fit is 1,487 lines **times every language**, and each bad line is heard by every viewer of that version. Today the only way to catch these is to listen to every line. Problem 2 is outside Kuku's core business.

## Assumptions

- Dubbed voices are AI TTS dropped into the original slots, and the video is not re-timed.
- Syllables per second is a fair stand-in for speaking time across languages.
- The comfortable maximum pace is the pace of the **fastest 10% of lines in the original show** (5.0 syllables/s here), so no outside numbers are needed.
- Exact lip-sync and mouth shapes are out of scope. Only start and end timing is checked.

## How it works

| Step | Who | What |
|---|--|------------|
| 1. Slots | Code | Each dialogue line's start and end come from the script. |
| 2. Pace limit | Code | Counts syllables per second for all original lines and sets max = 90th percentile. |
| 3. Translate | LLM | 30 lines per call, with speaker and emotion so the tone carries over. |
| 4. Check | Code | Syllables in the translation ÷ slot. Over the max = won't fit. |
| 5. Shorten | LLM | Over-long lines get an exact syllable budget, 30 per call, up to 2 rounds. |
| 6. Re-check | Code | Code (not the model) marks each line fits / fixed / still too long. |
| 7. Review | Human | The editor reviews only the *fixed* and *too long* lines, not all 1,487. |

**Syllable counter:** counts vowel groups for Latin script, and aksharas (consonant or vowel sounds) for Indic scripts, dropping the silent final "a" in Hindi-style scripts. It was exact on 5 of 7 hand-counted lines (Hindi, Odia, Bengali, English) and off by 1–2 on a Hinglish line and on one Hindi word with a silent "a" in the middle.
There is also a free "check my translator's file" mode (CSV with `id,text`), so the tool helps even without AI.

## Results

- **Free run on all 50 episodes:** 1,487 lines. Normal pace is 3.26 syllables/s and the max is 5.0. The median line has 54% room to grow, while 18% of lines have under 10% room and 34% have under 30%.
- **AI run (Hindi, episodes 1–5):** [fill in from `outputs/llm_hindi/summary.json`: % over the slot before the fix → % after, number of lines still too long].

## How I'd know it worked with a real team

1. **Saves time:** editor minutes spent fixing dubs per episode, before and after.
2. **Fewer redos:** the share of lines re-generated after the first TTS pass.
3. **Flags are right:** on 5 episodes, the share of flagged lines the editor agrees with, and the lines the editor had to fix that the tool missed.
4. **Shortening doesn't break meaning:** a bilingual reviewer rates a sample of the shortened lines (target 90% or more keep their meaning).
5. **Viewers:** the completion rate of dubbed episodes compared with the original language, and fewer dubbing complaints in reviews.

## Where it fails

- Syllables are not exactly seconds, because syllable length differs by language and by delivery (shouted lines are faster).
- It doesn't flag lines that are **too short** and leave silence.
- **The code checks length, not meaning.** A shortened line can lose a key detail, which is why the human review stays.
- Using the English pace as the limit may not match natural Hindi pacing. This needs tuning with real dubs.

## Scale and cost

About 85 model calls per show per language: 50 to translate and about 35 to shorten. That is roughly 130k input and 110k output tokens, or **about $0.5 per show per language** at Gemini 3.8 Flash paid prices (up to 31 Dec 2026). The checks are free code. The model is swapped with environment variables, so a stronger model can be plugged in.

## AI tools used

Claude (Anthropic): planning, code, research. [Add any other tool you used.]
**Where it got it wrong:** its first syllable counter used Python's `\w` to split words, which breaks Hindi words apart at vowel signs, so counts were wrong. Hand-counting 7 lines caught it. Its first summary also reported "10% of lines are already too fast", which is circular because the limit was defined as the fastest 10%. I replaced it with the "room to grow" numbers above.

<p class="src">Sources: Kuku TV App Store listing; CXOToday (Feb 2026, Kuku AI microdrama slate); MediaNews4U (May 2025, US launch); Aliyun developer article on short-drama dubbing timing; Unstar review analysis of ReelShort, DramaBox and others (2026); Gemini API pricing page.</p>
