"""Safety checks in plain code, run on every answer the model writes.
1) Law check: every Act, Section, or court case named in the answer must appear in a retrieved fact.
   If not, that sentence is removed and the user is told.
2) Lawyer check: some situations always get a "see a real lawyer" line, whatever the model said."""
import re

SECTION = re.compile(r"\b(?:section|sec\.?|s\.|धारा|ধারা|ধাৰা|धारा)\s*(\d+[A-Z]?)", re.I)
ACT = re.compile(r"\b((?:[A-Z][a-z]+ ){1,6}Act)\b,?\s*(\d{4})?")
CASE = re.compile(r"\b[A-Z][A-Za-z.&]+(?: [A-Z][A-Za-z.&]+)* (?:v\.|vs\.?|versus) [A-Z][A-Za-z.&]+", re.I)
COURT_SAID = re.compile(r"(supreme court|high court)\s+(has\s+)?(held|ruled|said|decided)", re.I)
IPC_ETC = re.compile(r"\b(IPC|BNS|CrPC|BNSS|CPC|Penal Code|Nyaya Sanhita|Suraksha Sanhita)\b")

URGENT_LAWYER = {
    "you are accused or police are involved": r"\b(police|fir against me|arrest|bail|summons|warrant|court notice|charge ?sheet|accused|giraftaar|thana)\b",
    "court papers or a deadline from a court": r"\b(court date|hearing|ex[- ]parte|decree|served|summon)",
    "violence, threats or safety risk": r"\b(threat|beat|hit me|violence|harass|blackmail|maar|dhamki|unsafe)\b",
    "property, family or inheritance matter": r"\b(divorce|custody|property dispute|land|will|inheritance|dowry|maintenance|498)\b",
}


ABBR = re.compile(r"\b(v|vs|Rs|No|Sec|s|Mr|Mrs|Dr|Ltd|Pvt|etc)\.\s", re.I)


def _pieces(text):
    """Split into [sentence, gap, sentence, gap...] keeping newlines and bullets intact.
    Does not break 'Ram v. Shyam' or 'Rs. 500'."""
    protected = ABBR.sub(lambda m: m.group(1) + "\u2024 ", text)
    return [p.replace("\u2024", ".") for p in re.split(r"((?<=[.!?।])\s+|\n+)", protected)]


def check_citations(answer, facts):
    """Removes sentences that name laws/sections/cases not found in the retrieved facts."""
    allowed = " ".join(f["text"] for f in facts).lower()
    allowed_sections = {x.lower() for x in SECTION.findall(allowed)}
    out, removed = [], []
    for i, s in enumerate(_pieces(answer)):
        if i % 2:  # whitespace between sentences
            out.append(s)
            continue
        bad = [m for m in SECTION.findall(s) if m.lower() not in allowed_sections]
        bad += [a for a, _ in ACT.findall(s) if a.strip().lower() not in allowed]
        bad += CASE.findall(s) + [m.group(0) for m in COURT_SAID.finditer(s)] + IPC_ETC.findall(s)
        if bad:
            removed.append({"sentence": s, "unverified": bad})
        else:
            out.append(s)
    return "".join(out).strip(), removed


def check_fact_ids(answer, facts):
    ids = set(re.findall(r"\[([A-Z]\d)\]", answer))
    return sorted(ids - {f["id"] for f in facts})


def lawyer_flags(user_text, topic):
    flags = [why for why, pat in URGENT_LAWYER.items() if re.search(pat, user_text, re.I)]
    if topic == "other":
        flags.append("outside what this assistant covers")
    return flags
