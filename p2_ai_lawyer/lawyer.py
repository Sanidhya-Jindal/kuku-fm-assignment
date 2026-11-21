"""Core flow: classify -> build the case -> explain where they stand -> draft -> practise.
use_llm=False runs a free offline version (keyword rules + fixed text, English only)."""
import re
from kb import TOPICS, facts_for, FACT
import guard
import templates

CHECKLIST = {
    "deposit": ["rent agreement", "deposit payment proof", "rent receipts", "move-out / key handover proof",
                "photos of the flat when you left", "chats or emails with the landlord"],
    "consumer": ["order or invoice", "payment proof", "complaint / ticket numbers", "chats or emails with the company",
                 "photos or video of the defect"],
    "wages": ["offer or appointment letter", "payslips", "attendance or work proof", "bank statements",
              "emails asking for your salary"],
    "cheque": ["the original cheque", "bank return memo", "proof of the debt (agreement, messages)",
               "date you received the return memo"],
    "cyber": ["transaction / UTR IDs", "screenshots", "fraudster's number or UPI ID", "bank SMS alerts",
              "exact time of the fraud"],
}
EVIDENCE_WORDS = {"agreement": 0, "receipt": 2, "screenshot": 1, "email": 5, "whatsapp": 5, "chat": 5, "invoice": 0,
                  "payslip": 1, "salary slip": 1, "memo": 1, "photo": 4, "offer letter": 0, "bank statement": 3}
NEXT_STEPS = {
    "deposit": ["Write to the landlord (WhatsApp + email) asking for the deposit by a clear date. Keep it polite and factual.",
                "If no reply, send a legal notice (draft below) by Speed Post.",
                "Still unpaid: file a money recovery claim, or go to the rent authority if your state has one. Lok Adalat is a cheaper way to settle."],
    "consumer": ["Complain to the company in writing and note the ticket number.",
                 "Call the National Consumer Helpline 1915 (free).",
                 "Still stuck: send a notice, then file online at the District Consumer Commission."],
    "wages": ["Email HR/manager asking for the exact unpaid amount and a payment date.",
              "Send a legal notice (draft below).",
              "Complain to your state Labour Department / labour authority."],
    "cheque": ["Note the date you got the bank's return memo: the 30-day clock for the notice starts there.",
               "Send the demand notice (draft below) within 30 days.",
               "Wait 15 days after they receive it. If unpaid, file the complaint within the next month. A lawyer helps here because the dates are strict."],
    "cyber": ["Call 1930 now, or report on cybercrime.gov.in.", "Call your bank and block the card/UPI.",
              "Save every screenshot and transaction ID. Do not delete the chat."],
}

SYSTEM = """You help ordinary people in India with everyday legal problems. You are NOT a lawyer, and you say so when it matters.
Rules:
- Use ONLY the FACTS given. End every statement about the law with its fact ID in brackets, like [C4].
- Never name an Act, section, rule, court, or past case that is not written in the FACTS. If the FACTS don't cover something, say plainly "I don't know this for sure" and point to a lawyer or the free legal aid line 15100.
- Never promise an outcome. Never invent amounts, dates or names.
- Reply in the SAME language and script the user wrote in (Hindi in Devanagari, Hinglish in Latin letters, etc.).
- Plain, short, kind. No legal jargon without explaining it."""

ADVISE = """FACTS:
{facts}

CASE FILE (built from what the user said):
{case}

USER SAID:
{text}

Write these short parts with headings: 1) What I understood 2) Where you stand 3) What you can do next (numbered steps)
4) Proof to collect 5) When you need a real lawyer. If key details are missing, ask up to 3 questions at the end."""

CASE = """Turn the user's story into a case file. Use only what they said; write "unknown" if not said.
Topics: {topics}
USER SAID:
{text}
Return JSON: {{"topic": one of [{keys}, "other"], "language": "language the user wrote in",
"what_happened": "2 lines", "timeline": [{{"date": "...", "event": "..."}}], "amount": "number or unknown",
"other_party": "...", "user_name": "unknown unless given", "evidence_have": [...], "evidence_missing": [...],
"questions": ["up to 3 questions that would most change the advice"]}}"""

PRACTICE = """Role-play. You are the {side} in this dispute. Push back the way a real {side} would (excuses, delays, half-truths),
but never threaten or abuse. Keep each reply to 2-3 sentences. Reply in the user's language.
After your in-character reply, add a line starting "Coach:" with one tip for the user, using only these FACTS:
{facts}
CASE: {case}
CONVERSATION SO FAR:
{history}
USER: {msg}"""


