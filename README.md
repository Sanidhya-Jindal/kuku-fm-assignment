# Kuku FM: AI Generalist Assignment

**Sanidhya Jindal** · 123MM0666 · Metallurgical & Materials Engineering, NIT Rourkela

| Folder | Problem | What it does |
|---|---|---|
| [`p1_promo_finder`](p1_promo_finder) | 1. Find the Promos | Reads microdrama screenplays and finds ranked 20–60s promo cuts (hook, cliffhanger, timestamps). |
| [`p2_ai_lawyer`](p2_ai_lawyer) | 2. AI Lawyer: Haq Saathi | Legal help chat for everyday problems in India (deposit, refund, salary, cheque bounce, UPI fraud). Text or voice, any language. Only states checked facts. |
| [`p3_dubfit`](p3_dubfit) | 3. Own problem: Dub-Fit | Checks whether each translated line fits its original time slot, and shortens the ones that don't. |

Each folder has its own README with run steps, a Streamlit app (`streamlit run app.py`), and a free mode that needs no API key.

## Swapping the model

Every tool reads the same environment variables:

```bash
export LLM_PROVIDER=openai                          # gemini | anthropic | openai (= any OpenAI-style server)
export LLM_BASE_URL=https://api.groq.com/openai/v1  # Groq, OpenRouter, Ollama, ...
export LLM_MODEL=<model-id>                         # copy from console.groq.com/docs/models
export LLM_API_KEY=your_key                         # never commit this
```

## Confidentiality

Kuku's input pack (screenplays) is not in this repo, and neither are outputs that quote it. Run the tools on your own copy of the scripts.
