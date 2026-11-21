"""Rules mode: finds and scores promos with simple word rules. No AI, free, runs anywhere.
Score = hook (first 3s) + cliffhanger (last 6s) + makes-sense-alone, for every legal start/end pair."""
import re
from parse import fmt

HOT_EMO = {"furious", "screaming", "shouting", "cruel", "venomous", "threatening", "mocking", "shocked",
           "desperate", "sobbing", "accusatory", "taunting", "spiteful", "scornful", "incredulous", "enraged",
           "cold", "menacing", "hysterical", "outraged", "contemptuous", "smug", "defiant", "commanding",
           "fierce", "vicious", "horrified", "panicked", "weeping", "deadly", "icy", "livid", "snarl"}
HIT = re.compile(r"\b(slap|strik|punch|grab|shov|kneel|collaps|blood|kiss|gasp|scream|rip|throw|threw|slam|"
                 r"sword|knife|dagger|pistol|gun|chok|faint|crash|shatter|reveal|unmask|pregnan|poison|"
                 r"stab|seiz|drag|arrest|burn|fire|tear[s ]|sob|fall|fell|lunge|bleed|wound|scar)", re.I)
CLIFF_FX = re.compile(r"(cliffhanger|ominous|cut to black|freeze|sting|stunned|swell|silence|smash cut|thunder)", re.I)
THREAT = re.compile(r"\b(never|dare|kill|destroy|ruin|secret|truth|who are you|regret|pay for|die|dead|"
                    r"divorce|leave|mine|lie|lied|betray|prove|marry|wife|husband|duke)\b", re.I)
CALM = re.compile(r"\b(gentle|fading out|tender|smil|relief|relieved|embrace|laugh|peaceful|thank|warm|content|hug)", re.I)
SOFT_START = re.compile(r"^(and|but|yes|no|so|then|because|\.\.\.|well)\b", re.I)


def _emo_hot(b):
    return any(w.strip().lower() in HOT_EMO for w in re.split(r"[,/ ]+", b["emotion"]))


def _window(blocks, s, e):
    return [b for b in blocks if b["start"] < e and b["end"] > s]


def hook_score(blocks, s):
    first = [b for b in blocks if s <= b["start"] < s + 3.0] + [b for b in blocks if b["start"] < s < b["end"] and b["kind"] != "dialogue"]
    sc, why = 0.0, ""
    for b in first:
        if b["kind"] == "dialogue":
            sc += 1.0 + 2.0 * _emo_hot(b) + (1.0 if b["text"].rstrip().endswith(("!", "?")) else 0)
            sc += 0.5 if len(b["text"].split()) <= 8 else 0
            why = why or f'{b["speaker"]} ({b["emotion"] or "line"}): "{b["text"]}"'
        elif HIT.search(b["text"]):
            sc += 2.0
    if not any(b["kind"] in ("dialogue", "action", "sfx") for b in first):
        sc -= 2.0  # only a camera move in the first 3s: scrollers keep scrolling
    act = next((f'[{b["kind"]}] {b["text"]}' for b in first if b["kind"] != "camera" and HIT.search(b["text"])), "")
    return min(sc, 6.0), why or act or (first[0]["text"] if first else "")  # cap so one busy moment can't dominate


def cliff_score(blocks, e, ep_end):
    last = [b for b in blocks if e - 6.0 < b["end"] <= e + 0.01]
    sc = 3.0 if ep_end - e < 1.0 else 0.0  # the writers built a cliffhanger into every episode ending
    lines = [b for b in last if b["kind"] == "dialogue"]
    if any(CLIFF_FX.search(b["text"]) for b in last if b["kind"] != "dialogue"):
        sc += 1.5
    if lines:
        t = lines[-1]["text"].rstrip()
        sc += 1.5 if t.endswith(("?", "...", "—", "-")) else 0
        sc += 1.0 if THREAT.search(t) else 0
        sc += 0.5 if _emo_hot(lines[-1]) else 0
    if any(HIT.search(b["text"]) for b in last):
        sc += 1.0
    if any(CALM.search(b["text"]) for b in last):
        sc -= 2.0  # warm, resolved ending: not a cliffhanger even if the episode ends here
    why = (lines[-1]["speaker"] + ': "' + lines[-1]["text"] + '"') if lines else (last[-1]["text"] if last else "")
    return min(sc, 6.0), why


