"""Haq Saathi: a legal help chat for everyday problems in India.  Run: streamlit run app.py"""
import json
import streamlit as st
import lawyer
from kb import TOPICS, CHECKED_ON

st.set_page_config(page_title="Haq Saathi", layout="wide")
st.title("Haq Saathi - legal help for everyday problems")
st.caption(f"Covers: {', '.join(t['title'] for t in TOPICS.values())}. Not a lawyer. Laws checked on {CHECKED_ON}.")

with st.sidebar:
    mode = st.radio("Mode", ["AI (any language, voice)", "Offline (free, English only)"])
    kw = {}
    if mode.startswith("AI"):
        kw["provider"] = st.selectbox("Provider", ["gemini", "openai", "anthropic"])
        kw["model"] = st.text_input("Model", {"gemini": "gemini-3.8-flash", "openai": "", "anthropic": "claude-sonnet-5-5"}[kw["provider"]])
        kw["api_key"] = st.text_input("API key", type="password")
        if kw["provider"] == "openai":
            kw["base_url"] = st.text_input("Base URL", "https://api.groq.com/openai/v1")
    if st.button("Start over"):
        st.session_state.clear()
        st.rerun()
use_llm = mode.startswith("AI")
ss = st.session_state
ss.setdefault("story", [])
ss.setdefault("result", None)
ss.setdefault("practice", [])

talk, prep, practise = st.tabs(["1. Tell your problem", "2. Your case + documents", "3. Practise with the other side"])

with talk:
    for m in ss.story:
        st.chat_message("user").write(m)
    if ss.result:
        st.chat_message("assistant").markdown(ss.result["answer"])
    voice = st.audio_input("Or speak (any language)") if use_llm else None
    msg = st.chat_input("What happened? Write in any language you like.")
    if voice is not None and not msg and ss.get("last_voice") != voice.size:
        from llm import transcribe
        ss.last_voice = voice.size
        try:
            msg = transcribe(voice.getvalue(), **kw)
        except Exception as e:
            st.error(f"Could not read the voice note: {e}")
    if msg:
        ss.story.append(msg)
        with st.spinner("Thinking..."):
            try:
                ss.result = lawyer.run("\n".join(ss.story), use_llm=use_llm, **kw)
            except Exception as e:
                st.error(f"Model call failed ({e}). Switch to Offline mode or check the key.")
        st.rerun()

with prep:
    r = ss.result
    if not r:
        st.info("Tell your problem first.")
    else:
        st.subheader("Your case file")
        c = r["case"]
        st.markdown(f"**Problem type:** {TOPICS.get(r['topic'], {}).get('title', 'Not covered yet')}")
        st.markdown(f"**What happened:** {c.get('what_happened', '')}")
        st.markdown(f"**Amount:** {c.get('amount')}  |  **Other side:** {c.get('other_party')}")
        if c.get("timeline"):
            st.table(c["timeline"])
        st.markdown("**Proof you have:** " + (", ".join(c.get("evidence_have") or []) or "none mentioned"))
        st.markdown("**Proof to collect:** " + ", ".join(c.get("evidence_missing") or []))
        if r["draft"]:
            st.subheader("Draft document (edit before sending)")
            text = st.text_area("Draft", r["draft"], height=420, label_visibility="collapsed")
            st.download_button("Download draft", text, "draft_notice.txt")
        st.subheader("Where each legal fact comes from")
        for s in r["sources"]:
            st.markdown(f"- [{s['id']}] {s['source']}")
        with st.expander("Safety checks on this answer"):
            st.json({k: v for k, v in r["checks"].items() if k != "raw_answer_before_checks"})

with practise:
    r = ss.result
    if not r or r["topic"] not in TOPICS or not use_llm:
        st.info("Needs AI mode and a covered problem. The bot plays your landlord / company / employer so you can rehearse.")
    else:
        for m in ss.practice:
            st.chat_message(m["role"]).write(m["text"])
        p = st.chat_input("Say what you'd say to them", key="practice_in")
        if p:
            hist = [f"{m['role']}: {m['text']}" for m in ss.practice]
            ss.practice.append({"role": "user", "text": p})
            ss.practice.append({"role": "assistant", "text": lawyer.practice(p, hist, r["topic"], r["case"], **kw)})
            st.rerun()