def classify_offline(text):
    t = text.lower()
    scores = {k: sum(w in t for w in v["keywords"]) for k, v in TOPICS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "other"


def case_offline(text, topic):
    amt = re.search(r"(?:rs\.?|₹|inr)\s*([\d,]+)|([\d,]{3,})\s*(?:rs|rupees|/-)", text, re.I)
    dates = re.findall(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2} (?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*(?: \d{4})?)", text, re.I)
    have = sorted({w for w in EVIDENCE_WORDS if w in text.lower()})
    return {"topic": topic, "language": "unknown (offline mode replies in English)",
            "what_happened": text[:300], "timeline": [{"date": d, "event": "(see story)"} for d in dates],
            "amount": (amt.group(1) or amt.group(2)).replace(",", "") if amt else "unknown",
            "other_party": TOPICS.get(topic, {}).get("other_side", "unknown"), "user_name": "unknown",
            "evidence_have": have, "evidence_missing": CHECKLIST.get(topic, []),
            "questions": ["When exactly did this happen (dates)?", "How much money is involved?",
                          "What proof do you have in writing?"]}


def advise_offline(topic, case, facts):
    if topic == "other":
        return ("I don't cover this kind of problem yet, and I don't want to guess about the law. "
                "Please talk to a lawyer. If money is a problem, call the free legal aid helpline 15100 [G1].")
    parts = [f"**What I understood:** {TOPICS[topic]['title']}.",
             "**Where you stand:**\n" + "\n".join(f"- {f['text']} [{f['id']}]" for f in facts if f["topic"] == topic),
             "**What you can do next:**\n" + "\n".join(f"{i}. {s}" for i, s in enumerate(NEXT_STEPS[topic], 1)),
             "**Proof to collect:** " + ", ".join(CHECKLIST[topic]) + ".",
             "**When you need a real lawyer:** if the other side sends a legal reply, if police or a court gets involved, "
             "or if the amount is large. Free legal aid: 15100 [G1].",
             "**Questions for you:** " + " ".join(case["questions"])]
    return "\n\n".join(parts)


def run(text, use_llm=False, **kw):
    """One full pass for a user's story. Returns everything shown to the user plus the checks."""
    import json
    if use_llm:
        from llm import chat_json, chat
        keys = ", ".join(TOPICS)
        case = chat_json(CASE.format(topics="; ".join(f"{k}: {v['title']}" for k, v in TOPICS.items()), keys=keys, text=text), **kw)
        topic = case.get("topic") if case.get("topic") in TOPICS else "other"
    else:
        topic = classify_offline(text)
        case = case_offline(text, topic)
    facts = facts_for(topic) if topic in TOPICS else facts_for("none")
    if use_llm:
        fact_txt = "\n".join(f"[{f['id']}] {f['text']}" for f in facts)
        raw = chat(ADVISE.format(facts=fact_txt, case=json.dumps(case, ensure_ascii=False), text=text), SYSTEM, **kw)
    else:
        raw = advise_offline(topic, case, facts)
    clean, removed = guard.check_citations(raw, facts)
    bad_ids = guard.check_fact_ids(clean, facts)
    for i in bad_ids:  # a fact ID the model made up: drop the tag
        clean = clean.replace(f"[{i}]", "")
    flags = guard.lawyer_flags(text, topic)
    draft = templates.draft(topic, case)
    if flags:
        clean = ("**Please speak to a real lawyer soon** (" + "; ".join(flags) +
                 "). If cost is a worry, call the free legal aid helpline 15100 [G1].\n\n" + clean)
        if any(w in flags[0] for w in ("accused", "court")):
            draft = None  # someone defending a case needs a lawyer, not a self-made notice
    if removed:
        clean += "\n\n_Note: I removed a part of my answer that mentioned a law I could not verify._"
    used = sorted(set(re.findall(r"\[([A-Z]\d)\]", clean)) & set(FACT))
    return {"topic": topic, "case": case, "answer": clean, "draft": draft,
            "sources": [{"id": i, "source": FACT[i]["source"]} for i in used],
            "checks": {"removed_unverified_law": removed, "unknown_fact_ids": bad_ids,
                       "lawyer_flags": flags, "raw_answer_before_checks": raw}}


def practice(msg, history, topic, case, use_llm=True, **kw):
    if not use_llm:
        return "Practice mode needs an AI model (add an API key)."
    import json
    from llm import chat
    facts = "\n".join(f"[{f['id']}] {f['text']}" for f in facts_for(topic))
    side = TOPICS.get(topic, {}).get("other_side") or "other side"
    out = chat(PRACTICE.format(side=side, facts=facts, case=json.dumps(case, ensure_ascii=False),
                               history="\n".join(history[-8:]), msg=msg), SYSTEM, temperature=0.7, **kw)
    clean, _ = guard.check_citations(out, facts_for(topic))
    return clean
