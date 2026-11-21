# Dub-Fit (Kuku AI Generalist, Problem 3)

**One person:** the localisation/dubbing editor adapting a show into another language.
**One step:** fitting each translated line into the time slot of the original shot.
**One output:** a line-by-line list of what fits, what doesn't, and a shorter version for what doesn't.

A translated line is often longer than the original. If the dub runs past the shot, the voice keeps going after the mouth stops, or TTS gets sped up and sounds robotic. Dub-Fit flags these lines before voice generation.

## Run it

```bash
pip install -r requirements.txt

# Free: how much room does the original timing leave for a longer translation?
python dubfit.py --input "path/to/scripts" --mode source

# Free: check a translator's file (CSV with columns id,text; ids like E001-012 from the script)
python dubfit.py --input "path/to/scripts" --mode check --translations hindi.csv --lang Hindi

# AI: translate, check, and auto-shorten lines that don't fit
export LLM_PROVIDER=gemini LLM_MODEL=gemini-3.8-flash LLM_API_KEY=...
python dubfit.py --input "path/to/scripts" --mode llm --lang Hindi --episodes 1-5

streamlit run app.py
python tests/test_syllables.py   # counter vs hand counts
```

## How it works

1. **Slots from the script** (code): every dialogue line already has start/end times.
2. **Pace limit from the show itself** (code): count syllables per second for every original line. The comfortable max is the pace of the fastest 10% of original lines (5.0 syllables/s for this show). No outside numbers needed.
3. **Translate** (AI, 30 lines per call, with speaker and emotion so the tone stays right).
4. **Check** (code): syllables in the translation divided by the slot. Over the max means it won't fit.
5. **Shorten** (AI, max 2 tries) with an exact syllable budget. **Code re-checks** and decides fits / fixed / still too long. The model never marks its own work.
6. **Human step:** the editor reviews only the `fixed` and `too_long` lines, not all 1,487.

Syllables: vowel groups for Latin script; aksharas for Indic scripts (Hindi, Bengali, Odia...) with silent final "a" dropped for Hindi-like scripts. Exact on 5 of 7 hand-counted lines, off by 1-2 on the others (Hinglish, inner silent "a").

## Confidentiality
Do not commit the scripts. The app takes uploads.
