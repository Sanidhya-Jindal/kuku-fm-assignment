"""Dub-Fit web app. Run: streamlit run app.py"""
import io, csv, tempfile, zipfile
from html import escape
from pathlib import Path
import pandas as pd
import streamlit as st
from parse import load_show
import dubfit
from dubfit import syllables
from ui import inject, html, meter

st.set_page_config(page_title="Dub-Fit", page_icon="🎙️", layout="wide", initial_sidebar_state="collapsed")
inject()

LOGO = ('<svg width="26" height="20" viewBox="0 0 26 20" aria-hidden="true"><rect x="1" y="1" width="18" height="18" rx="2" '
        'fill="none" stroke="#14212B" stroke-width="2"/><rect x="5" y="7" width="20" height="6" rx="1.5" fill="#2B45C9"/></svg>')
COLORS = {"fits": "#1E8F62", "ok": "#1E8F62", "fixed": "#2B45C9", "tight": "#C98A12", "too_long": "#CF3F3F",
          "no_room": "#CF3F3F", "missing": "#9AA6AE"}
NAMES = {"fits": "Fits", "ok": "Room to spare", "fixed": "Shortened to fit", "tight": "Tight", "too_long": "Still too long",
         "no_room": "No room left", "missing": "Not translated"}

html(f"""
<nav class="df-nav"><div class="df-mark">{LOGO}Dub-Fit</div>
<div><a href="#try-it">Try it</a><a href="#how-it-works">How it works</a>
<a href="https://github.com/Sanidhya-Jindal/kuku-fm-assignment" target="_blank">GitHub</a></div></nav>
<section class="df-hero"><div>
<h1>Will the dub fit the shot?</h1>
<p>Translated lines often run longer than the original. Dub-Fit checks every line against the time its shot allows, flags the ones that spill over, and rewrites them shorter before any voice is recorded.</p>
</div><div class="df-demo">
<div class="en">Original line, 1.4 second shot<b>Where were you last night?</b></div>
<div class="df-line">कल पूरी रात तुम आखिर कहाँ थे?</div>{meter(1.4, 10, 5.0, "First Hindi draft")}
<div class="df-line">कल रात कहाँ थे?</div>{meter(1.4, 5, 5.0, "Shortened by Dub-Fit")}
</div></section>
""")

html('<div class="df-h2" id="try-it"><h2>Check a show</h2></div><p class="df-lede">Upload the episode scripts as .txt files or one .zip. Nothing is stored after you close the page.</p>')
files = st.file_uploader("Screenplays", type=["txt", "zip"], accept_multiple_files=True, label_visibility="collapsed")
mode = st.radio("What do you want to check?", ["How much room the original timing leaves (free)",
                                               "A translator's file (free)", "Translate and shorten with AI"])
c1, c2 = st.columns(2)
eps = c1.text_input("Episodes", "1-3", help="For example 1-5. Leave empty for the whole show.")
lang = c2.text_input("Language of the dub", "Hindi", disabled=mode.startswith("How"))
kw, tr_file = {}, None
if mode.startswith("A translator"):
    tr_file = st.file_uploader("Translation file: a CSV with columns id and text, where id matches the script, like E001-012", type=["csv"])
if mode.startswith("Translate"):
    a, b = st.columns(2)
    kw["provider"] = a.selectbox("Provider", ["openai", "gemini", "anthropic"], help="openai works with any OpenAI-style server, such as Groq")
    kw["model"] = b.text_input("Model name", {"openai": "", "gemini": "gemini-3.8-flash", "anthropic": "claude-sonnet-5-5"}[kw["provider"]])
    if kw["provider"] == "openai":
        kw["base_url"] = a.text_input("Server address", "https://api.groq.com/openai/v1")
    kw["api_key"] = b.text_input("API key", type="password", help="Used for this run only, never saved")
go = st.button("Check the lines", type="primary", disabled=not files)

if go and files:
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
    cal = dubfit.calibrate(dubfit.lines_of(show))
    lines = dubfit.lines_of(show, dubfit.parse_eps(eps))
    status = st.empty()
    if mode.startswith("How"):
        lines = dubfit.source_report(lines, cal)
        kind = "source"
    else:
        if mode.startswith("A translator"):
            if not tr_file:
                st.error("Add the translation CSV, then check again.")
                st.stop()
            tr = {r["id"]: r["text"] for r in csv.DictReader(io.StringIO(tr_file.getvalue().decode("utf-8-sig")))}
        else:
            try:
                tr = dubfit.translate(lines, lang, log=status.info, **kw)
            except Exception as e:
                st.error(f"The model call failed: {e}. Check the key and model name.")
                st.stop()
        lines = dubfit.check(lines, tr, cal, lang, fix=mode.startswith("Translate"), log=status.info, **kw)
        kind = "dub"
    status.empty()
    st.session_state.out = {"lines": lines, "cal": cal, "kind": kind, "lang": lang}

