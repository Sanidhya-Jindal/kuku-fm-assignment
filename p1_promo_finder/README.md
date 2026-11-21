# Promo Finder (Kuku AI Generalist, Problem 1)

Reads microdrama screenplays and finds 20-60s promo cuts. Each promo comes with segment timestamps, the hook, the cliffhanger, one line on why it works, and a "post first" rank.

## Run it

```bash
pip install -r requirements.txt

# 1) Free rules mode (no key, under 1 second for 50 episodes)
python run.py --input "path/to/scripts_folder" --mode rules

# 2) LLM mode (any provider, swap with env vars)
export LLM_PROVIDER=gemini            # or anthropic, or openai (= any OpenAI-style server: Groq, OpenRouter, Ollama)
export LLM_MODEL=gemini-3.8-flash     # copy the exact model ID from your provider console
export LLM_API_KEY=your_key           # free key from aistudio.google.com
# export LLM_BASE_URL=https://api.groq.com/openai/v1   (only for openai-style servers)
python run.py --input "path/to/scripts_folder" --mode llm   # add --chunk 1 if the free tier says the request is too large

# 3) Web app
streamlit run app.py
```

Outputs go to `outputs/<mode>/`: `promos.json` (everything), `promos.csv` (one row per promo), `report.md` (top 10), and `qa.json` (automatic checks).

## How it works

1. **parse.py** (plain code): turns each script into timed blocks (dialogue, action, camera, sound) with IDs like `E012-034`.
2. **Find promos**
   - **rules.py**: tries every start/end pair at shot boundaries that does not cut through a line. It scores the first 3s (hot emotions like *Furious* or *Mocking*, action words like slap or grab), the last 6s (episode ending, unanswered question, threat, cliffhanger sound cue), and whether a new viewer can follow (few speakers, not a reply to an unheard line). It also tries a 2-part "cold open": the strongest hook moment glued before the run-up to the ending.
   - **llm_mode.py**: the model reads 3 episodes at a time and answers with **line IDs, not timestamps**. Code turns IDs into times and rejects unknown IDs, reversed ranges, segments that span two episodes, and promos outside 20-60s. Rejections are logged in `promos.json`. Rules mode then re-checks every pick as a second opinion and flags disagreements. A final call ranks what to post first.
3. **eval.py**: a human review sheet (Y/P/N grades for the top 10) and agreement between modes.

```bash
python eval.py sheet outputs/rules             # make review_sheet.csv
python eval.py score outputs/rules/review_sheet.csv
python eval.py compare outputs/rules outputs/llm
```

## Confidentiality

The input pack is Kuku's content. **Do not commit the scripts.** `.gitignore` blocks `*.txt` script folders. The app takes uploads instead of bundling data.
