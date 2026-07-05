import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# OPTIONAL SAFE IMPORT (prevents crash)
try:
    import plotly.express as px
except Exception:
    px = None

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer

from database.work_orders import (
    get_daily_work_order_trends,
    get_machine_failure_frequency,
    get_ai_vs_manual_breakdown
)

st.set_page_config(page_title="Analytics", layout="wide")

st.title("📈 System Analytics")

if "user" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

show_header(user, "Analytics", "System Insights")
show_sidebar(user)

# ==========================================================
# DAILY TRENDS
# ==========================================================

st.subheader("📊 Daily Work Orders")

trends = get_daily_work_order_trends()

if not trends.empty:
    st.line_chart(trends.set_index("date"))
else:
    st.info("No data available")

st.divider()

# ==========================================================
# MACHINE FREQUENCY
# ==========================================================

st.subheader("🔧 Machine Frequency")

freq = get_machine_failure_frequency()

if not freq.empty:
    st.bar_chart(freq.set_index("machine"))
else:
    st.info("No machine data")

st.divider()

# ==========================================================
# AI BREAKDOWN
# ==========================================================

st.subheader("🤖 AI vs Manual")

breakdown = get_ai_vs_manual_breakdown()

if breakdown:
    df = pd.DataFrame({
        "Source": list(breakdown.keys()),
        "Count": list(breakdown.values())
    })

    st.bar_chart(df.set_index("Source"))
else:
    st.info("No AI data")

st.divider()

show_footer()