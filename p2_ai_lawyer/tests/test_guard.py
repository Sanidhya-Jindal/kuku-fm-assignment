"""Feeds the law check made-up legal claims (the kind models invent) and real ones. Run: python tests/test_guard.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import guard
from kb import facts_for

FAKE = ["You can file a police case under Section 420 IPC for cheating.",
        "Under Section 318 of the BNS this is cheating.",
        "The Supreme Court ruled in Sharma v. Gupta that landlords must pay 18% interest.",
        "The Payment of Wages Act, 1936 says salary must be paid by the 7th.",
        "Section 27 of the Consumer Protection Act, 2019 lets you claim triple damages.",
        "मकान मालिक पर धारा 406 के तहत केस होगा।",
        "You have three years to file a consumer complaint."]  # known gap: wrong number, no law named
REAL = ["You have two years to file under Section 69 of the Consumer Protection Act, 2019 [C4].",
        "Call 1915, the National Consumer Helpline [C2].",
        "The District Commission handles claims up to Rs 50 lakh [C3].",
        "धारा 69 के तहत दो साल का समय है [C4]।"]
facts = facts_for("consumer") + facts_for("deposit")
res = []
for s in FAKE + REAL:
    clean, removed = guard.check_citations(s, facts)
    res.append({"sentence": s, "is_fake": s in FAKE, "removed": bool(removed)})
ok = sum(r["removed"] == r["is_fake"] for r in res)
out = {"correct": ok, "total": len(res), "results": res}
Path("outputs").mkdir(exist_ok=True)
Path("outputs/guard_test.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"{ok}/{len(res)} handled correctly")
for r in res:
    print(("OK  " if r["removed"] == r["is_fake"] else "MISS"), r["sentence"])
