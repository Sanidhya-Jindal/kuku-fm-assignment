"""LLM mode: the model reads the script and proposes promos by LINE ID, never by raw timestamp.
Code then turns IDs into timestamps and throws out anything invalid, so the model cannot invent times."""
import json
from llm import chat_json
from parse import fmt
from rules import hook_score, cliff_score, standalone_score, cut_points

SYSTEM = """You are a promo editor for short vertical drama apps (like ReelShort, DramaBox).
A promo is a 20-60 second clip cut from the show, posted on TikTok/Reels/Shorts to pull in NEW viewers.
A good promo:
- opens on a hook in the first 3 seconds (slap, reveal, shocking line) that stops a scrolling viewer
- ends on a cliffhanger: cut at an unresolved moment so the viewer needs to know what happens next
- makes sense to someone who has never seen the show
It is usually one continuous stretch, but may join 2-3 moments (same or different episodes) if that is clearly stronger.
Never start or end in the middle of a line of dialogue."""

PROMPT = """Script lines below. Each line: ID [start-end] TYPE SPEAKER (emotion): text
Episode summaries: {loglines}

{lines}

Find the {k} best promos in these episodes. Use only IDs that appear above.
Return: {{"promos": [{{"segments": [{{"start_id": "...", "end_id": "..."}}],
  "hook": "what happens in the first 3 seconds", "cliffhanger": "the unresolved moment it ends on",
  "why": "one line on why it works", "scores": {{"hook": 1-5, "cliff": 1-5, "standalone": 1-5}}}}]}}"""

RANK = """Here are candidate promos for one show. Rank the 10 you would post FIRST and say why in one line each.
Think about: strongest hook, strongest cliffhanger, needs no backstory, does not spoil big late twists,
and variety (do not post 3 near-identical promos in a row).
{items}
Return: {{"ranking": [{{"promo_id": "...", "reason": "..."}}]}}"""


def _line(b):
    who = f' {b["speaker"]}' if b["speaker"] else ""
    emo = f' ({b["emotion"]})' if b["emotion"] else ""
    return f'{b["id"]} [{fmt(b["start"])}-{fmt(b["end"])}] {b["kind"].upper()}{who}{emo}: {b["text"]}'


def propose(eps, k=4, **kw):
    """eps = a few consecutive episodes. Returns (valid_promos, rejected)."""
    index = {b["id"]: (e, b) for e in eps for b in e["blocks"]}
    lines = "\n".join(_line(b) for e in eps for b in e["blocks"])
    loglines = " | ".join(f'Ep{e["episode"]}: {e["logline"]}' for e in eps)
    out = chat_json(PROMPT.format(loglines=loglines, lines=lines, k=k), SYSTEM, **kw)
    good, bad = [], []
    for p in out.get("promos", []):
        ok, segs, why_bad = True, [], ""
        for sg in p.get("segments", []):
            a, b = index.get(sg.get("start_id")), index.get(sg.get("end_id"))
            if not a or not b:
                ok, why_bad = False, f"unknown ID {sg}"
                break
            if a[0] is not b[0]:
                ok, why_bad = False, f"segment spans two episodes {sg}"
                break
            s, e = a[1]["start"], b[1]["end"]
            if e <= s:
                ok, why_bad = False, f"end before start {sg}"
                break
            segs.append({"episode": a[0]["episode"], "start": s, "end": e})
        dur = sum(sg["end"] - sg["start"] for sg in segs)
        if ok and not 18 <= dur <= 62:  # 2s grace for shot edges
            ok, why_bad = False, f"duration {dur:.1f}s outside 20-60s"
        if not ok or not segs:
            bad.append({"model_output": p, "reason": why_bad or "no segments"})
            continue
        p.update(segments=segs, duration=round(dur, 2), flags=_checks(eps, segs))
        p["scores"]["total"] = sum(p["scores"].get(x, 0) for x in ("hook", "cliff", "standalone"))
        good.append(p)
    return good, bad


def _checks(eps, segs):
    """Same rule checks as rules mode, used as a second opinion on the model's picks."""
    by_ep = {e["episode"]: e for e in eps}
    flags = []
    first, last = segs[0], segs[-1]
    e0, e1 = by_ep[first["episode"]], by_ep[last["episode"]]
    hs, _ = hook_score(e0["blocks"], first["start"])
    cs, _ = cliff_score(e1["blocks"], last["end"], e1["duration"])
    if hs <= 0:
        flags.append("rules disagree: weak first 3s")
    if cs <= 0:
        flags.append("rules disagree: soft ending")
    for sg in segs:
        _, f = standalone_score(by_ep[sg["episode"]]["blocks"], sg["start"], sg["end"])
        flags += [x for x in f if x == "cuts into a line"]
    return flags


def rank(promos, **kw):
    items = "\n".join(f'{p["promo_id"]}: {p["hook"]} -> {p["cliffhanger"]} ({p["why"]})' for p in promos)
    out = chat_json(RANK.format(items=items), **kw)
    return out.get("ranking", [])


def run(show, chunk=3, k=4, log=print, **kw):
    promos, rejected = [], []
    for i in range(0, len(show), chunk):
        eps = show[i:i + chunk]
        log(f"LLM reading episodes {eps[0]['episode']}-{eps[-1]['episode']}...")
        try:
            g, b = propose(eps, k=k, **kw)
        except Exception as ex:  # keep going; record the failure honestly
            g, b = [], [{"reason": f"call failed: {ex}", "episodes": [e["episode"] for e in eps]}]
        promos += g
        rejected += b
    for n, p in enumerate(promos, 1):
        p["promo_id"] = f"P{n:03d}"
    ranking = rank(promos, **kw) if promos else []
    return promos, rejected, ranking
