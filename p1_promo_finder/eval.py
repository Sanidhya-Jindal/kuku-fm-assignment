"""Quality checks a human runs.
  python eval.py sheet outputs/rules            -> makes review_sheet.csv (top 10, blank grade columns)
  python eval.py score outputs/rules/review_sheet.csv   -> % of promos that pass each test
  python eval.py compare outputs/rules outputs/llm      -> how often the two modes pick the same moments
Grades: Y = yes, P = partly, N = no."""
import csv, json, sys
from pathlib import Path
from rules import describe, _overlap


def sheet(folder, n=10):
    res = json.loads((Path(folder) / "promos.json").read_text())
    with open(Path(folder) / "review_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "promo_id", "segments", "hook", "cliffhanger", "hook_ok", "cliff_ok", "standalone_ok", "would_post", "note"])
        for p in res["promos"][:n]:
            w.writerow([p["rank"], p["promo_id"], describe(p), p["hook"], p["cliffhanger"], "", "", "", "", ""])
    print("Fill in Y/P/N in", Path(folder) / "review_sheet.csv")


def score(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    for col in ["hook_ok", "cliff_ok", "standalone_ok", "would_post"]:
        g = [r[col].strip().upper() for r in rows if r[col].strip()]
        if g:
            print(f"{col:14s} Y {g.count('Y')}/{len(g)}  P {g.count('P')}  N {g.count('N')}")


def compare(a, b):
    A = json.loads((Path(a) / "promos.json").read_text())["promos"]
    B = json.loads((Path(b) / "promos.json").read_text())["promos"]
    hits = [p["promo_id"] for p in B if any(_overlap(p, q) >= 0.5 for q in A)]
    print(f"{len(hits)}/{len(B)} promos in {b} overlap a promo in {a} by >=50%. "
          f"Disagreements are the first place a human should look.")


if __name__ == "__main__":
    {"sheet": lambda: sheet(sys.argv[2]), "score": lambda: score(sys.argv[2]),
     "compare": lambda: compare(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
