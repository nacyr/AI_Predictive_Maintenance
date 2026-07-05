import streamlit as st
import pandas as pd

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


# ==========================================================
# BAR CHART
# ==========================================================

def bar_chart(
    data,
    x=None,
    y=None,
    title=None,
    height=400
):
    """
    Display a bar chart.
    Falls back to Streamlit if Plotly is unavailable.
    """

    if data is None or len(data) == 0:
        st.info("No data available.")
        return

    if PLOTLY_AVAILABLE and x and y:

        fig = px.bar(
            data,
            x=x,
            y=y,
            title=title
        )

        fig.update_layout(height=height)

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        if isinstance(data, pd.Series):
            st.bar_chart(data)

        elif y is not None and y in data.columns:

            chart = data.set_index(x)[y] if x else data[y]
            st.bar_chart(chart)

        else:

            st.bar_chart(data)


# ==========================================================
# LINE CHART
# ==========================================================

def line_chart(
    data,
    x=None,
    y=None,
    title=None,
    height=400
):

    if data is None or len(data) == 0:
        st.info("No data available.")
        return

    if PLOTLY_AVAILABLE and x and y:

        fig = px.line(
            data,
            x=x,
            y=y,
            title=title
        )

        fig.update_layout(height=height)

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        if isinstance(data, pd.Series):
            st.line_chart(data)

        elif y is not None and y in data.columns:

            chart = data.set_index(x)[y] if x else data[y]
            st.line_chart(chart)

        else:

            st.line_chart(data)


# ==========================================================
# PIE CHART
# ==========================================================

def pie_chart(
    data,
    names,
    values,
    title=None
):

    if data is None or len(data) == 0:
        st.info("No data available.")
        return

    if PLOTLY_AVAILABLE:

        fig = px.pie(
            data,
            names=names,
            values=values,
            title=title
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.dataframe(data)


# ==========================================================
# STATUS BAR CHART
# ==========================================================

def work_order_status_chart(df):

    if df is None or df.empty:
        st.info("No work orders available.")
        return

    counts = (
        df["status"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "Status",
        "Count"
    ]

    bar_chart(
        counts,
        x="Status",
        y="Count",
        title="Work Order Status"
    )


# ==========================================================
# MACHINE RISK CHART
# ==========================================================

def machine_risk_chart(machine_df):

    if machine_df is None or machine_df.empty:
        st.info("No machine data available.")
        return

    bar_chart(
        machine_df,
        x="Machine",
        y="Failure Risk (%)",
        title="Machine Failure Risk"
    )


# ==========================================================
# DAILY TREND CHART
# ==========================================================

def trend_chart(trend_df):

    if trend_df is None or trend_df.empty:
        st.info("No trend data available.")
        return

    line_chart(
        trend_df,
        x="date",
        y="count",
        title="Daily Work Orders"
    )