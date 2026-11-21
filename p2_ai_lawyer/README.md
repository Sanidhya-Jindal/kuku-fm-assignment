# Haq Saathi: AI legal help for everyday problems (Kuku AI Generalist, Problem 2)

A chat where a person in India describes a problem by text or voice, in their own language. It builds their case, explains where they stand using only checked facts, drafts the notice, and lets them practise against the other side.

**Covers (in depth):** security deposit not returned, refund / defective product / bad service, unpaid salary, cheque bounce, online/UPI fraud.
**Does not cover:** family, property, criminal defence, tax, or anything else. It says so and points to free legal aid (15100).

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py                      # pick Offline (free) or AI mode in the sidebar

python run_tests.py --mode offline        # 12 test cases -> outputs/offline/
export LLM_PROVIDER=gemini LLM_MODEL=gemini-3.8-flash LLM_API_KEY=...   # free key: aistudio.google.com
python run_tests.py --mode llm            # same cases with the model -> outputs/llm/
python tests/test_guard.py                # feeds the law check made-up laws -> outputs/guard_test.json
```

Swap models with `LLM_PROVIDER` (gemini / anthropic / openai = any OpenAI-style server such as Groq or Ollama) and `LLM_MODEL`. No code changes.

## How it stops made-up law

1. **A small checked fact list** (`kb.py`, 22 facts, each with a source link, checked 21 Nov 2026). The model only sees the facts for the user's topic.
2. **The model must tag every legal statement** with a fact ID like `[C4]`. Invented IDs are stripped.
3. **A code check after every answer** (`guard.py`): any Act, Section (also धारा), court ruling, case name ("X v. Y"), IPC/BNS mention that is not in the given facts gets its sentence removed, and the user is told.
4. **Legal documents come from fixed templates**, not from the model. Unknown details stay as `[____]`.
5. **"See a real lawyer" rules in code**: police, court papers, being accused, violence, family or property matters, and unknown topics always get a lawyer + 15100 line. If the user is the accused, no self-made notice is drafted.

**Known gap:** the check catches named laws, not wrong numbers with no law named (for example "three years" instead of two). `tests/test_guard.py` shows this miss on purpose.

## Files
`kb.py` facts · `guard.py` checks · `lawyer.py` flow · `templates.py` notices · `llm.py` model adapter + voice · `app.py` UI · `run_tests.py` / `tests/` test cases
