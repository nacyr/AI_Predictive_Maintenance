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
    get_work_orders,
    update_work_order_status,
    create_work_order,
    create_work_order_from_prediction
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

st.title("🔧 Engineer Dashboard")

# ==========================================================
# AUTO REFRESH (FIXED KEY)
# ==========================================================

st_autorefresh(
    interval=10000,
    key="engineer_dashboard_refresh"
)

# ==========================================================
# AUTH CHECK
# ==========================================================

if "user" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

if not user:
    st.switch_page("app.py")
    st.stop()

allowed_roles = ["Administrator", "Maintenance Engineer", "Engineer"]

if user["role"] not in allowed_roles:
    st.error("Access Denied")
    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(user, "🔧 Engineer Dashboard", "Diagnostics & Maintenance Center")
show_sidebar(user)

# ==========================================================
# LOAD DATA (SAFE)
# ==========================================================

try:
    orders = get_work_orders()
except Exception:
    orders = pd.DataFrame()

if orders is None:
    orders = pd.DataFrame()

# ==========================================================
# KPI CALCULATIONS (SAFE)
# ==========================================================

if not orders.empty:

    pending = (orders["status"] == "PENDING").sum()
    approved = (orders["status"] == "APPROVED").sum()
    completed = (orders["status"] == "COMPLETED").sum()
    rejected = (orders["status"] == "REJECTED").sum()

else:
    pending = approved = completed = rejected = 0

# ==========================================================
# MACHINE LIST
# ==========================================================

machines = [
    "Pump A1",
    "Compressor B2",
    "Generator C3",
    "Motor D4",
    "Cooling Unit E5"
]

records = []

# ==========================================================
# AI MONITORING
# ==========================================================

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

    # auto work order creation (safe function)
    create_work_order_from_prediction(
        machine=machine,
        risk_score=probability,
        sensor_data=sensor
    )

    records.append({
        "Machine": machine,
        "Temperature (°C)": round(sensor["temperature"], 2),
        "Pressure (bar)": round(sensor["pressure"], 2),
        "Vibration": round(sensor["vibration"], 2),
        "Current (A)": round(sensor["current"], 2),
        "RPM": int(sensor["rpm"]),
        "Health (%)": round((1 - probability) * 100, 1),
        "Risk (%)": round(probability * 100, 2),
        "Status": "🔴 Critical" if probability >= 0.7
                  else "🟡 Warning" if probability >= 0.4
                  else "🟢 Normal"
    })

machine_df = pd.DataFrame(records)

# ==========================================================
# KPI DASHBOARD
# ==========================================================

st.subheader("📊 Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Machines", len(machine_df))
c2.metric("Pending", pending)
c3.metric("Approved", approved)
c4.metric("Completed", completed)

st.divider()

# ==========================================================
# LIVE TABLE (FIXED)
# ==========================================================

st.subheader("📡 Live Diagnostics")

st.dataframe(machine_df, use_container_width=True, hide_index=True)

# ==========================================================
# CRITICAL ALERTS
# ==========================================================

st.subheader("🚨 Critical Machines")

critical_df = machine_df[machine_df["Risk (%)"] >= 70]

if critical_df.empty:
    st.success("No critical machines detected.")
else:
    st.error(f"{len(critical_df)} machine(s) require attention")
    st.dataframe(critical_df, use_container_width=True, hide_index=True)

# ==========================================================
# CREATE WORK ORDER (FIXED KEYS)
# ==========================================================

st.divider()
st.subheader("➕ Create Work Order")

machine_sel = st.selectbox("Machine", machines, key="eng_machine")
issue = st.text_area("Issue", key="eng_issue")
priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"], key="eng_priority")

if st.button("Create Work Order", key="eng_create_btn"):

    if issue.strip():

        create_work_order(
            machine=machine_sel,
            issue=issue,
            priority=priority,
            created_by=user["fullname"]
        )

        st.success("Work order created")
        st.rerun()

    else:
        st.warning("Enter issue description")

# ==========================================================
# UPDATE STATUS (FIXED ID KEY)
# ==========================================================

st.divider()
st.subheader("⚙ Update Work Order")

if not orders.empty:

    order_id = st.selectbox(
        "Work Order ID",
        orders["id"].tolist(),
        key="eng_order_id"
    )

    new_status = st.selectbox(
        "Status",
        ["PENDING", "APPROVED", "IN_PROGRESS", "COMPLETED", "REJECTED"],
        key="eng_status"
    )

    if st.button("Update Status", key="eng_update_btn"):

        update_work_order_status(order_id, new_status)

        st.success("Updated successfully")
        st.rerun()

# ==========================================================
# RECENT WORK ORDERS
# ==========================================================

st.divider()
st.subheader("📋 Recent Work Orders")

if not orders.empty:

    recent = orders.sort_values("id", ascending=False).head(5)

    st.dataframe(recent, use_container_width=True, hide_index=True)

# ==========================================================
# SYSTEM STATUS
# ==========================================================

st.divider()
st.subheader("🟢 System Status")

if not machine_df.empty:

    high_risk = (machine_df["Risk (%)"] >= 70).sum()

    if high_risk == 0:
        st.success("All systems normal")
    elif high_risk <= 2:
        st.warning("Some machines need attention")
    else:
        st.error("Critical maintenance required")

# ==========================================================
# FOOTER
# ==========================================================

show_footer()

st.caption("Engineer Dashboard • AI Predictive Maintenance System")