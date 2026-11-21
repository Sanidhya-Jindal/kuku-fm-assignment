"""Find promos in a folder of screenplays.
  python run.py --input path/to/scripts --mode rules         (free, no key)
  python run.py --input path/to/scripts --mode llm           (set LLM_PROVIDER / LLM_API_KEY first)
Writes promos.json, promos.csv, report.md and qa.json to --out."""
import argparse, csv, json
from pathlib import Path
from parse import load_show, fmt
import rules


def post_first_order(promos):
    """Ranking rule: best score, nudged toward early episodes (new viewers start at Ep1, fewer spoilers),
    with at most one promo per episode in the first 10 posts for variety."""
    def key(p):
        ep = p["segments"][0]["episode"]
        return -(p["scores"]["total"] + (1.0 if ep <= 10 else 0.5 if ep <= 20 else -0.5 if ep > 35 else 0))
    order, seen, rest = [], set(), []
    for p in sorted(promos, key=key):
        ep = p["segments"][0]["episode"]
        (rest if ep in seen and len(order) < 10 else order).append(p)
        seen.add(ep)
    return order + rest


def analyze(show, mode="rules", log=print, **kw):
    rejected, llm_rank = [], []
    if mode == "llm":
        import llm_mode
        promos, rejected, llm_rank = llm_mode.run(show, log=log, **kw)
        pos = {r["promo_id"]: i for i, r in enumerate(llm_rank)}
        reason = {r["promo_id"]: r.get("reason", "") for r in llm_rank}
        promos.sort(key=lambda p: (pos.get(p["promo_id"], 999), -p["scores"]["total"]))
        for p in promos:
            p["rank_reason"] = reason.get(p["promo_id"], "")
    else:
        promos = [p for ep in show for p in rules.find_promos(ep)]
        promos = post_first_order(promos)
        for p in promos:
            p["duration"] = round(sum(s["end"] - s["start"] for s in p["segments"]), 2)
    for i, p in enumerate(promos, 1):
        p["rank"] = i
        p.setdefault("promo_id", f"P{i:03d}")
    return {"mode": mode, "promos": promos, "rejected_by_checks": rejected, "qa": qa(promos, rejected, show)}


def qa(promos, rejected, show):
    """Automatic checks. They catch broken promos, not boring ones: a human still reviews the top 10."""
    d = [p["duration"] for p in promos]
    flagged = [p["promo_id"] for p in promos if p.get("flags")]
    eps_covered = {s["episode"] for p in promos for s in p["segments"]}
    return {"episodes_in": len(show), "promos_out": len(promos), "episodes_with_a_promo": len(eps_covered),
            "duration_min_max": [min(d, default=0), max(d, default=0)],
            "all_within_20_60s": all(19.9 <= x <= 60.1 for x in d),
            "promos_with_warning_flags": len(flagged), "flagged_ids": flagged,
            "model_outputs_rejected": len(rejected)}


def write(result, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "promos.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    (out / "qa.json").write_text(json.dumps(result["qa"], indent=2))
    with open(out / "promos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "promo_id", "segments", "duration_s", "hook", "cliffhanger", "why", "score", "flags"])
        for p in result["promos"]:
            w.writerow([p["rank"], p["promo_id"], rules.describe(p), p["duration"], p["hook"], p["cliffhanger"],
                        p["why"], p["scores"]["total"], "; ".join(p.get("flags", []))])
    lines = [f"# Promo report ({result['mode']} mode)\n", "```", json.dumps(result["qa"], indent=1), "```\n",
             "## Post these first\n"]
    for p in result["promos"][:10]:
        lines += [f"**#{p['rank']} {p['promo_id']}** - {rules.describe(p)} ({p['duration']}s, score {p['scores']['total']})",
                  f"- Hook: {p['hook']}", f"- Cliffhanger: {p['cliffhanger']}", f"- Why: {p['why']}"]
        if p.get("rank_reason"):
            lines.append(f"- Why post early: {p['rank_reason']}")
        if p.get("flags"):
            lines.append(f"- Check: {'; '.join(p['flags'])}")
        lines.append("")
    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--mode", choices=["rules", "llm"], default="rules")
    ap.add_argument("--out", default="outputs")
    ap.add_argument("--chunk", type=int, default=3, help="episodes per LLM call; use 1 if your free tier rejects big requests")
    a = ap.parse_args()
    show = load_show(a.input)
    res = analyze(show, a.mode, **({"chunk": a.chunk} if a.mode == "llm" else {}))
    write(res, Path(a.out) / a.mode)
    print(json.dumps(res["qa"], indent=1))
