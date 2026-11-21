"""One small function to call any chat model. Swap models with env vars, no code change:
  LLM_PROVIDER = gemini | openai | anthropic      (openai also covers Groq, OpenRouter, Ollama, Together...)
  LLM_MODEL    = model name, e.g. gemini-3.8-flash, gemini-3.5-flash-lite, claude-sonnet-5-5 (copy exact IDs from your console)
  LLM_API_KEY  = your key
  LLM_BASE_URL = only for openai-style servers, e.g. https://api.groq.com/openai/v1
"""
import json, os, re, time
import requests

DEFAULT_MODEL = {"gemini": "gemini-3.8-flash", "anthropic": "claude-sonnet-5-5"}  # openai-style: set LLM_MODEL


def chat(prompt, system="", provider=None, model=None, api_key=None, base_url=None, temperature=0.2, retries=4):
    provider = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower()
    model = model or os.getenv("LLM_MODEL") or DEFAULT_MODEL.get(provider, "")
    key = api_key or os.getenv("LLM_API_KEY", "")
    if not model or not key:
        raise ValueError("Set LLM_API_KEY (and LLM_MODEL for openai-style servers).")
    for attempt in range(retries):
        try:
            if provider == "gemini":
                body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": temperature}}
                if system:
                    body["systemInstruction"] = {"parts": [{"text": system}]}
                r = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    headers={"x-goog-api-key": key}, json=body, timeout=180)
                r.raise_for_status()
                parts = r.json()["candidates"][0]["content"]["parts"]
                return "".join(p.get("text", "") for p in parts if not p.get("thought"))
            if provider == "anthropic":
                r = requests.post("https://api.anthropic.com/v1/messages",
                                  headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                                  json={"model": model, "max_tokens": 4096, "system": system, "temperature": temperature,
                                        "messages": [{"role": "user", "content": prompt}]}, timeout=180)
                r.raise_for_status()
                return "".join(c.get("text", "") for c in r.json()["content"])
            base = base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
            msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
            r = requests.post(f"{base.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {key}"},
                              json={"model": model, "messages": msgs, "temperature": temperature}, timeout=180)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code in (429, 500, 503) and attempt < retries - 1:
                time.sleep(15 * (attempt + 1))  # free tiers rate-limit; wait and retry
                continue
            raise


def chat_json(prompt, system="", **kw):
    """Asks for JSON and pulls the first JSON object/array out of the reply."""
    text = chat(prompt + "\n\nReply with JSON only.", system, **kw)
    m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
    if not m:
        raise ValueError(f"Model did not return JSON: {text[:300]}")
    return json.loads(m.group(1))
