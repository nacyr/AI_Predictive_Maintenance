import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
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

from database.work_orders import (
    get_all_work_orders,
    assign_work_order,
    change_work_order_status
)

from utils.simulator import generate_sensor_data
from ml.smart_maintenance_engine import predict_failure

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Engineer Dashboard",
    page_icon="🔧",
    layout="wide"
)

st_autorefresh(interval=10000, key="engineer_refresh")

# ==========================================================
# SESSION CHECK
# ==========================================================

if "user" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

# ==========================================================
# HEADER
# ==========================================================

show_header(user, "🔧 Engineer Dashboard", "Diagnostics Center")
show_sidebar(user)

# ==========================================================
# DATA
# ==========================================================

orders = get_all_work_orders()

st.subheader("📊 Work Order Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total", len(orders))
col2.metric("Pending", (orders["status"] == "PENDING").sum() if not orders.empty else 0)
col3.metric("Completed", (orders["status"] == "COMPLETED").sum() if not orders.empty else 0)

st.divider()

# ==========================================================
# LIVE MACHINE MONITORING
# ==========================================================

machines = ["Pump A1", "Compressor B2", "Motor C3"]

records = []

for m in machines:

    sensor = generate_sensor_data()

    _, risk = predict_failure(
        sensor["temperature"],
        sensor["pressure"],
        sensor["vibration"],
        sensor["current"],
        sensor["rpm"],
        sensor["running_hours"]
    )

    records.append({
        "Machine": m,
        "Temp": sensor["temperature"],
        "Pressure": sensor["pressure"],
        "Vibration": sensor["vibration"],
        "Risk (%)": round(risk * 100, 2)
    })

df = pd.DataFrame(records)

st.subheader("🤖 AI Monitoring")
st.dataframe(df, use_container_width=True)

st.bar_chart(df.set_index("Machine")["Risk (%)"])

st.divider()

# ==========================================================
# WORK ORDER UPDATE (FIX DUPLICATE IDS)
# ==========================================================

st.subheader("🛠 Update Work Orders")

if not orders.empty:

    order_id = st.selectbox("Select Work Order", orders["id"].tolist())

    new_status = st.selectbox(
        "Status",
        ["PENDING", "APPROVED", "COMPLETED", "REJECTED"]
    )

    if st.button("Update Status"):

        change_work_order_status(order_id, new_status)
        st.success("Updated successfully")
        st.rerun()

# ==========================================================
# FOOTER
# ==========================================================

show_footer()