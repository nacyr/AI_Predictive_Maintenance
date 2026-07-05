import streamlit as st
import pandas as pd


def section_title(title: str):
    st.markdown(f"## {title}")
    st.divider()


def metric_row(*metrics):
    cols = st.columns(len(metrics))

    for i, (label, value) in enumerate(metrics):
        cols[i].metric(label, value)


def dataframe_card(df: pd.DataFrame):
    if df is None or (hasattr(df, "empty") and df.empty):
        st.info("No data available.")
        return

    st.dataframe(df, use_container_width=True, hide_index=True)