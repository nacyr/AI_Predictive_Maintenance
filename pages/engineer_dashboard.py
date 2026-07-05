import streamlit as st
import pandas as pd

from utils.page_config import setup_page, end_page
from utils.dashboard_widgets import (
    load_work_orders,
    generate_machine_data,
    show_machine_health_summary
)
from utils.navigation import quick_navigation

from utils.simulator import generate_sensor_data
from ml.smart_maintenance_engine import predict_failure

from database.work_orders import update_work_order_status

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="Engineer Dashboard",
    icon="👷",
    allowed_roles=[
        "Administrator",
        "Maintenance Engineer",
        "Operations Engineer"
    ],
    subtitle="Task Execution & Diagnostics"
)

# ==========================================================
# LOAD DATA
# ==========================================================

orders = load_work_orders()

# Safe fallback
if orders is None:
    orders = pd.DataFrame()

# ==========================================================
# FILTER: ONLY ASSIGNED TO ENGINEER (SIMPLIFIED)
# ==========================================================

engineer_name = user.get("fullname", "")

if not orders.empty and "assigned_to" in orders.columns:
    my_tasks = orders[
        orders["assigned_to"].fillna("") == engineer_name
    ]
else:
    my_tasks = pd.DataFrame()

# ==========================================================
# KPI SECTION
# ==========================================================

st.subheader("📊 My Work Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Assigned Tasks", len(my_tasks))

if not my_tasks.empty:
    col2.metric("Pending", (my_tasks["status"] == "PENDING").sum())
    col3.metric("Completed", (my_tasks["status"] == "COMPLETED").sum())
else:
    col2.metric("Pending", 0)
    col3.metric("Completed", 0)

st.divider()

# ==========================================================
# MY WORK ORDERS
# ==========================================================

st.subheader("🛠 My Assigned Work Orders")

if my_tasks.empty:
    st.info("No assigned work orders.")
else:
    st.dataframe(
        my_tasks,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# UPDATE STATUS (ENGINEER ACTION ONLY)
# ==========================================================

st.subheader("⚙ Update Task Status")

if not my_tasks.empty:

    task_id = st.selectbox(
        "Select Task",
        my_tasks["id"].tolist()
    )

    new_status = st.selectbox(
        "Update Status",
        ["PENDING", "IN_PROGRESS", "COMPLETED"]
    )

    if st.button("Update Task", use_container_width=True):

        update_work_order_status(task_id, new_status)

        st.success("Task updated successfully.")
        st.rerun()

else:
    st.info("No tasks to update.")

st.divider()

# ==========================================================
# LIVE MACHINE DIAGNOSTICS (READ ONLY)
# ==========================================================

st.subheader("🤖 Machine Diagnostics (Read Only)")

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
        "Temp": round(sensor["temperature"], 2),
        "Pressure": round(sensor["pressure"], 2),
        "Vibration": round(sensor["vibration"], 2),
        "Risk (%)": round(risk * 100, 2)
    })

df = pd.DataFrame(records)

st.dataframe(df, use_container_width=True, hide_index=True)

st.bar_chart(df.set_index("Machine")["Risk (%)"])

st.divider()

# ==========================================================
# MACHINE HEALTH SUMMARY
# ==========================================================

show_machine_health_summary(df)

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

quick_navigation(
    prediction=True,
    analytics=True,
    maintenance=False,
    admin=user.get("role") == "Administrator"
)

st.divider()

# ==========================================================
# SESSION INFO
# ==========================================================

st.subheader("👤 Session Info")

st.info(f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}

**Mode:** Execution Only
""")

# ==========================================================
# FOOTER
# ==========================================================

end_page()