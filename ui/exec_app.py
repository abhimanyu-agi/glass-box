"""
Executive Safety Operations Dashboard — with dedicated AI workspace.
"""

# --- Path fix ---
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# -----------------

import streamlit as st
import plotly.graph_objects as go

from ui.data import (
    kpi_summary,
    monthly_trend,
    top_states,
    weather_impact,
    city_hotspots,
    available_years,
)
from agent.graph import build_agent
from ui.components.charts import render as render_chart


# ===========================================================================
# Page config — MUST be first Streamlit command
# ===========================================================================
st.set_page_config(
    page_title="Safety Operations",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ===========================================================================
# Cached agent + session state
# ===========================================================================
@st.cache_resource
def get_agent():
    return build_agent()


agent = get_agent()

# Session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "view" not in st.session_state:
    st.session_state.view = "dashboard"     # "dashboard" or "ask_ai"


# ===========================================================================
# Design tokens
# ===========================================================================
COLOR_ACCENT       = "#4f46e5"
COLOR_ACCENT_HOVER = "#4338ca"
COLOR_ACCENT_SOFT  = "#eef2ff"
COLOR_DANGER       = "#dc2626"
COLOR_TEXT_PRIMARY = "#0f172a"
COLOR_TEXT_MUTED   = "#64748b"
COLOR_TEXT_FAINT   = "#94a3b8"
COLOR_BORDER       = "#e2e8f0"
COLOR_BG_CARD      = "#ffffff"
COLOR_BG_PAGE      = "#f8fafc"
CHART_GRID         = "#f1f5f9"


# ===========================================================================
# Global CSS — shared across both views
# ===========================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    .stApp {{ background-color: {COLOR_BG_PAGE}; }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 4rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1440px;
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}

    /* HEADER */
    .exec-title {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {COLOR_TEXT_PRIMARY};
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .exec-subtitle {{
        font-size: 0.875rem;
        color: {COLOR_TEXT_MUTED};
        margin-top: 4px;
        font-weight: 400;
    }}

    /* KPI CARDS */
    div[data-testid="stMetric"] {{
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 1.5rem 1.75rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    div[data-testid="stMetric"]:hover {{
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
        transition: box-shadow 150ms ease;
    }}
    div[data-testid="stMetricLabel"] p {{
        color: {COLOR_TEXT_MUTED} !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.5rem !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }}

    .section-title {{
        font-size: 0.9375rem;
        font-weight: 600;
        color: {COLOR_TEXT_PRIMARY};
        margin: 2rem 0 0.75rem 0;
        letter-spacing: -0.01em;
    }}
    .section-subtitle {{
        font-size: 0.8125rem;
        color: {COLOR_TEXT_MUTED};
        font-weight: 400;
        margin-top: -0.5rem;
        margin-bottom: 1rem;
    }}

    div[data-testid="stPlotlyChart"] {{
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }}

    div[data-testid="stDataFrame"] {{
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }}

    /* PRIMARY BUTTON — "Ask AI" and "Back to Dashboard" */
    button[kind="primary"] {{
        background: {COLOR_ACCENT} !important;
        color: white !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 10px 22px !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
        transition: all 150ms ease !important;
    }}
    button[kind="primary"]:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35) !important;
        background: {COLOR_ACCENT_HOVER} !important;
    }}

    /* SECONDARY BUTTON — starter / follow-up questions */
    button[kind="secondary"] {{
        background: white !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        transition: all 150ms ease !important;
    }}
    button[kind="secondary"]:hover {{
        border-color: {COLOR_ACCENT} !important;
        background: {COLOR_ACCENT_SOFT} !important;
        color: {COLOR_ACCENT} !important;
    }}

    /* AI VIEW — welcome block */
    .ai-welcome {{
        text-align: center;
        padding: 2rem 1rem 1.5rem 1rem;
    }}
    .ai-welcome-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
    }}
    .ai-welcome-title {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {COLOR_TEXT_PRIMARY};
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }}
    .ai-welcome-sub {{
        font-size: 0.95rem;
        color: {COLOR_TEXT_MUTED};
        margin: 0;
    }}

    /* AI VIEW — starter questions section label */
    .starter-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {COLOR_TEXT_FAINT};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 2rem 0 0.75rem 0;
    }}

    /* AI VIEW — chat input styling */
    div[data-testid="stChatInput"] textarea {{
        border-radius: 999px !important;
        border: 1px solid {COLOR_BORDER} !important;
        padding: 0.875rem 1.25rem !important;
        font-size: 0.95rem !important;
    }}

    /* Chat messages — tighten spacing */
    div[data-testid="stChatMessage"] {{
        background: transparent !important;
        padding: 0.5rem 0 !important;
    }}

    /* Section divider */
    .divider {{
        border-bottom: 1px solid {COLOR_BORDER};
        margin: 1.5rem 0;
    }}
