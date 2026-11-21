# Problem 2: Build an AI Lawyer: Haq Saathi

<div class="meta">Sanidhya Jindal · Roll 123MM0666 · Metallurgical & Materials Engineering, NIT Rourkela<br>
Prototype: [link] · Raw outputs: [link] · Walkthrough: [link]</div>

## What I picked and why

I chose depth over breadth: five money problems where people usually give up, even though a clear official route exists. These are a **security deposit not returned**, **refund / defective product / bad service**, **unpaid salary**, **cheque bounce**, and **online/UPI fraud**. Everything else (family, property, criminal defence, tax) gets an honest "I don't cover this, here is free legal aid" reply.

## Assumptions

- The user is the person who is owed money. If they are accused, or police or a court is involved, the bot steps back and sends them to a lawyer.
- Claims are small, within the District Consumer Commission's ₹50 lakh limit.
- Rent law differs by state, so the bot never assumes the Model Tenancy Act applies. It says "only if your state has adopted it".
- The legal facts were checked on 21 Nov 2026, and the app shows that date. The Labour Codes are in force from 21 Nov 2025, but some of their rules are still being phased in.

## What it does

1. **Takes the problem** by text or voice, in any language (Hindi, Hinglish, Odia, …). Voice is turned into text by the same model.
2. **Builds the case:** what happened, a timeline, the amount, the other party, the proof they have, the proof they still need, and the 3 questions that would most change the advice.
3. **Explains where they stand and what to do next**, in their own language and in plain words. Every legal statement is tagged with a fact ID like `[C4]` that links to a source.
4. **Prepares the document:** a legal/demand notice (deposit, consumer, salary, or a cheque-bounce notice with the 15-day demand) or a fraud report for 1930 and the bank. Unknown details stay as `[____]`.
5. **Practice mode:** the bot plays the landlord, company, or employer and pushes back, with a one-line "Coach:" tip after each reply.

## How it avoids inventing laws

| Layer | How |
|---|---------|
| Checked fact list | 22 short facts, each with a source link. The model only sees the facts for the user's topic. |
| Tag every claim | The model must end each legal statement with a fact ID. Code strips made-up IDs. |
| Law check in code | Any Act, Section (also *dhara* in Hindi), court ruling, "X v. Y" case name, or IPC/BNS mention that is not in the given facts gets its sentence removed, and the user is told. |
| Fixed templates | Notice wording comes from code, never from the model. |
| Lawyer rules in code | Police, court papers, being accused, violence, family or property matters, and unknown topics always get a "see a real lawyer + call 15100" line. An accused person gets no self-made notice. |

**Law-check test** (`tests/test_guard.py`): it removed 6 out of 6 invented claims (Section 420 IPC, BNS 318, a fake *Sharma v. Gupta* ruling, the replaced Payment of Wages Act, a made-up "Section 27" of the Consumer Protection Act, and *dhara 406* written in Hindi) and kept 4 out of 4 real ones. **It missed** "three years to file a consumer complaint" (the real limit is two years), because no law is named in that sentence. This is the main gap left.

## Test cases (12, in `tests/cases.json`, raw outputs in `outputs/`)

The cases are in English, Hinglish, Hindi and Odia. They include a trap that asks for "an IPC section and a Supreme Court judgment", an out-of-scope divorce question, a user who is accused, and a vague message.

| Mode | Right topic | Lawyer referral when needed | Final answers with unverified law |
|---|---|---|---|
| Offline (free) | 11/12 | 12/12 | 0/12 |
| AI ([model]) | [fill after `run_tests.py --mode llm`] | [ ] | [ ] |

## Where it fails

- **Offline mode is English-only keyword matching.** The Odia case was missed and fell back to "see a lawyer", which is safe but not helpful. AI mode exists for this.
- **Wrong numbers with no law named** get past the law check (see above).
- **Offline mode gives an accused person the claimant's steps.** The lawyer warning comes first and no notice is drafted, but the steps are still the wrong ones.
- It can't check that names, addresses or dates in the notice are true. State-specific details (rent courts, fee tables) are not covered.
- The facts go stale. Each one carries its source, and they need re-checking every month.

## Scale and cost

- **Per conversation:** about 2 model calls, roughly 4k input tokens and 1k output tokens. That is under $0.01 on Gemini Flash paid prices, and the free tier covers testing.
- **Adding a topic** means adding checked facts plus test cases, with no code changes.
- **People in the loop:** a lawyer reviews new or changed facts, and a legal-aid volunteer queue reviews flagged chats (police, court, violence).
- **Success measures:** the share of users who send the notice or file, the share who say it was resolved, and zero answers with unverified law in a weekly random audit.

## AI tools used

Claude (Anthropic): planning, code, research. [Add any other tool you used.]
**Where it got it wrong:** it set `gemini-2.5-flash` as the default model. A search showed Google had limited 2.5 access for new projects, so I switched to `gemini-3.8-flash`. Its first law check also split sentences at "v.", so half of a fake case name survived. Feeding it fake laws on purpose caught this.

<p class="src">Fact sources (all in kb.py): PIB/Labour Ministry (Labour Codes, 21 Nov 2025); PIB, Consumer Protection Jurisdiction Rules 2021; Consumer Protection Act 2019, s.69; NI Act 1881, ss.138/142 guides; PRS India (Model Tenancy Act); NALSA (15100, s.12 LSA Act); National Cybercrime Reporting Portal (1930).</p>