def standalone_score(blocks, s, e):
    win = _window(blocks, s, e)
    lines = [b for b in win if b["kind"] == "dialogue"]
    speakers = {b["speaker"].replace("LADY ", "") for b in lines}
    sc, flags = 0.0, []
    if len(speakers) > 4:
        sc -= len(speakers) - 4
        flags.append(f"{len(speakers)} speakers")
    talk = sum(min(b["end"], e) - max(b["start"], s) for b in lines) / (e - s)
    if talk < 0.25:
        sc -= 1.5
        flags.append("mostly visual, little dialogue")
    prev = [b for b in blocks if b["kind"] == "dialogue" and b["end"] <= s + 0.05]
    reply = lines and prev and s - prev[-1]["end"] < 2.0 and prev[-1]["speaker"] != lines[0]["speaker"]
    if lines and (SOFT_START.match(lines[0]["text"]) or reply):
        sc -= 1.0
        flags.append("opens mid-conversation")
    if any(b["kind"] == "dialogue" and b["start"] < s < b["end"] - 0.2 for b in blocks):
        sc -= 3.0
        flags.append("cuts into a line")
    return sc, flags


def cut_points(blocks):
    """Legal cut times = shot boundaries that do not slice through a line of dialogue."""
    lines = [b for b in blocks if b["kind"] == "dialogue"]
    ok = lambda t: not any(b["start"] + 0.05 < t < b["end"] - 0.05 for b in lines)
    shots = [b for b in blocks if b["kind"] == "camera"] or blocks
    starts = sorted({b["start"] for b in shots if ok(b["start"])})
    ends = sorted({b["end"] for b in shots if ok(b["end"])})
    return starts, ends


def find_promos(ep, lo=20.0, hi=60.0, per_episode=2):
    blocks, dur = ep["blocks"], ep["duration"]
    starts, ends = cut_points(blocks)
    hooks = {s: hook_score(blocks, s) for s in starts}
    cands = []
    for e in ends:
        cs, cwhy = cliff_score(blocks, e, dur)
        for s in starts:
            if not lo <= e - s <= hi:
                continue
            hs, hwhy = hooks[s]
            ss, flags = standalone_score(blocks, s, e)
            sweet = 0.5 if 30 <= e - s <= 45 else 0.0
            total = 1.2 * hs + 1.0 * cs + 0.8 * ss + sweet
            cands.append({"segments": [{"episode": ep["episode"], "start": s, "end": e}],
                          "hook": hwhy, "cliffhanger": cwhy, "flags": flags,
                          "scores": {"hook": hs, "cliff": cs, "standalone": ss, "total": round(total, 2)}})
    # Two-segment "cold open": the episode's strongest hook moment (4-10s) glued before the run-up to the ending.
    best_h = max(starts, key=lambda s: hooks[s][0], default=None)
    if best_h is not None and dur > 0:
        h_end = min((e for e in ends if 4 <= e - best_h <= 10), default=None)
        if h_end:
            cs, cwhy = cliff_score(blocks, dur, dur)
            for s in starts:
                L = dur - s
                if s > h_end + 2 and lo <= L + (h_end - best_h) <= hi and L >= 15:
                    ss, flags = standalone_score(blocks, s, dur)
                    total = 1.2 * hooks[best_h][0] + cs + 0.8 * ss
                    cands.append({"segments": [{"episode": ep["episode"], "start": best_h, "end": h_end},
                                               {"episode": ep["episode"], "start": s, "end": dur}],
                                  "hook": hooks[best_h][1], "cliffhanger": cwhy, "flags": flags + ["2-part cut: check it flows"],
                                  "scores": {"hook": hooks[best_h][0], "cliff": cs, "standalone": ss,
                                             "total": round(total - 1.5, 2)}})  # penalty: joins are riskier
    cands.sort(key=lambda c: -c["scores"]["total"])
    picked = []
    for c in cands:  # keep the best ones that do not overlap much
        if all(_overlap(c, p) < 0.3 for p in picked):
            picked.append(c)
        if len(picked) == per_episode:
            break
    for p in picked:
        p["why"] = explain(p)
    return picked


def _span(c):
    return {(sg["episode"], round(t, 1)) for sg in c["segments"] for t in _frange(sg["start"], sg["end"])}


def _frange(a, b):
    t = a
    while t < b:
        yield t
        t += 0.5


def _overlap(a, b):
    A, B = _span(a), _span(b)
    return len(A & B) / max(1, min(len(A), len(B)))


def explain(c):
    s = c["scores"]
    parts = ["strong first 3 seconds" if s["hook"] >= 3 else "weak-ish opening"]
    parts.append("ends on the episode's own cliffhanger" if s["cliff"] >= 3 else
                 "ends on an unresolved line" if s["cliff"] >= 1.5 else "soft ending")
    if not c["flags"]:
        parts.append("easy to follow cold")
    return "; ".join(parts) + "."


def describe(c):
    return " + ".join(f'Ep{sg["episode"]} {fmt(sg["start"])}-{fmt(sg["end"])}' for sg in c["segments"])
