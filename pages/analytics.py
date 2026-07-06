import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ==========================================================
# OPTIONAL PLOTLY IMPORT
# ==========================================================

try:
    import plotly.express as px
except Exception:
    px = None

# ==========================================================
# PROJECT PATH
# ==========================================================

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# ==========================================================
# IMPORTS
# ==========================================================

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer

from database.work_orders import (
    get_daily_work_order_trends,
    get_machine_failure_frequency,
    get_ai_vs_manual_breakdown,
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Analytics",
    page_icon="📈",
    layout="wide"
)

# ==========================================================
# AUTHENTICATION
# ==========================================================

if "user" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

# ==========================================================
# AUTO REFRESH
# ==========================================================

refresh_count = st_autorefresh(
    interval=10_000,
    key="analytics_dashboard_refresh"
)

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "Analytics Dashboard",
    "Enterprise System Insights"
)

show_sidebar(user)

st.success(
    f"""
🟢 LIVE ANALYTICS

Last Updated: {datetime.now().strftime('%d %b %Y %H:%M:%S')}

Refresh Count: {refresh_count}

Update Interval: 10 Seconds
"""
)

st.title("📈 Enterprise Analytics Dashboard")

st.divider()

# ==========================================================
# DAILY WORK ORDER TRENDS
# ==========================================================

st.subheader("📊 Daily Work Order Trends")

trends = get_daily_work_order_trends()

if trends.empty:

    st.info("No daily trend data available.")

else:

    st.line_chart(
        trends.set_index("date")
    )

    st.dataframe(
        trends,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# MACHINE FAILURE FREQUENCY
# ==========================================================

st.subheader("🔧 Machine Failure Frequency")

frequency = get_machine_failure_frequency()

if frequency.empty:

    st.info("No machine statistics available.")

else:

    st.bar_chart(
        frequency.set_index("machine")
    )

    st.dataframe(
        frequency,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# AI VS MANUAL WORK ORDERS
# ==========================================================

st.subheader("🤖 AI vs Manual Work Orders")

breakdown = get_ai_vs_manual_breakdown()

if breakdown:

    ai_df = pd.DataFrame({

        "Source": list(breakdown.keys()),

        "Count": list(breakdown.values())

    })

    st.bar_chart(
        ai_df.set_index("Source")
    )

    st.dataframe(
        ai_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No AI work order data available.")

st.divider()

# ==========================================================
# DASHBOARD STATUS
# ==========================================================

st.subheader("🟢 Dashboard Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Auto Refresh",
        "Enabled"
    )

with col2:
    st.metric(
        "Interval",
        "10 Seconds"
    )

with col3:
    st.metric(
        "Refresh Count",
        refresh_count
    )

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

show_footer()