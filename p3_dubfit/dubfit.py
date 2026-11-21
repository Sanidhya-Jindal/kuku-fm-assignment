"""Dub-Fit: checks whether each translated line can be spoken inside its original time slot,
and asks the model to shorten the ones that cannot.
  python dubfit.py --input scripts/ --mode source                         (free: how tight the original timing is)
  python dubfit.py --input scripts/ --mode llm --lang Hindi --episodes 1-5   (translate + check + fix)
  python dubfit.py --input scripts/ --mode check --translations my.csv     (free: check a translator's file: id,text)"""
import argparse, csv, json, re, statistics, unicodedata
from pathlib import Path
from parse import load_show

VIRAMA = {"्", "্", "੍", "્", "୍", "்", "్", "್", "്"}
SCHWA_DROP = ("ऀ", "৿", "਀", "૿")  # Devanagari, Bengali, Gurmukhi, Gujarati: final 'a' is usually silent


def syllables(text):
    """Rough syllable count. English/Latin: vowel groups. Indic scripts: aksharas (consonant or vowel
    not killed by a virama), minus a silent final 'a' in Hindi-like scripts. Good enough to rank lines."""
    n = 0
    for w in re.findall(r"[^\s.,!?;:\"'()\-\u2014\u2026\u0964\u0965]+", text):  # \w would split Indic words at vowel signs
        if all(ord(c) < 0x900 for c in w):
            w = w.lower()
            k = len(re.findall(r"[aeiouy]+", w))
            if w.endswith("e") and k > 1 and not w.endswith(("le", "ee")):
                k -= 1
            n += max(1, k) if re.search(r"[a-z]", w) else len(re.findall(r"\d", w))
            continue
        aks, bare_end = 0, False
        for i, c in enumerate(w):
            if unicodedata.category(c) == "Lo":
                nxt = w[i + 1] if i + 1 < len(w) else ""
                if nxt in VIRAMA:
                    continue
                aks += 1
                indep_vowel = (ord(c) - 0x900) % 0x80 in range(0x04, 0x15)  # e.g. अ इ ई, not a consonant
                bare_end = (not indep_vowel) and (not nxt or unicodedata.category(nxt) not in ("Mc", "Mn")
                                                  or nxt in "ंঁਂં")  # anusvara keeps it bare
        if aks > 1 and bare_end and SCHWA_DROP[0] <= w[0] <= SCHWA_DROP[3]:
            aks -= 1
        n += aks
    return n


def lines_of(show, episodes=None):
    out = []
    for e in show:
        if episodes and e["episode"] not in episodes:
            continue
        for b in e["blocks"]:
            if b["kind"] == "dialogue" and b["end"] > b["start"]:
                out.append({"id": b["id"], "episode": e["episode"], "speaker": b["speaker"], "emotion": b["emotion"],
                            "slot": round(b["end"] - b["start"], 2), "en": b["text"]})
    return out


def calibrate(lines, pct=0.9):
    """The comfortable max pace = the pace of the fastest 10% of lines in the ORIGINAL show.
    A dubbed line faster than that will sound rushed or spill past its shot."""
    rates = sorted(syllables(l["en"]) / l["slot"] for l in lines)
    return {"median_rate": round(statistics.median(rates), 2), "max_rate": round(rates[int(pct * (len(rates) - 1))], 2)}


def rate(text, slot):
    return round(syllables(text) / slot, 2) if slot else 99.0


TRANSLATE = """Translate these lines from a vertical drama into natural, spoken {lang} for dubbing.
Keep the meaning, emotion and names. It must be speakable in about the same time as the English.
Lines (id | seconds | speaker (emotion) | English):
{rows}
Return JSON: {{"lines": [{{"id": "...", "text": "..."}}]}}"""

SHORTEN = """These {lang} dubbing lines are too long for their time slots. Rewrite each one shorter in natural
spoken {lang}, with AT MOST the syllable budget given. Keep the core meaning and emotion; drop filler, not key information.
(id | slot seconds | syllable budget | current syllables | English | current {lang})
{rows}
Return JSON: {{"lines": [{{"id": "...", "text": "..."}}]}}"""


def translate(lines, lang, batch=30, log=print, **kw):
    from llm import chat_json
    out = {}
    for i in range(0, len(lines), batch):
        chunk = lines[i:i + batch]
        log(f"Translating lines {i + 1}-{i + len(chunk)} of {len(lines)}...")
        rows = "\n".join(f'{l["id"]} | {l["slot"]} | {l["speaker"]} ({l["emotion"]}) | {l["en"]}' for l in chunk)
        try:
            res = chat_json(TRANSLATE.format(lang=lang, rows=rows), **kw)
            out.update({x["id"]: x["text"] for x in res.get("lines", []) if x.get("id")})
        except Exception as e:
            log(f"  batch failed: {e}")
    return out


