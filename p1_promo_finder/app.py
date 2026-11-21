"""Promo Finder web app. Run: streamlit run app.py"""
import io, json, tempfile, zipfile
from html import escape
from pathlib import Path
import pandas as pd
import streamlit as st
from parse import load_show, fmt
from rules import describe
from run import analyze
from ui import inject, html

st.set_page_config(page_title="Promo Finder", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")
inject()

PHONE = """
<svg class="pf-phone" width="230" height="400" viewBox="0 0 230 400" role="img" aria-label="A vertical promo: hook at the start, cliffhanger at the cut">
<rect x="20" y="4" width="190" height="372" rx="28" fill="#3B1B34" stroke="#5A3150" stroke-width="2"/>
<rect x="34" y="22" width="162" height="290" rx="14" fill="#1E0C1A"/>
<rect x="48" y="40" width="96" height="10" rx="5" fill="#CC2E64"/>
<rect x="48" y="58" width="70" height="8" rx="4" fill="#5A3150"/>
<rect x="48" y="240" width="134" height="8" rx="4" fill="#5A3150"/>
<rect x="48" y="256" width="110" height="8" rx="4" fill="#5A3150"/>
<rect x="48" y="282" width="80" height="10" rx="5" fill="#12867F"/>
<line x1="44" y1="340" x2="186" y2="340" stroke="#5A3150" stroke-width="4" stroke-linecap="round"/>
<rect x="70" y="333" width="88" height="14" rx="4" fill="#E9DDE8"/>
<rect x="68" y="326" width="4" height="28" rx="2" fill="#CC2E64"/>
<rect x="156" y="326" width="4" height="28" rx="2" fill="#12867F"/>
<text x="70" y="370" fill="#E3D3E0" font-size="11" font-family="Schibsted, sans-serif">0:00</text>
<text x="137" y="370" fill="#E3D3E0" font-size="11" font-family="Schibsted, sans-serif">0:42</text>
</svg>"""

html(f"""
<div class="pf-band">
  <nav class="pf-nav"><div class="pf-mark"><span></span>Promo Finder</div>
  <div><a href="#try-it">Try it</a><a href="#how-it-works">How it works</a>
  <a href="https://github.com/Sanidhya-Jindal/kuku-fm-assignment" target="_blank">GitHub</a></div></nav>
  <section class="pf-hero"><div>
    <h1>Find the forty seconds that sell your show.</h1>
    <p>Drop in a microdrama's screenplays. Promo Finder reads every episode and returns ready-to-cut promos for Reels, TikTok and Shorts, ranked by which to post first.</p>
    <div class="pf-legend"><span><i style="background:#CC2E64"></i>Opens on a hook</span><span><i style="background:#12867F"></i>Cuts on a cliffhanger</span></div>
  </div>{PHONE}</section>
</div>
""")

html('<div class="pf-h2" id="try-it"><h2>Find promos in a show</h2></div><p class="pf-lede">Upload the episode scripts as .txt files or one .zip. Nothing is stored after you close the page.</p>')
files = st.file_uploader("Screenplays", type=["txt", "zip"], accept_multiple_files=True, label_visibility="collapsed")
c1, c2 = st.columns([1, 1])
mode = c1.radio("How should it read the scripts?", ["Rules: free and instant", "AI: deeper judgement, needs a key"])
kw = {}
if mode.startswith("AI"):
    kw["provider"] = c2.selectbox("Provider", ["openai", "gemini", "anthropic"], help="openai works with any OpenAI-style server, such as Groq")
    kw["model"] = c2.text_input("Model name", {"openai": "", "gemini": "gemini-3.8-flash", "anthropic": "claude-sonnet-5-5"}[kw["provider"]])
    if kw["provider"] == "openai":
        kw["base_url"] = c2.text_input("Server address", "https://api.groq.com/openai/v1")
    kw["api_key"] = c2.text_input("API key", type="password", help="Used for this run only, never saved")
run = st.button("Find promos", type="primary", disabled=not files)

if run and files:
    with tempfile.TemporaryDirectory() as d:
        for f in files:
            if f.name.endswith(".zip"):
                zipfile.ZipFile(io.BytesIO(f.read())).extractall(d)
            else:
                Path(d, f.name).write_bytes(f.read())
        show = load_show(d)
    if not show:
        st.error("No episodes found. Upload .txt screenplays, or a .zip that contains them.")
        st.stop()
    status = st.empty()
    try:
        res = analyze(show, "llm" if mode.startswith("AI") else "rules", log=lambda m: status.info(m), **kw)
    except Exception as e:
        status.error(f"The model call failed: {e}. Check the key and model name, or switch to Rules.")
        st.stop()
    status.empty()
    st.session_state.result, st.session_state.durations = res, {e["episode"]: e["duration"] for e in show}

res = st.session_state.get("result")
if res:
    dur = st.session_state.durations
    q, ps = res["qa"], res["promos"]
    lo, hi = q["duration_min_max"]
    html(f'<div class="pf-h2"><h2>Post these first</h2></div><p class="pf-summary">Read <b>{q["episodes_in"]} episodes</b> and found '
         f'<b>{q["promos_out"]} promos</b>, every one between {lo:.0f} and {hi:.0f} seconds. '
         f'{q["promos_with_warning_flags"]} carry a note worth checking before you cut.</p>')
    for p in ps[:10]:
        segs = p["segments"]
        ep = segs[0]["episode"]
        total = dur.get(ep, max(s["end"] for s in segs)) or 1
        bars = "".join(f'<div class="cut" style="left:{100*s["start"]/total:.2f}%;width:{100*(s["end"]-s["start"])/total:.2f}%"></div>'
                       for s in segs if s["episode"] == ep)
        h = 100 * segs[0]["start"] / total
        c = 100 * min(segs[-1]["end"], total) / total
        where = " then ".join(f'episode {s["episode"]}, {fmt(s["start"])} to {fmt(s["end"])}' for s in segs)
        chips = "".join(f'<span class="pf-chip">Check: {escape(f)}</span>' for f in p.get("flags", []))
        reason = f'<p class="pf-why"><b>Why post it early:</b> {escape(p["rank_reason"])}</p>' if p.get("rank_reason") else ""
        html(f"""<div class="pf-row"><div class="pf-rank">{p["rank"]}</div><div>
        <h3>Episode {ep}{" (two-part cut)" if len(segs) > 1 else ""}, {p["duration"]:.0f} seconds</h3>
        <div class="pf-meta">Cut {where}.</div>
        <div class="pf-tl"><div class="ep"></div>{bars}<div class="h" style="left:{h:.2f}%"></div><div class="c" style="left:calc({c:.2f}% - 4px)"></div></div>
        <div class="pf-scale"><span>Episode start</span><span>Episode end, {fmt(total)}</span></div>
        <div class="pf-pair"><div class="pf-q"><small>Opens on</small><div>{escape(p["hook"])}</div></div>
        <div class="pf-q c"><small>Cuts on</small><div>{escape(p["cliffhanger"])}</div></div></div>
        <p class="pf-why"><b>Why it works:</b> {escape(p["why"])}</p>{reason}{chips}</div></div>""")

    df = pd.DataFrame([{"Rank": p["rank"], "Cut": describe(p), "Seconds": p["duration"], "Opens on": p["hook"],
                        "Cuts on": p["cliffhanger"], "Why it works": p["why"], "Score": p["scores"]["total"],
                        "Check": "; ".join(p.get("flags", []))} for p in ps])
    with st.expander(f"All {len(ps)} promos and automatic checks"):
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.json(res["qa"])
    d1, d2, _ = st.columns([1, 1, 3])
    d1.download_button("Download CSV", df.to_csv(index=False), "promos.csv")
    d2.download_button("Download JSON", json.dumps(res, indent=2, ensure_ascii=False), "promos.json")

html("""
<div class="pf-h2" id="how-it-works"><h2>How it works</h2></div>
<p class="pf-lede">AI reads the story. Plain code handles everything that has to be exact.</p>
<div class="pf-steps">
<div><b>Read</b><p>Each script becomes timed lines of dialogue, action, camera and sound.</p></div>
<div><b>Find</b><p>Every start and end point is scored for the first 3 seconds, the last moment, and whether a stranger can follow.</p></div>
<div><b>Check</b><p>Cuts never slice a line, stay within 20 to 60 seconds, and AI picks are re-checked by the rules.</p></div>
<div><b>Rank</b><p>Strongest first, leaning to early episodes so new viewers aren't spoiled.</p></div>
</div>
<div class="pf-foot">Built by Sanidhya Jindal for the Kuku AI Generalist assignment. <a href="https://github.com/Sanidhya-Jindal/kuku-fm-assignment" target="_blank">Source code</a></div>
""")