out = st.session_state.get("out")
if out:
    lines, cal, kind = out["lines"], out["cal"], out["kind"]
    order = ["ok", "tight", "no_room"] if kind == "source" else ["fits", "fixed", "too_long", "missing"]
    counts = {k: sum(l["status"] == k for l in lines) for k in order}
    n = len(lines) or 1
    html('<div class="df-h2"><h2>What we found</h2></div>')
    if kind == "source":
        r = dubfit.room_stats(lines)
        html(f'<p class="df-sum">In {len(lines)} lines, a normal pace is {cal["median_rate"]} syllables a second and the fastest comfortable pace is '
             f'{cal["max_rate"]}. Half the lines could grow by {r["median_room_pct"]}% before a dub stops fitting, but '
             f'{r["lines_with_under_30pct_room"]} of lines have less than 30% room.</p>')
    else:
        html(f'<p class="df-sum">Checked {len(lines)} {escape(out["lang"])} lines against their shots. '
             f'{counts["fits"]} fit as translated, {counts["fixed"]} were shortened to fit, and {counts["too_long"]} still need a human.</p>')
    html('<div class="df-split">' + "".join(f'<div style="width:{100*counts[k]/n:.2f}%;background:{COLORS[k]}">{counts[k] if counts[k]/n > .06 else ""}</div>'
                                            for k in order if counts[k]) + '</div>' +
         '<div class="df-keys">' + "".join(f'<span><i style="background:{COLORS[k]}"></i>{NAMES[k]}: {counts[k]}</span>' for k in order) + '</div>')

    if kind == "source":
        todo = sorted(lines, key=lambda l: l["room_pct"])[:15]
        html('<div class="df-h2"><h2>Tightest lines</h2></div><p class="df-lede">Any longer translation of these will spill past the shot.</p>')
    else:
        todo = sorted([l for l in lines if l["status"] in ("too_long", "fixed")], key=lambda l: (l["status"] != "too_long", -l.get("rate_before", 0)))[:20]
        html('<div class="df-h2"><h2>Lines to review</h2></div><p class="df-lede">Still too long first, then lines Dub-Fit shortened. Check the shortened ones still say the same thing.</p>')
    for l in todo:
        tag = f'<span class="df-tag" style="background:{COLORS[l["status"]]}">{NAMES[l["status"]]}</span>'
        body = f'<p class="df-en">{escape(l["en"])}</p>'
        if kind == "source":
            body += meter(l["slot"], syllables(l["en"]), cal["max_rate"], "Original English")
        else:
            body += f'<div class="df-tr"><small>Translation</small>{escape(l["translation"] or "")}</div>'
            body += meter(l["slot"], syllables(l["translation"] or ""), cal["max_rate"], "As translated")
            if l.get("final") and l["final"] != l["translation"]:
                body += f'<div class="df-tr"><small>Shortened</small>{escape(l["final"])}</div>'
                body += meter(l["slot"], syllables(l["final"]), cal["max_rate"], "After shortening")
        html(f'<div class="df-item"><div class="df-id"><b>{l["id"]}</b><span>Episode {l["episode"]}, {escape(l["speaker"].title())}</span>'
             f'<span>{l["slot"]} s shot</span>{tag}</div><div>{body}</div></div>')

    df = pd.DataFrame(lines)
    with st.expander(f"All {len(lines)} lines"):
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8-sig"), "dubfit_lines.csv")

html("""
<div class="df-h2" id="how-it-works"><h2>How it works</h2></div>
<p class="df-lede">AI translates and rewrites. Plain code measures, so the model never marks its own work.</p>
<div class="df-steps">
<div><b>Measure the shot</b><p>Each line's start and end come straight from the script.</p></div>
<div><b>Set the pace limit</b><p>The fastest 10% of original lines set how fast a dub can comfortably go.</p></div>
<div><b>Translate and check</b><p>Syllables in the dub, divided by the shot length, show what spills over.</p></div>
<div><b>Shorten and re-check</b><p>Long lines get an exact syllable budget, and code checks every rewrite.</p></div>
</div>
<div class="df-foot">Built by Sanidhya Jindal for the Kuku AI Generalist assignment. <a href="https://github.com/Sanidhya-Jindal/kuku-fm-assignment" target="_blank">Source code</a></div>
""")