def check(lines, tr, cal, lang="", fix=False, tries=2, batch=30, log=print, **kw):
    """Marks each line: fits / fixed / too_long / missing. With fix=True the model shortens the long ones
    (30 per call, up to 2 rounds) and code re-checks every rewrite."""
    mx = cal["max_rate"]
    for l in lines:
        t = tr.get(l["id"])
        l["translation"], l["final"], l["status"], l["attempts"] = t, t, ("missing" if not t else None), 0
        if t:
            l["rate_before"] = rate(t, l["slot"])
            l["status"] = "fits" if l["rate_before"] <= mx else "too_long"
    for k in range(tries if fix else 0):
        todo = [l for l in lines if l["status"] == "too_long"]
        if not todo:
            break
        from llm import chat_json
        log(f"Round {k + 1}: shortening {len(todo)} lines...")
        for i in range(0, len(todo), batch):
            chunk = todo[i:i + batch]
            rows = "\n".join(f'{l["id"]} | {l["slot"]} | {max(1, int(mx * l["slot"]))} | {syllables(l["final"])} | '
                             f'{l["en"]} | {l["final"]}' for l in chunk)
            try:
                res = {x["id"]: x["text"] for x in chat_json(SHORTEN.format(lang=lang, rows=rows), **kw).get("lines", [])}
            except Exception as e:
                log(f"  shorten batch failed: {e}")
                continue
            for l in chunk:
                if res.get(l["id"]):
                    l["final"], l["attempts"] = res[l["id"]], k + 1
                    if rate(l["final"], l["slot"]) <= mx:  # code decides, not the model
                        l["status"] = "fixed"
    for l in lines:
        if l.get("final"):
            l["rate_after"] = rate(l["final"], l["slot"])
    return lines


def summarize(lines, cal, mode, lang):
    c = {s: sum(l.get("status") == s for l in lines) for s in ("fits", "fixed", "too_long", "missing")}
    checked = len(lines) - c["missing"]
    before = sum(l.get("rate_before", 0) > cal["max_rate"] for l in lines)
    return {"mode": mode, "language": lang, "lines": len(lines), "calibration": cal, **c,
            "over_slot_before_fix_pct": round(100 * before / checked, 1) if checked else None,
            "over_slot_after_fix_pct": round(100 * c["too_long"] / checked, 1) if checked else None}


def source_report(lines, cal):
    """Free mode: how tight is the original timing? Lines already at max pace leave no room for a longer translation."""
    for l in lines:
        l["rate_en"] = rate(l["en"], l["slot"])
        l["room_pct"] = round(100 * (cal["max_rate"] * l["slot"] / max(1, syllables(l["en"])) - 1))
        l["status"] = ("no_room" if l["room_pct"] <= 0 else "tight" if l["room_pct"] < 20 else "ok")
    return lines


def room_stats(lines):
    """How much LONGER (in syllables) could a translation of each line be before it passes the max pace?"""
    r = sorted(l["room_pct"] for l in lines)
    return {"median_room_pct": r[len(r) // 2],
            **{f"lines_with_under_{k}pct_room": f"{100 * sum(x < k for x in r) / len(r):.0f}%" for k in (10, 20, 30, 50)}}


def write(lines, summary, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    keys = sorted({k for l in lines for k in l}, key=lambda k: list(lines[0]).index(k) if k in lines[0] else 99)
    with open(out / "lines.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(lines)
    bad = [l for l in lines if l.get("status") in ("too_long", "no_room", "fixed")]
    md = [f"# Dub-Fit report ({summary['mode']}{', ' + summary['language'] if summary['language'] else ''})", "",
          "```", json.dumps(summary, indent=1, ensure_ascii=False), "```", "", "## Lines to look at", ""]
    for l in sorted(bad, key=lambda l: -(l.get("rate_before") or l.get("rate_en") or 0))[:40]:
        md.append(f"- **{l['id']}** ({l['slot']}s, {l['status']}) EN: {l['en']}")
        if l.get("translation"):
            md.append(f"  - before: {l['translation']} ({l.get('rate_before')} syl/s)")
            if l["final"] != l["translation"]:
                md.append(f"  - after: {l['final']} ({l.get('rate_after')} syl/s)")
    (out / "report.md").write_text("\n".join(md), encoding="utf-8")


def parse_eps(s):
    if not s:
        return None
    a, _, b = s.partition("-")
    return set(range(int(a), int(b or a) + 1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--mode", choices=["source", "llm", "check"], default="source")
    ap.add_argument("--lang", default="")
    ap.add_argument("--episodes", default="")
    ap.add_argument("--translations", help="CSV with columns id,text (for --mode check)")
    ap.add_argument("--out", default="outputs")
    a = ap.parse_args()
    show = load_show(a.input)
    all_lines = lines_of(show)
    cal = calibrate(all_lines)  # calibrate on the whole show, even when checking a few episodes
    lines = lines_of(show, parse_eps(a.episodes))
    if a.mode == "source":
        lines = source_report(lines, cal)
        c = {s: sum(l["status"] == s for l in lines) for s in ("ok", "tight", "no_room")}
        summary = {"mode": "source", "language": "English (original)", "lines": len(lines), "calibration": cal, **c,
                   "room_for_longer_translation": room_stats(lines),
                   "note": "max_rate is the pace of the fastest 10% of lines in this show, so ~10% are 'no_room' by design."}
        name = "source_english"
    else:
        if a.mode == "check":
            tr = {r["id"]: r["text"] for r in csv.DictReader(open(a.translations, encoding="utf-8-sig"))}
        else:
            tr = translate(lines, a.lang)
        lines = check(lines, tr, cal, a.lang, fix=a.mode == "llm")
        summary = summarize(lines, cal, a.mode, a.lang)
        name = f"{a.mode}_{a.lang or 'translation'}".lower()
    write(lines, summary, Path(a.out) / name)
    print(json.dumps(summary, indent=1, ensure_ascii=False))
