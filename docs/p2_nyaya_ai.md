# Problem 2: Build an AI Lawyer: Nyaya AI

<div class="meta">Sanidhya Jindal · Roll 123MM0666 · Metallurgical & Materials Engineering, NIT Rourkela<br>
Code: github.com/Sanidhya-Jindal/nyaya-ai- · Test cases and raw outputs: github.com/Sanidhya-Jindal/kuku-fm-assignment (p2_nyaya_ai) · Walkthrough: [link]</div>

## Why this problem, and what I built

Most people never get help with everyday legal problems: they don't know which law applies or where to start, and a lawyer feels expensive. The biggest risk with an AI lawyer is that it invents laws, sections and cases with confidence. So I built Nyaya AI around one rule: **answer only from documents it has actually found, and say so when it finds nothing.**

It has two modes:

- **Citizen** gives plain-language guidance on rights, procedures and the statutes involved.
- **Lawyer** is for deeper research: it extracts the legal issues, plans queries, retrieves sources, drafts an answer, then critiques and revises it.

## Assumptions

- Users ask about **Indian law**, in text. Questions about another country's law are declined politely.
- The user wants to understand their position and next steps. Nyaya does not replace a lawyer, and every answer carries that disclaimer.

## How it works

| Step | What happens |
|--|--------|
| 1. Intent gate | The model sorts each message into greeting, out of scope (non-Indian law), or Indian legal question. Greetings get a short reply and skip the research pipeline entirely, which cuts cost on non-legal messages by about 97%. |
| 2. Query rewrite | Follow-ups like "what's the punishment for it?" are rewritten into a standalone search query using the conversation history, before retrieval. |
| 3. Hybrid retrieval | FAISS semantic search over 4,209 chunks from 39 Indian legal documents (acts, judgments, IPC/CrPC/Constitution Q&A) runs in parallel with a Tavily web search. Social-media and user-generated sites are blocked as sources. |
| 4. Answer | **Citizen:** a short research loop, then a grounded answer. **Lawyer:** issue extractor, planner, retriever, drafter and critic agents loop until the critic scores the draft 0.7 or higher, or 3 rounds pass. |
| 5. Score and show | An AI judge rates relevance, faithfulness and clarity, blended with semantic similarity. Sources and the score sit in expandable panels under the answer. |

Stack: FastAPI, LangGraph (13 nodes in two graphs), Groq Llama 3.1 8B, FAISS (all-MiniLM-L6-v2), Tavily, SQLite, React and Clerk, plus a Streamlit interface.

## How it avoids made-up laws

1. **A measured relevance cutoff.** FAISS returns 8 candidates, and only those within an L2 distance of 1.25 are kept. I set this by measuring: in-domain questions landed at 0.70–1.15, and off-topic ones at 1.31–1.76. Irrelevant documents are dropped, not used as filler.
2. **Honest failure.** If both the library and the web come back empty, the pipeline skips the model and says it couldn't find reliable information, instead of answering with nothing to stand on.
3. **Grounded generation.** The model is told never to invent or guess a case name, citation, section or article. If the sources don't contain one, it must say so.
4. **Self-critique** in lawyer mode catches weak drafts before the user sees them.
5. **Clear labels.** The evaluation is called a *quality* score, not an accuracy score. Every answer says it is not legal advice and that cited acts and judgments should be verified.

## Test cases (12, in `p2_nyaya_ai/tests/cases.json`)

Everyday problems (a deposit in English and in Hinglish, a refund, unpaid salary, a cheque bounce, an urgent UPI fraud, a confusing legal notice), a trap asking for "an IPC section and a Supreme Court judgment", an accused user with a court date, a lawyer-mode question, a California law question and a greeting.

`run_tests.py` saves every raw answer and checks the time taken, whether the answer points to a lawyer, whether it admits a gap, which sections it names, and **case names that appear nowhere in the listed sources**, the first place to look for invented citations.

**Results:** [fill in from `outputs/summary.json`: median time, answers pointing to a lawyer, answers with unsourced case names].

## Where it fails

- **No hard check on citations.** The no-invention rule is an instruction to the model, backed by retrieval. Nothing in code yet compares every cited section against the retrieved text. That is the next thing I would add.
- **The library is narrow.** The 39 documents lean toward recent acts and judgments. Everyday tenancy, consumer and wage questions rely mostly on the web search, which is less reliable.
- **Text and English only.** There is no voice input, and no tuning for Hindi or other Indian languages yet.
- **It explains, but doesn't draft** notices or complaints yet, and the AI judge hasn't been checked against human-labelled answers.
- **Slow and shallow on the free tier:** about 22 seconds at the median (down from about 90), and one research pass to stay within Groq's limits.

## Scale and cost

- **Per question:** a handful of calls to Groq's cheap Llama 3.1 8B plus one Tavily search, the main cost after its free tier. Greetings skip research, so they're nearly free.
- **Swap or grow:** set `GROQ_MODEL` for a larger model; add documents and rebuild the index with one script.
- **People in the loop:** a lawyer reviews the library and a monthly sample of answers; answers naming unsourced cases get flagged.

## Credits and AI tools used

Parts of Nyaya AI's codebase come from the open-source L.A.R.A (Legal Analysis & Research Assistant) project. The agent orchestration, retrieval pipeline, grounding safeguards and evaluation were reworked by me.
**AI tools:** [list the tools you used, and one place where they got it wrong].
