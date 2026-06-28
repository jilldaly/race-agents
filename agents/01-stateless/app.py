"""Single-turn Streamlit UI — the Journalist's Quick Fact-Checker.

Stateless: each question is independent. Shows the answer, any story chart a tool
produced, and the tool trace — so every number is traceable to a deterministic
tool call, not the model.
"""
import streamlit as st

from backend import config
from backend.agent import answer

st.set_page_config(page_title="Cork Marathon Fact-Checker", page_icon="🏃")

# --- Sidebar: what it can answer + honest limits (best-practice disclosure) ---
with st.sidebar:
    st.header("About")
    st.markdown(
        "A **stateless fact-checker** for the **Cork City Marathon** "
        "(Full / Half / 10K, **2024–2026**). It answers one question at a time, "
        "computing every number from code and showing its working."
    )
    st.subheader("Try asking")
    st.markdown(
        "- What % of 2026 marathon finishers were female?\n"
        "- Show the gender split of the 2026 races\n"
        "- Has female participation grown since 2024?\n"
        "- What was the median half-marathon time in 2025?"
    )
    st.subheader("Limitations")
    st.markdown(
        "- **Race finishers only** — excludes volunteers, other distances, and "
        "anyone who didn't finish.\n"
        "- No individual data (names/bibs are never exposed).\n"
        "- No live results — it reads the published 2024–2026 results.\n"
        "- One question at a time — it has **no memory** of earlier questions.\n"
        "- For comprehensive deep-dives, that's the job of the later agents (03/04)."
    )

st.title("Cork City Marathon — quick fact-checker")
st.caption(
    f"Stateless tool-caller · {config.MODEL} · numbers from code · Full / Half / 10K, 2024–2026"
)

if not config.API_KEY:
    st.warning(
        "No `GEMINI_API_KEY` set — copy `.env.example` to `.env` and add your "
        "key to enable the model. (The tools and golden eval run without it.)"
    )

with st.form("ask"):
    question = st.text_input(
        "Ask a question",
        placeholder="e.g. What % of 2026 marathon finishers were female?",
    )
    st.caption("Tip: name a race (Full / Half / 10K) and a year (2024–2026).")
    submitted = st.form_submit_button("Ask", type="primary")

MAX_Q_LEN = 500          # reject over-long questions (token-burn guard)
MAX_Q_PER_SESSION = 30   # soft per-session cap (the Gemini daily quota is the hard ceiling)

if submitted and question:
    if len(question) > MAX_Q_LEN:
        st.warning(f"Please keep questions under {MAX_Q_LEN} characters.")
    elif st.session_state.get("n_asked", 0) >= MAX_Q_PER_SESSION:
        st.warning("You've reached the question limit for this session — refresh to start over.")
    else:
        st.session_state["n_asked"] = st.session_state.get("n_asked", 0) + 1
        try:
            with st.spinner("Thinking…"):
                result = answer(question)
        except Exception:
            # Never surface a traceback to the public; also absorbs transient model 5xx/429s.
            st.error("Something went wrong answering that — please try again in a moment.")
        else:
            st.markdown(f"### {result.answer}")

            # Story charts a tool produced (the model narrated the numbers; here we
            # show the picture). The model only ever saw a relative path + numbers,
            # never the pixels or an absolute path.
            for t in result.trace:
                obs = t.get("observation")
                if isinstance(obs, dict) and obs.get("chart"):
                    st.image(obs["chart"], caption=obs.get("caption"))

            label = f"How I got this — {len(result.trace)} tool call(s), {result.steps} step(s)"
            with st.expander(label):
                if not result.trace:
                    st.write("No tools were called.")
                for t in result.trace:
                    st.code(f"{t['tool']}({t['args']})\n→ {t['observation']}", language="python")
