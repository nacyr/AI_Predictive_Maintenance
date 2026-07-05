import sys
from pathlib import Path

import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ==========================================================
# PROJECT ROOT
# ==========================================================

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# ==========================================================
# IMPORTS
# ==========================================================

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Historical Analytics",
    page_icon="📈",
    layout="wide"
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="history_refresh"
)

# ==========================================================
# LOGIN
# ==========================================================

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Please login first.")
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

allowed_roles = [
    "Administrator",
    "Supervisor",
    "Operations Engineer",
    "Maintenance Engineer",
    "Guest"
]

if user["role"] not in allowed_roles:
    st.error("Access Denied")
    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "📈 Historical Analytics",
    "Historical AI Prediction & Maintenance Analytics"
)

show_sidebar(user)

# ==========================================================
# DATABASE
# ==========================================================

db_path = project_root / "database" / "maintenance.db"

try:

    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query(
        "SELECT * FROM predictions ORDER BY timestamp DESC",
        conn
    )

    conn.close()

except Exception:

    df = pd.DataFrame()

# ==========================================================
# NO DATA
# ==========================================================

if df.empty:

    st.warning("No historical prediction data available.")

    show_footer()

    st.stop()

# ==========================================================
# DATA PREPARATION
# ==========================================================

df["timestamp"] = pd.to_datetime(df["timestamp"])

# ==========================================================
# MACHINE FILTER
# ==========================================================

machines = ["All Machines"] + sorted(df["machine"].unique().tolist())

selected_machine = st.selectbox(
    "Select Machine",
    machines
)

if selected_machine != "All Machines":

    df = df[
        df["machine"] == selected_machine
    ]

# ==========================================================
# KPI CARDS
# ==========================================================

avg_health = df["machine_health"].mean()

avg_failure = df["failure_probability"].mean()

avg_remaining = df["remaining_life"].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Prediction Records",
    len(df)
)

c2.metric(
    "Average Health",
    f"{avg_health:.1f}%"
)

c3.metric(
    "Average Failure",
    f"{avg_failure:.1f}%"
)

c4.metric(
    "Remaining Life",
    f"{avg_remaining:.0f} hrs"
)

st.divider()

# ==========================================================
# DATA TABLE
# ==========================================================

st.subheader("📋 Historical Prediction Records")

st.dataframe(
    df,
    width="stretch",
    hide_index=True
)

st.divider()

# ==========================================================
# HEALTH TREND
# ==========================================================

st.subheader("📈 Machine Health Trend")

fig = px.line(

    df,

    x="timestamp",

    y="machine_health",

    color="machine",

    markers=True

)

st.plotly_chart(
    fig,
    width="stretch"
)

# ==========================================================
# FAILURE TREND
# ==========================================================

st.subheader("⚠ Failure Probability Trend")

fig = px.line(

    df,

    x="timestamp",

    y="failure_probability",

    color="machine",

    markers=True

)

st.plotly_chart(
    fig,
    width="stretch"
)

# ==========================================================
# MACHINE COMPARISON
# ==========================================================

st.subheader("🏭 Average Machine Health")

comparison = (

    df.groupby("machine")["machine_health"]

    .mean()

    .reset_index()

)

fig = px.bar(

    comparison,

    x="machine",

    y="machine_health",

    text_auto=".1f"

)

st.plotly_chart(
    fig,
    width="stretch"
)

# ==========================================================
# LATEST AI PREDICTIONS
# ==========================================================

st.subheader("🤖 Latest AI Recommendations")

latest = df[
    [
        "timestamp",
        "machine",
        "failure_probability",
        "remaining_life",
        "recommendation"
    ]
].head(10)

st.dataframe(
    latest,
    width="stretch",
    hide_index=True
)

# ==========================================================
# SYSTEM SUMMARY
# ==========================================================

st.divider()

if avg_failure < 30:

    st.success("Overall equipment health is excellent.")

elif avg_failure < 60:

    st.warning("Some equipment should be monitored closely.")

else:

    st.error("Several machines are approaching failure thresholds.")

# ==========================================================
# FOOTER
# ==========================================================

show_footer()