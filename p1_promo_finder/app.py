"""Streamlit app: upload screenplays, get ranked promos.  Run: streamlit run app.py"""
import io, json, tempfile, zipfile
from pathlib import Path
import pandas as pd
import streamlit as st
from parse import load_show
from rules import describe
from run import analyze

st.set_page_config(page_title="Promo Finder", layout="wide")
st.title("Promo Finder")
st.caption("Upload a show's screenplays (.txt files or one .zip). Get 20-60s promo cuts with hook, cliffhanger and rank.")

files = st.file_uploader("Screenplays", type=["txt", "zip"], accept_multiple_files=True)
mode = st.radio("Mode", ["rules (free, instant)", "llm (needs an API key)"], horizontal=True)
kw = {}
if mode.startswith("llm"):
    c1, c2, c3 = st.columns(3)
    kw["provider"] = c1.selectbox("Provider", ["gemini", "openai", "anthropic"])
    kw["model"] = c2.text_input("Model", {"gemini": "gemini-3.8-flash", "openai": "",
                                          "anthropic": "claude-sonnet-5-5"}[kw["provider"]])
    kw["api_key"] = c3.text_input("API key", type="password")
    if kw["provider"] == "openai":
        kw["base_url"] = st.text_input("Base URL (Groq: https://api.groq.com/openai/v1)", "https://api.openai.com/v1")

if files and st.button("Find promos", type="primary"):
    with tempfile.TemporaryDirectory() as d:
        for f in files:
            if f.name.endswith(".zip"):
                zipfile.ZipFile(io.BytesIO(f.read())).extractall(d)
            else:
                Path(d, f.name).write_bytes(f.read())
        show = load_show(d)
    if not show:
        st.error("No episodes found.")
        st.stop()
    box = st.empty()
    res = analyze(show, mode.split()[0], log=box.info, **kw)
    box.success(f"{len(show)} episodes read, {len(res['promos'])} promos found.")
    st.subheader("Post these first")
    for p in res["promos"][:10]:
        with st.container(border=True):
            st.markdown(f"**#{p['rank']}  {describe(p)}**  ({p['duration']}s, score {p['scores']['total']})")
            st.markdown(f"**Hook:** {p['hook']}  \n**Cliffhanger:** {p['cliffhanger']}  \n**Why:** {p['why']}")
            if p.get("rank_reason"):
                st.markdown(f"**Why post early:** {p['rank_reason']}")
            if p.get("flags"):
                st.warning("Check: " + "; ".join(p["flags"]))
    st.subheader("All promos")
    df = pd.DataFrame([{"rank": p["rank"], "segments": describe(p), "sec": p["duration"], "hook": p["hook"],
                        "cliffhanger": p["cliffhanger"], "why": p["why"], "score": p["scores"]["total"],
                        "flags": "; ".join(p.get("flags", []))} for p in res["promos"]])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.subheader("Automatic checks")
    st.json(res["qa"])
    st.download_button("Download JSON", json.dumps(res, indent=2), "promos.json")
    st.download_button("Download CSV", df.to_csv(index=False), "promos.csv")
