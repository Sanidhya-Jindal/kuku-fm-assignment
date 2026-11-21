# Kuku FM: AI Generalist Assignment

**Sanidhya Jindal** · 123MM0666 · Metallurgical & Materials Engineering, NIT Rourkela

Three small, working AI tools for the three problems in Kuku's AI Generalist brief. Each one runs for free without an API key, and each has an AI mode where the model can be swapped with one setting.

| | Problem | Live app | What it does |
|---|---|---|---|
| 1 | **Find the Promos** | [kuku-promo-finder-xyz.streamlit.app](https://kuku-promo-finder-xyz.streamlit.app/) | Reads a microdrama's screenplays and returns ranked 20–60 second promo cuts, each with a hook, a cliffhanger and exact timestamps. |
| 2 | **AI Lawyer (Nyaya AI)** | [github.com/Sanidhya-Jindal/nyaya-ai-](https://github.com/Sanidhya-Jindal/nyaya-ai-) | A legal research assistant for Indian law. It answers in plain language (citizen mode) or runs a team of research agents that draft and critique their own answer (lawyer mode), using only sources it actually finds. |
| 3 | **Dub-Fit** (own problem) | [kuku-dubfit.streamlit.app](https://kuku-dubfit.streamlit.app/) | Checks whether each translated line fits the time slot of its shot, and shortens the ones that don't before any voice is recorded. |

---

## 1. Promo Finder

![Promo Finder](docs/screenshots/promo_finder.png)

**The problem:** an editor watches every episode to pick promos by hand, and Kuku releases new shows every week.

**How it works**
1. **Read** (code): each script becomes timed lines of dialogue, action, camera and sound.
2. **Find**:
   - *Free mode* scores every legal start and end point on three things: the first 3 seconds (the hook), the final moment (the cliffhanger), and whether a new viewer can follow.
   - *AI mode* reads 3 episodes at a time and proposes promos.
3. **Check** (code): the AI answers with **line IDs, never timestamps**. Code converts them to times and rejects unknown IDs, reversed ranges and anything outside 20–60 s, so the model can't invent a cut. The rules then re-score every AI pick and flag disagreements.
4. **Rank**: strongest first, leaning toward early episodes so new viewers aren't spoiled.

**Results on the 50-episode input pack (free mode):**
- 100 promos found in under a second, all between 21 and 60 s, covering every episode.
- In a hand review of the top 10, 3 were ready to post, 3 were maybe, and 4 were no.
- Main known failure: it treats every episode ending as a cliffhanger, even happy ones.

[Folder and run steps](p1_promo_finder)

## 2. Nyaya AI: AI lawyer

**Code:** [github.com/Sanidhya-Jindal/nyaya-ai-](https://github.com/Sanidhya-Jindal/nyaya-ai-) · **Test cases and raw outputs:** [`p2_nyaya_ai`](p2_nyaya_ai)

**The problem:** most people never get help with everyday legal problems, and AI chatbots tend to invent laws and cases with confidence.

**How it works**
- **Intent gate:** greetings skip the research pipeline, and questions about non-Indian law are declined politely.
- **Citizen mode** rewrites the question using the conversation so far, searches, and answers in plain language.
- **Lawyer mode** runs a loop of agents: issue extractor, planner, retriever, drafter and critic. It revises the draft until the critic scores it 0.7 or higher, or 3 rounds pass.
- **Hybrid retrieval** runs FAISS search over 4,209 chunks from 39 Indian legal documents alongside a live Tavily web search. Social-media sources are blocked.

**How it avoids made-up law**
- **A measured relevance cutoff** (L2 distance 1.25) drops off-topic documents instead of padding the answer with them.
- **If nothing relevant is found, it says so**, rather than answering from nothing.
- **The model is told never to invent** a case, section or citation.
- **Every answer shows its sources** and a quality score labelled as quality, not correctness.

**Known gaps:**
- There is no hard code check of cited sections against the sources yet.
- The legal library is narrow, so everyday questions lean on web search.
- It works in English text only.

## 3. Dub-Fit

![Dub-Fit](docs/screenshots/dubfit.png)

**The problem:** when a show is adapted into Hindi, Tamil or another language, the translated line often runs longer than the shot. The voice keeps going after the mouth stops, or the speech gets sped up and sounds robotic.

**How it works**
1. **Measure** (code): the time slot for each line comes from the script.
2. **Set the pace limit** (code): the fastest comfortable pace is taken from the fastest 10% of the show's own original lines. No outside numbers are needed.
3. **Translate** (AI), then **check** in code: syllables ÷ slot shows which lines spill over.
4. **Shorten** (AI) with an exact syllable budget, then **re-check in code**. The model never marks its own work.
5. **Review** (human): the editor checks only the flagged lines.

**Results:**
- Across all 1,487 lines in the input pack, a third have less than 30% room, so even a slightly longer translation won't fit.
- The syllable counter handles English and Indic scripts (Hindi, Bengali, Odia and others). It matched hand counts exactly on 5 of 7 test lines.

[Folder and run steps](p3_dubfit)

---

## Run it yourself

```bash
git clone https://github.com/Sanidhya-Jindal/kuku-fm-assignment
cd kuku-fm-assignment/p1_promo_finder      # or p3_dubfit; Nyaya AI has its own repo
pip install -r requirements.txt
streamlit run app.py
```

Each folder's README also has command-line runs and tests.

### Swap the AI model

Every tool reads the same environment variables, so a different or stronger model plugs in with no code changes:

```bash
export LLM_PROVIDER=openai                          # gemini | anthropic | openai (any OpenAI-style server)
export LLM_BASE_URL=https://api.groq.com/openai/v1  # e.g. Groq, OpenRouter, Ollama
export LLM_MODEL=<model-id>                         # copy from your provider's console
export LLM_API_KEY=<your-key>                       # never commit this
```

In the web apps, you can enter the provider, model and key on the page instead. They are used for that run only.

## Repository layout

```
p1_promo_finder/   parse.py · rules.py (free mode) · llm_mode.py (AI mode) · run.py · eval.py · app.py
p2_nyaya_ai/       test cases · run_tests.py (runs them against Nyaya AI) · outputs/   (app code: nyaya-ai- repo)
p3_dubfit/         dubfit.py · app.py · tests/
docs/              2-page solution docs (PDF) and screenshots
```

## What's not in this repo

Kuku's input pack (the screenplays) is confidential, so it isn't here. The raw outputs for Problems 1 and 3 aren't either, because they quote the scripts; they were shared separately. To try the apps, upload your own copy of the scripts.

## AI tools used

This was built with Claude (Anthropic) for planning, code and research. Every decision, result and failure written up here was checked by running the tools on real inputs.
