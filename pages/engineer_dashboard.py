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
    update_work_order_status
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

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="engineer_dashboard_refresh"
)

# ==========================================================
# LOGIN
# ==========================================================

if "user" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

if user is None:
    st.switch_page("app.py")
    st.stop()

# ==========================================================
# ROLE PERMISSION
# ==========================================================

allowed_roles = [
    "Administrator",
    "Maintenance Engineer",
    "Engineer"
]

if user["role"] not in allowed_roles:
    st.error("Access Denied")
    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "🔧 Engineer Dashboard",
    "Maintenance & Diagnostics Center"
)

show_sidebar(user)

# ==========================================================
# LOAD DATABASE
# ==========================================================

try:
    orders = get_work_orders()
except Exception:
    orders = pd.DataFrame()

# ==========================================================
# WORK ORDER METRICS
# ==========================================================

total_orders = len(orders)

pending = 0
approved = 0
completed = 0
rejected = 0

if not orders.empty:

    pending = (
        orders["status"] == "PENDING"
    ).sum()

    approved = (
        orders["status"] == "APPROVED"
    ).sum()

    completed = (
        orders["status"] == "COMPLETED"
    ).sum()

    rejected = (
        orders["status"] == "REJECTED"
    ).sum()

# ==========================================================
# LIVE AI MACHINE MONITORING
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

    health = round((1 - probability) * 100, 1)

    if probability >= 0.70:
        status = "🔴 Critical"

    elif probability >= 0.40:
        status = "🟡 Warning"

    else:
        status = "🟢 Normal"

    records.append({

        "Machine": machine,

        "Temperature (°C)": round(sensor["temperature"], 2),

        "Pressure (bar)": round(sensor["pressure"], 2),

        "Vibration": round(sensor["vibration"], 2),

        "Current (A)": round(sensor["current"], 2),

        "RPM": int(sensor["rpm"]),

        "Health (%)": health,

        "Failure Risk (%)": round(probability * 100, 2),

        "Status": status

    })

machine_df = pd.DataFrame(records)

# ==========================================================
# KPI DASHBOARD
# ==========================================================

st.subheader("📊 Maintenance Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Machines",
    len(machine_df)
)

k2.metric(
    "Pending Jobs",
    pending
)

k3.metric(
    "Approved Jobs",
    approved
)

k4.metric(
    "Completed",
    completed
)

st.divider()

# ==========================================================
# SECOND KPI ROW
# ==========================================================

critical_count = (
    machine_df["Status"]
    .str.contains("Critical")
    .sum()
)

warning_count = (
    machine_df["Status"]
    .str.contains("Warning")
    .sum()
)

normal_count = (
    machine_df["Status"]
    .str.contains("Normal")
    .sum()
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Normal",
    normal_count
)

c2.metric(
    "Warning",
    warning_count
)

c3.metric(
    "Critical",
    critical_count
)

st.divider()

# ==========================================================
# LIVE MACHINE DIAGNOSTICS
# ==========================================================

st.subheader("🏭 Live Machine Diagnostics")

st.dataframe(
    machine_df,
    width="stretch",
    hide_index=True
)

st.divider()

# ==========================================================
# CRITICAL MACHINES
# ==========================================================

st.subheader("🚨 Critical Machine Alerts")

critical_df = machine_df[
    machine_df["Failure Risk (%)"] >= 70
]

if critical_df.empty:

    st.success("No critical machines detected.")

else:

    st.error(
        f"{len(critical_df)} machine(s) require immediate maintenance."
    )

    st.dataframe(
        critical_df,
        width="stretch",
        hide_index=True
    )

st.divider()
# ==========================================================
# APPROVED WORK ORDERS
# ==========================================================

st.subheader("🛠 Approved Work Orders")

approved_orders = pd.DataFrame()

if orders.empty:

    st.info("No work orders available.")

else:

    approved_orders = orders[
        orders["status"] == "APPROVED"
    ]

    if approved_orders.empty:

        st.info("There are currently no approved work orders.")

    else:

        st.dataframe(
            approved_orders,
            width="stretch",
            hide_index=True
        )

st.divider()

# ==========================================================
# COMPLETE MAINTENANCE
# ==========================================================

if not approved_orders.empty:

    st.subheader("✅ Complete Maintenance")

    selected_order = st.selectbox(
        "Select Work Order ID",
        approved_orders["id"].tolist()
    )

    if st.button(
        "Mark Work Order as Completed",
        width="stretch"
    ):

        update_work_order_status(
            selected_order,
            "COMPLETED"
        )

        st.success("Maintenance work completed successfully.")

        st.rerun()

st.divider()

# ==========================================================
# ALL WORK ORDERS
# ==========================================================

st.subheader("📋 All Work Orders")

if orders.empty:

    st.info("No work orders found.")

else:

    st.dataframe(
        orders,
        width="stretch",
        hide_index=True
    )

st.divider()

# ==========================================================
# WORK ORDER STATUS
# ==========================================================

st.subheader("📊 Work Order Distribution")

if orders.empty:

    st.info("No work order statistics available.")

else:

    st.bar_chart(
        orders["status"].value_counts()
    )

st.divider()

# ==========================================================
# ENGINEER NOTES
# ==========================================================

st.subheader("📝 Maintenance Notes")

notes = st.text_area(
    "Record inspection notes",
    placeholder="Enter maintenance observations...",
    height=180
)

if st.button(
    "💾 Save Notes",
    width="stretch"
):

    if notes.strip():

        st.success(
            "Maintenance notes saved successfully (Demo Mode)."
        )

    else:

        st.warning("Please enter some notes before saving.")

st.divider()

# ==========================================================
# MACHINE HEALTH SUMMARY
# ==========================================================

st.subheader("📈 Machine Health Summary")

avg_health = machine_df["Health (%)"].mean()
avg_risk = machine_df["Failure Risk (%)"].mean()

m1, m2 = st.columns(2)

m1.metric(
    "Average Machine Health",
    f"{avg_health:.1f}%"
)

m2.metric(
    "Average Failure Risk",
    f"{avg_risk:.1f}%"
)

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

st.subheader("⚡ Quick Navigation")

nav1, nav2, nav3, nav4 = st.columns(4)

with nav1:

    if st.button(
        "🤖 AI Prediction",
        width="stretch"
    ):
        st.switch_page("pages/prediction.py")

with nav2:

    if st.button(
        "📈 Analytics",
        width="stretch"
    ):
        st.switch_page("pages/analytics.py")

with nav3:

    if st.button(
        "🛠 Work Orders",
        width="stretch"
    ):
        st.switch_page("pages/maintenance_work_orders.py")

with nav4:

    if st.button(
        "🏠 Admin Dashboard",
        width="stretch"
    ):
        st.switch_page("pages/admin_dashboard.py")

st.divider()

# ==========================================================
# SYSTEM STATUS
# ==========================================================

st.subheader("🟢 System Status")

if critical_count == 0:

    st.success(
        "All monitored equipment is operating within normal limits."
    )

elif critical_count <= 2:

    st.warning(
        f"{critical_count} machine(s) require maintenance attention."
    )

else:

    st.error(
        f"{critical_count} critical machine(s) require immediate intervention."
    )

if warning_count > 0:

    st.info(
        f"{warning_count} machine(s) are currently under observation."
    )

st.divider()

# ==========================================================
# LAST UPDATE
# ==========================================================

st.caption(
    f"Last Updated: {datetime.now().strftime('%d %B %Y %H:%M:%S')}"
)

# ==========================================================
# FOOTER
# ==========================================================

show_footer()