import sys
from pathlib import Path

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
    get_work_orders,
    update_work_order_status,
)

from utils.simulator import generate_sensor_data
from ml.predict import predict_failure

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Engineer Dashboard",
    page_icon="🔧",
    layout="wide"
)

st_autorefresh(
    interval=10000,
    key="engineer_dashboard_refresh"
)

# ==========================================================
# SESSION
# ==========================================================

if "user" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "🔧 Engineer Dashboard",
    "Maintenance Diagnostics Center"
)

show_sidebar(user)

# ==========================================================
# LOAD DATA
# ==========================================================

try:
    orders = get_work_orders()
except Exception:
    orders = pd.DataFrame()

# ==========================================================
# KPI
# ==========================================================

st.subheader("📊 Work Order Overview")

total = len(orders)

pending = (
    (orders["status"] == "PENDING").sum()
    if not orders.empty else 0
)

approved = (
    (orders["status"] == "APPROVED").sum()
    if not orders.empty else 0
)

completed = (
    (orders["status"] == "COMPLETED").sum()
    if not orders.empty else 0
)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total", total)
k2.metric("Pending", pending)
k3.metric("Approved", approved)
k4.metric("Completed", completed)

st.divider()

# ==========================================================
# LIVE MACHINE MONITORING
# ==========================================================

machines = [
    "Pump A1",
    "Compressor B2",
    "Generator C3",
    "Motor D4",
    "Cooling Unit E5"
]

records = []

for machine in machines:

    sensor = generate_sensor_data()

    prediction, probability = predict_failure(
        sensor["temperature"],
        sensor["pressure"],
        sensor["vibration"],
        sensor["current"],
        sensor["rpm"],
        sensor["running_hours"]
    )

    records.append({
        "Machine": machine,
        "Temperature (°C)": round(sensor["temperature"], 2),
        "Pressure (bar)": round(sensor["pressure"], 2),
        "Vibration": round(sensor["vibration"], 2),
        "Current (A)": round(sensor["current"], 2),
        "RPM": int(sensor["rpm"]),
        "Prediction": "Failure" if prediction else "Normal",
        "Risk (%)": round(probability * 100, 2)
    })

machine_df = pd.DataFrame(records)

st.subheader("🤖 AI Machine Monitoring")

st.dataframe(
    machine_df,
    width="stretch",
    hide_index=True
)

st.bar_chart(
    machine_df.set_index("Machine")["Risk (%)"]
)

st.divider()

# ==========================================================
# HIGH RISK MACHINES
# ==========================================================

st.subheader("🚨 High Risk Machines")

high_risk = machine_df[
    machine_df["Risk (%)"] >= 70
]

if high_risk.empty:

    st.success("No critical machines detected.")

else:

    st.error(
        f"{len(high_risk)} machine(s) require immediate maintenance."
    )

    st.dataframe(
        high_risk,
        width="stretch",
        hide_index=True
    )

st.divider()

# ==========================================================
# WORK ORDERS
# ==========================================================

st.subheader("📋 Work Orders")

if orders.empty:

    st.info("No work orders available.")

else:

    st.dataframe(
        orders,
        width="stretch",
        hide_index=True
    )

st.divider()

# ==========================================================
# UPDATE STATUS
# ==========================================================

if not orders.empty:

    st.subheader("🛠 Update Work Order Status")

    order_id = st.selectbox(
        "Work Order ID",
        orders["id"].tolist(),
        key="engineer_order"
    )

    new_status = st.selectbox(
        "New Status",
        [
            "PENDING",
            "APPROVED",
            "ASSIGNED",
            "IN_PROGRESS",
            "COMPLETED",
            "REJECTED"
        ],
        key="engineer_status"
    )

    if st.button(
        "Update Status",
        key="engineer_update"
    ):

        update_work_order_status(
            order_id,
            new_status
        )

        st.success("Work order updated successfully.")

        st.rerun()

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

show_footer()