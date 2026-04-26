"""
Chart renderers — take a pandas DataFrame + chart_type + context,
and render it cleanly in Streamlit.

Each renderer is defensive: if the DataFrame shape doesn't match
what the chart type expects, we fall back to a table with a note.
"""

import pandas as pd
import streamlit as st
import plotly.express as px


def _safe_first_value(df: pd.DataFrame):
    """Return a best-effort scalar + label for a single-cell result."""
    if df.empty:
        return None, None
    first_row = df.iloc[0]
    # Find the first numeric column for the value
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        return first_row[col], col.replace("_", " ").title()
    # No numeric column — just show the first cell
    return first_row.iloc[0], df.columns[0].replace("_", " ").title()


def render_kpi_card(df: pd.DataFrame, title: str = ""):
    """
    Single big number with optional secondary value.
    Good for 'how many X in Y' questions.
    """
    if df.empty:
        st.info("No data matched this query.")
        return

    value, label = _safe_first_value(df)
    if value is None:
        st.warning("Could not extract a KPI value from the result.")
        st.dataframe(df, use_container_width=True)
        return

    # Format the number nicely
    if isinstance(value, (int, float)):
        if abs(value) >= 1_000_000:
            display = f"{value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            display = f"{value:,.0f}"
        elif isinstance(value, float):
            display = f"{value:.2f}"
        else:
            display = f"{value:,}"
    else:
        display = str(value)

    # Show as a proper metric widget
    st.metric(label=label, value=display)


def render_kpi_delta(df: pd.DataFrame, title: str = ""):
    """
    KPI with a delta/change indicator. Expects a row with value + change columns.
    Falls back to plain KPI if shape doesn't match.
    """
    if df.empty:
        st.info("No data matched this query.")
        return

    # Heuristic: look for a column containing 'pct', 'change', 'delta'
    delta_col = None
    for col in df.columns:
        if any(k in col.lower() for k in ("pct", "change", "delta", "variance")):
            delta_col = col
            break

    value, label = _safe_first_value(df)
    if value is None:
        render_kpi_card(df, title)
        return

    # Format primary value
    if isinstance(value, (int, float)):
        display = f"{value:,.1f}" if isinstance(value, float) else f"{value:,}"
    else:
        display = str(value)

    delta = None
    if delta_col and delta_col in df.columns:
        delta_val = df.iloc[0][delta_col]
        if isinstance(delta_val, (int, float)):
            delta = f"{delta_val:+.1f}%"

    st.metric(label=label, value=display, delta=delta)


def render_bar(df: pd.DataFrame, title: str = ""):
    """
    Horizontal bar chart for rankings. Expects at least one dimension + one numeric.
    """
    if df.empty:
        st.info("No data matched this query.")
        return

    if len(df.columns) < 2:
        st.dataframe(df, use_container_width=True)
        return

    # First non-numeric column = category axis
    cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    if not cat_cols or not num_cols:
        st.dataframe(df, use_container_width=True)
        return

    x_col = cat_cols[0]
    y_col = num_cols[0]

    fig = px.bar(
        df.sort_values(y_col, ascending=True),
        x=y_col,
        y=x_col,
        orientation="h",
        title=title or f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        height=max(300, 40 * len(df)),
        yaxis=dict(categoryorder="total ascending"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_grouped_bar(df: pd.DataFrame, title: str = ""):
    """
    Grouped bars for 2-dimension comparisons (e.g., state × year).
    Expects 2 categorical + 1 numeric column.
    """
    if df.empty or len(df.columns) < 3:
        render_bar(df, title)
        return

    cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    if len(cat_cols) < 2 or not num_cols:
        render_bar(df, title)
        return

    fig = px.bar(
        df, x=cat_cols[0], y=num_cols[0], color=cat_cols[1], barmode="group",
        title=title,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=420)
    st.plotly_chart(fig, use_container_width=True)


def render_line(df: pd.DataFrame, title: str = ""):
    """
    Line chart for time series. First date-like column = x-axis.
    """
    if df.empty:
        st.info("No data matched this query.")
        return

    # Find x-axis (date/datetime column, or something named *_month/*_date/*_year)
    x_col = None
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            x_col = col
            break
    if x_col is None:
        for col in df.columns:
            if any(k in col.lower() for k in ("month", "date", "year", "period")):
                x_col = col
                break
    if x_col is None:
        # Fall back to bar if we can't find a time axis
        render_bar(df, title)
        return

    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not num_cols:
        st.dataframe(df, use_container_width=True)
        return

    # Use ALL numeric columns as lines — this handles multi-series automatically
    fig = px.line(
        df, x=x_col, y=num_cols, markers=True,
        title=title,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=420)
    st.plotly_chart(fig, use_container_width=True)


def render_table(df: pd.DataFrame, title: str = ""):
    """The honest fallback. Also good for questions that genuinely want a list."""
    if df.empty:
        st.info("No data matched this query.")
        return
    if title:
        st.caption(title)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Dispatcher — the single entry point the UI calls
# ---------------------------------------------------------------------------
RENDERERS = {
    "kpi_card": render_kpi_card,
    "kpi_delta": render_kpi_delta,
    "bar": render_bar,
    "grouped_bar": render_grouped_bar,
    "line": render_line,
    "table": render_table,
}


def render(df: pd.DataFrame | None, chart_type: str, title: str = ""):
    """
    Render a DataFrame in Streamlit using the chosen chart type.
    Falls back to table for unknown chart types.
    """
    if df is None or df.empty:
        return  # nothing to render — narrative already explained this

    renderer = RENDERERS.get(chart_type, render_table)
    try:
        renderer(df, title=title)
    except Exception as e:
        # Never let a chart render error break the chat
        st.warning(f"Chart render fell back to table ({e})")
        render_table(df, title=title)