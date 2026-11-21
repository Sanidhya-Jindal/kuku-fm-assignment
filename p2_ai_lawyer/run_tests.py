"""Runs every test case and saves the raw, unedited output.
  python run_tests.py --mode offline        (free, no key)
  python run_tests.py --mode llm            (set LLM_PROVIDER / LLM_MODEL / LLM_API_KEY)"""
import argparse, json, re, time
from pathlib import Path
import guard, lawyer
from kb import facts_for

ap = argparse.ArgumentParser()
ap.add_argument("--mode", choices=["offline", "llm"], default="offline")
ap.add_argument("--cases", default="tests/cases.json")
a = ap.parse_args()
out = Path("outputs") / a.mode
out.mkdir(parents=True, exist_ok=True)
rows = []
for c in json.loads(Path(a.cases).read_text(encoding="utf-8")):
    t0 = time.time()
    try:
        r = lawyer.run(c["text"], use_llm=a.mode == "llm")
    except Exception as e:
        r = {"error": str(e)}
    r["input"] = c
    (out / f"{c['id']}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    if "error" in r:
        rows.append({"id": c["id"], "error": r["error"]})
        continue
    ans = r["answer"]
    # Re-run the law check on the FINAL answer: it must find nothing left to remove.
    _, leftover = guard.check_citations(ans, facts_for(r["topic"]))
    rows.append({
        "id": c["id"], "topic": r["topic"], "topic_ok": r["topic"] == c["expect_topic"],
        "lawyer_line": "real lawyer" in ans.lower() or "15100" in ans,
        "lawyer_ok": (not c["expect_lawyer"]) or ("real lawyer" in ans.lower()),
        "unverified_law_removed": len(r["checks"]["removed_unverified_law"]),
        "unverified_law_left": len(leftover), "unknown_fact_ids": r["checks"]["unknown_fact_ids"],
        "cites_facts": bool(re.search(r"\[[A-Z]\d\]", ans)), "has_draft": bool(r["draft"]),
        "seconds": round(time.time() - t0, 2)})
summary = {"mode": a.mode, "cases": len(rows),
           "topic_correct": sum(x.get("topic_ok", False) for x in rows),
           "lawyer_referral_when_needed": sum(x.get("lawyer_ok", False) for x in rows),
           "final_answers_with_unverified_law": sum(x.get("unverified_law_left", 1) > 0 for x in rows),
           "rows": rows}
(out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=1))
for x in rows:
    print(x)
