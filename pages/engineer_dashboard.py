import streamlit as st
import pandas as pd

from utils.page_config import setup_page, end_page

from utils.simulator import generate_sensor_data

from database.work_orders import (
    get_work_orders,
    update_work_order_status
)

# NOTE:
# We remove ML dependency to avoid import crashes.
# If ML module fails, dashboard still works.

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="🔧 Engineer Dashboard",
    icon="🔧",
    subtitle="Diagnostics & Work Execution Center",
    allowed_roles=[
        "Maintenance Engineer",
        "Administrator",
        "Supervisor"
    ],
)

# ==========================================================
# LOAD WORK ORDERS
# ==========================================================

orders = get_work_orders()

if orders is None or orders.empty:
    orders = pd.DataFrame()

# ==========================================================
# KPI OVERVIEW
# ==========================================================

st.subheader("📊 Work Order Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total", len(orders))
col2.metric("Pending", (orders["status"] == "PENDING").sum() if not orders.empty else 0)
col3.metric("Completed", (orders["status"] == "COMPLETED").sum() if not orders.empty else 0)

st.divider()

# ==========================================================
# MACHINE MONITORING (SIMULATED SAFE MODE)
# ==========================================================

st.subheader("🤖 Live Machine Monitoring (Simulation)")

machines = ["Pump A1", "Compressor B2", "Motor C3"]

records = []

for m in machines:

    sensor = generate_sensor_data()

    # Safe fallback risk calculation (no ML dependency)
    risk = (
        sensor["temperature"] * 0.2 +
        sensor["vibration"] * 0.3 +
        sensor["pressure"] * 0.1
    ) / 100

    records.append({
        "Machine": m,
        "Temperature": sensor["temperature"],
        "Pressure": sensor["pressure"],
        "Vibration": sensor["vibration"],
        "Risk (%)": round(risk * 100, 2)
    })

df = pd.DataFrame(records)

st.dataframe(df, use_container_width=True, hide_index=True)

st.bar_chart(df.set_index("Machine")["Risk (%)"])

st.divider()

# ==========================================================
# WORK ORDER EXECUTION PANEL
# ==========================================================

st.subheader("🛠 Execute Work Orders")

if orders.empty:
    st.info("No work orders available.")
else:

    order_id = st.selectbox(
        "Select Work Order",
        orders["id"].tolist()
    )

    new_status = st.selectbox(
        "Update Status",
        ["IN_PROGRESS", "COMPLETED", "REJECTED"]
    )

    if st.button("Update Status", use_container_width=True):

        update_work_order_status(order_id, new_status)

        st.success("Work order updated successfully.")
        st.rerun()

st.divider()

# ==========================================================
# ASSIGNED WORK ORDERS
# ==========================================================

st.subheader("📋 Assigned Work Orders")

if orders.empty:
    st.info("No assigned work orders.")
else:
    st.dataframe(orders, use_container_width=True, hide_index=True)

st.divider()

# ==========================================================
# SESSION INFO
# ==========================================================

st.subheader("👤 Session Information")

st.info(f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}

**Mode:** Engineer Execution Dashboard
""")

# ==========================================================
# FOOTER
# ==========================================================

end_page()