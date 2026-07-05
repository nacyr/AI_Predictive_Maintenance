import streamlit as st
import pandas as pd


# ==========================================================
# SECTION TITLE
# ==========================================================

def section_title(title: str):
    st.markdown(f"## {title}")
    st.divider()


# ==========================================================
# METRIC ROW
# ==========================================================

def metric_row(*metrics):
    """
    Usage:
    metric_row(
        ("Total", 10),
        ("Pending", 5)
    )
    """

    cols = st.columns(len(metrics))

    for i, (label, value) in enumerate(metrics):
        cols[i].metric(label, value)


# ==========================================================
# DATAFRAME CARD
# ==========================================================

def dataframe_card(df: pd.DataFrame):

    if df is None or (hasattr(df, "empty") and df.empty):
        st.info("No data available.")
        return

    st.dataframe(df, use_container_width=True, hide_index=True)