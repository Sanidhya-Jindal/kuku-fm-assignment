"""Runs the test cases against a running Nyaya AI backend and saves the raw, unedited answers.

1. Start Nyaya AI's backend (in the nyaya-ai- repo):  cd backend && python app.py   (serves on port 8010)
2. Then here:  python run_tests.py
Writes outputs/<case>.json for every case and outputs/summary.json with simple automatic checks."""
import argparse, json, re, time
from pathlib import Path
import requests

CASE_NAME = re.compile(r"\b([A-Z][\w.&]+(?: [A-Z][\w.&]+)*) (?:v\.|vs\.?|versus) ([A-Z][\w.&]+)")
LAWYER = re.compile(r"\b(lawyer|advocate|legal aid|15100|legal professional|legal expert)\b", re.I)
GAP = re.compile(r"couldn't find|could not find|no reliable information|not (?:in|available in) my sources", re.I)
SECTION = re.compile(r"\b(?:section|sec\.)\s*\d+[A-Z]?", re.I)

ap = argparse.ArgumentParser()
ap.add_argument("--url", default="http://127.0.0.1:8010/process_query")
ap.add_argument("--cases", default="tests/cases.json")
a = ap.parse_args()

out = Path("outputs")
out.mkdir(exist_ok=True)
rows = []
for c in json.loads(Path(a.cases).read_text(encoding="utf-8")):
    t0 = time.time()
    try:
        r = requests.post(a.url, json={"user_query": c["text"], "role": c["role"], "thread_id": f"test-{c['id']}"}, timeout=300)
        r.raise_for_status()
        res = r.json()
    except Exception as e:
        res = {"error": str(e)}
    secs = round(time.time() - t0, 1)
    (out / f"{c['id']}.json").write_text(json.dumps({"input": c, "response": res, "seconds": secs}, indent=2, ensure_ascii=False), encoding="utf-8")
    ans = res.get("final_analysis", "") or ""
    sources = " ".join(res.get("sources") or [])
    cases_named = [re.sub(r"^(In|The|See|As|Per) ", "", " v. ".join(m)) for m in CASE_NAME.findall(ans)]
    rows.append({
        "id": c["id"], "seconds": secs, "error": res.get("error"),
        "sources_listed": len(res.get("sources") or []),
        "mentions_lawyer_or_legal_aid": bool(LAWYER.search(ans)),
        "admits_gap": bool(GAP.search(ans)),
        "sections_named": sorted(set(m.lower() for m in SECTION.findall(ans))),
        # A case name in the answer that appears nowhere in the listed sources needs a human check.
        "case_names_not_in_sources": [n for n in cases_named if n.split(" v. ")[0].split()[0].lower() not in sources.lower()],
    })
    print(rows[-1])

summary = {"cases": len(rows), "errors": sum(bool(x["error"]) for x in rows),
           "median_seconds": sorted(x["seconds"] for x in rows)[len(rows) // 2],
           "answers_mentioning_lawyer_or_legal_aid": sum(x["mentions_lawyer_or_legal_aid"] for x in rows),
           "answers_with_unsourced_case_names": sum(bool(x["case_names_not_in_sources"]) for x in rows),
           "rows": rows}
(out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=1))
