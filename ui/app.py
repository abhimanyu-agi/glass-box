"""Streamlit app — AI Safety Analyst + embedded Superset dashboard."""

# --- Path fix ---
import sys
import os
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# -----------------

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from agent.graph import build_agent
from ui.components.charts import render as render_chart


load_dotenv()


st.set_page_config(
    page_title="Safety Operations AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",   # collapsed by default now; more canvas
)


# ---------------------------------------------------------------------------
# Custom CSS — tighten padding, raise the density a touch for execs
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    .stChatInputContainer {
        padding-bottom: 0.5rem;
    }
    iframe {
        border: 1px solid #e6e6e6;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_agent():
    return build_agent()


agent = get_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------------------------
# Top bar
# ---------------------------------------------------------------------------
header_cols = st.columns([6, 1])
with header_cols[0]:
    st.markdown("### 🛡️  Safety Operations AI")
    st.caption("Ask questions about US road safety data · Dashboard on the right updates independently")
with header_cols[1]:
    if st.button("🔄 New chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("pending_question", None)
        st.rerun()


st.divider()


# ---------------------------------------------------------------------------
# Two-column layout: AI chat on the left, Superset dashboard on the right
# ---------------------------------------------------------------------------
left_col, right_col = st.columns([11, 9])   # roughly 55/45 split


# ==== RIGHT COLUMN: Superset embed ====
with right_col:
    st.markdown("##### 📊 Live Dashboard")
    dashboard_url = os.getenv(
        "SUPERSET_DASHBOARD_URL",
        "http://localhost:8088/superset/dashboard/1/?standalone=3",
    )
    components.iframe(dashboard_url, height=820, scrolling=True)
    st.caption(f"Embedded from Superset · [Open full dashboard]({dashboard_url.replace('?standalone=3', '')})")


# ==== LEFT COLUMN: AI chat ====
with left_col:
    st.markdown("##### 💬 AI Assistant")

    # Starter questions — shown only when chat is empty
    if not st.session_state.messages:
        st.caption("Try asking:")
        starter_questions = [
            "How many severe incidents happened in California in 2022?",
            "Top 5 states by severe accidents last year",
            "Which weather conditions cause the most severe accidents?",
            "Compare California and Texas for night-time incidents",
        ]
        for q in starter_questions:
            if st.button(q, key=f"starter_{hash(q)}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()


    # ----- Message renderer -----
    def render_assistant_message(state: dict, message_idx: int = None):
        narrative = state.get("narrative", "")
        chart_type = state.get("chart_type", "table")
        df = state.get("query_result_df")

        st.markdown(narrative)

        if df is not None and len(df) > 0:
            render_chart(df, chart_type)

        followups = state.get("suggested_followups", []) or []
        is_latest = (message_idx is not None
                     and message_idx == len(st.session_state.messages) - 1)

        if followups and is_latest:
            st.markdown("")
            st.caption("💡 Continue exploring:")
            cols = st.columns(len(followups[:3]))
            for i, q in enumerate(followups[:3]):
                with cols[i]:
                    button_key = f"followup_{message_idx}_{i}"
                    if st.button(q, key=button_key, use_container_width=True):
                        st.session_state.pending_question = q
                        st.rerun()


    # ----- Render chat history -----
    chat_container = st.container()
    with chat_container:
        for idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                if msg["role"] == "user":
                    st.markdown(msg["content"])
                else:
                    if msg.get("state"):
                        render_assistant_message(msg["state"], message_idx=idx)
                    else:
                        st.markdown(msg["content"])


    # ----- Input: typed or queued follow-up -----
    typed_question = st.chat_input("Ask about road safety...")
    pending = st.session_state.pop("pending_question", None)
    user_question = typed_question or pending


    if user_question:
        st.session_state.messages.append({
            "role": "user",
            "content": user_question,
            "state": None,
        })
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_question)

        # Build conversation history for agent context
        history = []
        for prior in st.session_state.messages[:-1][-6:]:
            if prior["role"] == "user":
                history.append({"role": "user", "content": prior["content"]})
            elif prior.get("state"):
                history.append({
                    "role": "assistant",
                    "content": prior["state"].get("narrative", ""),
                })

        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = agent.invoke({
                        "question": user_question,
                        "conversation_history": history,
                        "trace": [],
                        "total_cost_usd": 0.0,
                        "retry_count": 0,
                    })
                render_assistant_message(
                    result,
                    message_idx=len(st.session_state.messages),
                )

        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get("narrative", ""),
            "state": result,
        })
        st.rerun()