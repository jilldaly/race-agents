"""Single-turn Streamlit UI — the Journalist's Quick Fact-Checker.

Stateless: each question is independent. Shows the answer plus the tool trace so
every number is traceable to a deterministic tool call, not the model.
"""
import streamlit as st

from backend import config
from backend.agent import answer

st.set_page_config(page_title="Cork Marathon Fact-Checker", page_icon="🏃")
st.title("Cork City Marathon — quick fact-checker")
st.caption(
    f"Stateless tool-caller · {config.MODEL} · numbers from code · Full / Half / 10K, 2024–2026"
)

if not config.API_KEY:
    st.warning(
        "No `GEMINI_API_KEY` set — copy `.env.example` to `.env` and add your "
        "free-tier key to enable the model. (The tools and golden eval run without it.)"
    )

question = st.text_input(
    "Ask a question",
    placeholder="e.g. What was the female median time in the 2026 marathon?",
)

if st.button("Ask", type="primary") and question:
    with st.spinner("Thinking…"):
        result = answer(question)
    st.markdown(f"### {result.answer}")
    label = f"How I got this — {len(result.trace)} tool call(s), {result.steps} step(s)"
    with st.expander(label):
        if not result.trace:
            st.write("No tools were called.")
        for t in result.trace:
            st.code(f"{t['tool']}({t['args']})\n→ {t['observation']}", language="python")
