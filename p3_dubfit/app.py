"""Dub-Fit app. Run: streamlit run app.py"""
import io, tempfile, zipfile, csv
from pathlib import Path
import pandas as pd
import streamlit as st
from parse import load_show
import dubfit

st.set_page_config(page_title="Dub-Fit", layout="wide")
st.title("Dub-Fit: will each dubbed line fit its shot?")
st.caption("Upload a show's screenplays. Translate the lines (or upload a translator's CSV), see which won't fit their time slot, and get shorter versions.")

files = st.file_uploader("Screenplays (.txt or .zip)", type=["txt", "zip"], accept_multiple_files=True)
mode = st.radio("What to do", ["Check original timing (free)", "Check my translation CSV (free)", "Translate + fix with AI"], horizontal=True)
kw, tr_file = {}, None
c1, c2 = st.columns(2)
eps = c1.text_input("Episodes (e.g. 1-5, blank = all)", "1-3")
lang = c2.text_input("Target language", "Hindi")
if mode.startswith("Check my"):
    tr_file = st.file_uploader("Translation CSV with columns id,text", type=["csv"])
if mode.startswith("Translate"):
    a, b, c = st.columns(3)
    kw["provider"] = a.selectbox("Provider", ["gemini", "openai", "anthropic"])
    kw["model"] = b.text_input("Model", {"gemini": "gemini-3.8-flash", "openai": "", "anthropic": "claude-sonnet-5-5"}[kw["provider"]])
    kw["api_key"] = c.text_input("API key", type="password")
    if kw["provider"] == "openai":
        kw["base_url"] = st.text_input("Base URL", "https://api.groq.com/openai/v1")

if files and st.button("Run", type="primary"):
    with tempfile.TemporaryDirectory() as d:
        for f in files:
            if f.name.endswith(".zip"):
                zipfile.ZipFile(io.BytesIO(f.read())).extractall(d)
            else:
                Path(d, f.name).write_bytes(f.read())
        show = load_show(d)
    cal = dubfit.calibrate(dubfit.lines_of(show))
    lines = dubfit.lines_of(show, dubfit.parse_eps(eps))
    st.info(f"Normal pace in this show: {cal['median_rate']} syllables/s. Max comfortable pace (fastest 10% of original lines): {cal['max_rate']} syllables/s.")
    box = st.empty()
    if mode.startswith("Check original"):
        lines = dubfit.source_report(lines, cal)
        st.json(dubfit.room_stats(lines))
    else:
        if tr_file:
            tr = {r["id"]: r["text"] for r in csv.DictReader(io.StringIO(tr_file.getvalue().decode("utf-8-sig")))}
        elif mode.startswith("Translate"):
            tr = dubfit.translate(lines, lang, log=box.info, **kw)
        else:
            st.error("Upload the translation CSV.")
            st.stop()
        lines = dubfit.check(lines, tr, cal, lang, fix=mode.startswith("Translate"), log=box.info, **kw)
        st.json(dubfit.summarize(lines, cal, mode, lang))
    df = pd.DataFrame(lines)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8-sig"), "dubfit_lines.csv")