</style>
""", unsafe_allow_html=True)


# ===========================================================================
# Formatting helpers
# ===========================================================================
def fmt_big(n) -> str:
    if n is None:
        return "—"
    n = float(n)
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.0f}K"
    return f"{n:,.0f}"


def fmt_pct(n, signed: bool = False) -> str:
    if n is None:
        return "—"
    sign = "+" if signed and n > 0 else ""
    return f"{sign}{n:.1f}%"


def style_chart(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=20, t=10, b=10),
        plot_bgcolor=COLOR_BG_CARD,
        paper_bgcolor=COLOR_BG_CARD,
        font=dict(family="Inter, -apple-system, sans-serif", size=12, color=COLOR_TEXT_PRIMARY),
        xaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(color=COLOR_TEXT_FAINT, size=11)),
        yaxis=dict(gridcolor=CHART_GRID, zeroline=False, showline=False,
                   tickfont=dict(color=COLOR_TEXT_FAINT, size=11)),
        showlegend=False,
        hoverlabel=dict(bgcolor="white", bordercolor=COLOR_BORDER,
                        font=dict(color=COLOR_TEXT_PRIMARY, family="Inter")),
    )
    return fig


# ===========================================================================
# ===========================================================================
# VIEW ROUTER
# ===========================================================================
# ===========================================================================

def render_dashboard_view():
    """Main dashboard — KPIs, charts, table."""
    # --- Header ---
    h_left, h_spacer, h_ask, h_year = st.columns([5, 3, 2, 2])

    with h_left:
        st.markdown(
            """
            <div>
                <p class="exec-title">🛡️ Safety Operations</p>
                <p class="exec-subtitle">US road incidents · Data through March 2023</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with h_ask:
        st.markdown("<div style='padding-top: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("🤖 Ask AI", type="primary", use_container_width=True, key="open_ai"):
            st.session_state.view = "ask_ai"
            st.rerun()

    with h_year:
        st.markdown("<div style='padding-top: 1.25rem;'></div>", unsafe_allow_html=True)
        years = available_years()
        default_year = 2022 if 2022 in years else years[0]
        selected_year = st.selectbox(
            "Year",
            options=years,
            index=years.index(default_year),
            label_visibility="collapsed",
        )

    st.markdown(f'<div class="divider"></div>', unsafe_allow_html=True)

    # --- KPI row ---
    kpis = kpi_summary(selected_year)
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1: st.metric("Total Incidents", fmt_big(kpis["total_incidents"]))
    with k2: st.metric("Severe Incidents", fmt_big(kpis["severe_incidents"]))
    with k3: st.metric("Severity Rate", fmt_pct(kpis["severe_rate_pct"]))
    with k4: st.metric("YoY Change", fmt_pct(kpis["yoy_change_pct"], signed=True))

    # --- Trend ---
    st.markdown('<p class="section-title">Monthly Trend</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Total and severe incidents over the last 24 months</p>', unsafe_allow_html=True)

    trend_df = monthly_trend(months=24)
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_df["incident_month"], y=trend_df["total_incidents"],
        mode="lines", name="Total",
        line=dict(color=COLOR_ACCENT, width=2.5, shape="spline", smoothing=0.4),
        fill="tozeroy", fillcolor="rgba(79, 70, 229, 0.08)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Total: %{y:,}<extra></extra>",
    ))
    fig_trend.add_trace(go.Scatter(
        x=trend_df["incident_month"], y=trend_df["severe_incidents"],
        mode="lines", name="Severe",
        line=dict(color=COLOR_DANGER, width=2.5, shape="spline", smoothing=0.4),
        hovertemplate="<b>%{x|%b %Y}</b><br>Severe: %{y:,}<extra></extra>",
    ))
    fig_trend.update_layout(hovermode="x unified")
    style_chart(fig_trend, height=320)
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

    # --- Two-col: states + weather ---
    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        st.markdown('<p class="section-title">Top 10 States</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Severe incidents, selected year</p>', unsafe_allow_html=True)
        states_df = top_states(selected_year, top_n=10).sort_values("severe_incidents", ascending=True)
        fig_states = go.Figure(go.Bar(
            x=states_df["severe_incidents"], y=states_df["state"], orientation="h",
            marker=dict(color=states_df["severe_incidents"],
                        colorscale=[[0, "#c7d2fe"], [1, COLOR_ACCENT]], line=dict(width=0)),
            text=[f"{v:,}" for v in states_df["severe_incidents"]],
            textposition="outside",
            textfont=dict(size=11, color=COLOR_TEXT_MUTED),
            hovertemplate="<b>%{y}</b><br>%{x:,} severe incidents<extra></extra>",
        ))
        style_chart(fig_states, height=380)
        fig_states.update_xaxes(showticklabels=False)
        st.plotly_chart(fig_states, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.markdown('<p class="section-title">Weather Impact</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Severity rate by weather condition</p>', unsafe_allow_html=True)
        weather_df = weather_impact(selected_year, min_incidents=500, top_n=10).sort_values("severe_rate_pct", ascending=True)
        fig_weather = go.Figure(go.Bar(
            x=weather_df["severe_rate_pct"], y=weather_df["weather_condition"], orientation="h",
            marker=dict(color=weather_df["severe_rate_pct"],
                        colorscale=[[0, "#fecaca"], [1, COLOR_DANGER]], line=dict(width=0)),
            text=[f"{v:.1f}%" for v in weather_df["severe_rate_pct"]],
            textposition="outside",
            textfont=dict(size=11, color=COLOR_TEXT_MUTED),
            hovertemplate="<b>%{y}</b><br>Severity rate: %{x:.2f}%<extra></extra>",
        ))
        style_chart(fig_weather, height=380)
        fig_weather.update_xaxes(showticklabels=False)
        st.plotly_chart(fig_weather, use_container_width=True, config={"displayModeBar": False})

    # --- Hotspots ---
    st.markdown('<p class="section-title">Accident Hotspots</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Top 15 cities by severe incidents</p>', unsafe_allow_html=True)
    cities_df = city_hotspots(selected_year, top_n=15)
    display_df = cities_df.rename(columns={
        "state": "State", "city": "City",
        "total_incidents": "Total", "severe_incidents": "Severe", "critical_incidents": "Critical",
    })
    st.dataframe(
        display_df, use_container_width=True, hide_index=True, height=420,
        column_config={
            "State": st.column_config.TextColumn(width="small"),
            "City": st.column_config.TextColumn(width="medium"),
            "Total": st.column_config.NumberColumn(format="%d"),
            "Severe": st.column_config.NumberColumn(format="%d"),
            "Critical": st.column_config.NumberColumn(format="%d"),
        },
    )

    # --- Footer ---
    st.markdown(
        f"""
        <div style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid {COLOR_BORDER};
             color: {COLOR_TEXT_MUTED}; font-size: 0.8125rem; text-align: center;">
            Powered by Azure OpenAI + PostgreSQL · AI-augmented exec reporting
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------

def render_assistant_reply(state: dict):
    """Narrative + chart inside assistant messages."""
    narrative = state.get("narrative", "")
    chart_type = state.get("chart_type", "table")
    df = state.get("query_result_df")

    st.markdown(narrative)
    if df is not None and len(df) > 0:
        render_chart(df, chart_type)


def render_ai_view():
    """Dedicated AI chat workspace."""
    # --- Header ---
    h_left, h_spacer, h_back = st.columns([6, 4, 2])

    with h_left:
        st.markdown(
            """
            <div>
                <p class="exec-title">🤖 Ask AI</p>
                <p class="exec-subtitle">Your analyst for road safety data · Grounded in live Postgres</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with h_back:
        st.markdown("<div style='padding-top: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("← Back to Dashboard", type="primary", use_container_width=True, key="back_to_dash"):
            st.session_state.view = "dashboard"
            st.rerun()

    st.markdown(f'<div class="divider"></div>', unsafe_allow_html=True)

    # --- Welcome + starters (only when chat is empty) ---
    if not st.session_state.chat_messages:
        st.markdown(
            """
            <div class="ai-welcome">
                <div class="ai-welcome-icon">👋</div>
                <p class="ai-welcome-title">What would you like to explore?</p>
                <p class="ai-welcome-sub">Ask in plain English — I'll pull the numbers and explain.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<p class="starter-label">Popular questions</p>', unsafe_allow_html=True)

        starters = [
            "How many severe incidents happened in 2022?",
            "Top 5 states by severe accidents in 2022",
            "Which weather conditions cause the most severe accidents?",
            "Compare California and Texas severity in 2022",
        ]
        c1, c2 = st.columns(2, gap="medium")
        for i, q in enumerate(starters):
            target = c1 if i % 2 == 0 else c2
            with target:
                if st.button(q, key=f"starter_{i}", use_container_width=True, type="secondary"):
                    st.session_state.pending_question = q
                    st.rerun()

    # --- Chat history ---
    for idx, msg in enumerate(st.session_state.chat_messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                if msg.get("state"):
                    render_assistant_reply(msg["state"])
                else:
                    st.markdown(msg["content"])

                is_latest = idx == len(st.session_state.chat_messages) - 1
                followups = (msg.get("state") or {}).get("suggested_followups", []) or []
                if is_latest and followups:
                    st.markdown(
                        f"<p style='color: {COLOR_TEXT_FAINT}; font-size: 0.75rem; "
                        f"font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; "
                        f"margin: 1.5rem 0 0.5rem 0;'>Continue exploring</p>",
                        unsafe_allow_html=True,
                    )
                    fcols = st.columns(len(followups[:3]), gap="small")
                    for fi, fq in enumerate(followups[:3]):
                        with fcols[fi]:
                            if st.button(fq, key=f"fu_{idx}_{fi}", use_container_width=True, type="secondary"):
                                st.session_state.pending_question = fq
                                st.rerun()

    # --- Input: chat_input anchors to the bottom of the view, which is
    # correct behavior for a chat UI ---
    typed = st.chat_input("Ask about road safety...")
    pending = st.session_state.pending_question
    st.session_state.pending_question = None
    user_question = typed or pending

    if user_question:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_question,
            "state": None,
        })

        history = []
        for prior in st.session_state.chat_messages[:-1][-6:]:
            if prior["role"] == "user":
                history.append({"role": "user", "content": prior["content"]})
            elif prior.get("state"):
                history.append({
                    "role": "assistant",
                    "content": prior["state"].get("narrative", ""),
                })

        with st.spinner("Analyzing..."):
            result = agent.invoke({
                "question": user_question,
                "conversation_history": history,
                "trace": [],
                "total_cost_usd": 0.0,
                "retry_count": 0,
            })

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": result.get("narrative", ""),
            "state": result,
        })
        st.rerun()


# ===========================================================================
# ROUTER
# ===========================================================================
if st.session_state.view == "ask_ai":
    render_ai_view()
else:
    render_dashboard_view()