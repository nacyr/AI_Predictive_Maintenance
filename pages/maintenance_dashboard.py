import streamlit as st
import pandas as pd

from utils.page_config import setup_page, end_page
from utils.dashboard_widgets import (
    load_work_orders,
    generate_machine_data,
    show_work_order_kpis,
    show_machine_table
)
from utils.navigation import quick_navigation

from database.work_orders import (
    create_work_order,
    update_work_order_status
)

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="Maintenance Dashboard",
    icon="🛠",
    allowed_roles=[
        "Administrator",
        "Maintenance Engineer"
    ],
    subtitle="Maintenance Control Center"
)

# ==========================================================
# LOAD DATA
# ==========================================================

orders = load_work_orders()
machines = generate_machine_data()

# ==========================================================
# KPI SECTION
# ==========================================================

show_work_order_kpis(orders)

st.divider()

# ==========================================================
# PLANT OVERVIEW (READ ONLY)
# ==========================================================

st.subheader("🏭 Plant Overview")

show_machine_table(machines)

st.divider()

# ==========================================================
# WORK ORDER CREATION (CORE FUNCTION)
# ==========================================================

st.subheader("➕ Create Work Order")

col1, col2 = st.columns(2)

with col1:

    machine = st.selectbox(
        "Select Machine",
        machines["Machine"].tolist() if not machines.empty else []
    )

with col2:

    priority = st.selectbox(
        "Priority",
        ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    )

issue = st.text_area(
    "Issue Description",
    placeholder="Describe the maintenance problem..."
)

if st.button("Create Work Order", use_container_width=True):

    if machine and issue.strip():

        create_work_order(
            machine=machine,
            issue=issue,
            priority=priority,
            created_by=user.get("fullname", "SYSTEM")
        )

        st.success("Work order created successfully.")
        st.rerun()

    else:
        st.warning("Please complete all fields.")

st.divider()

# ==========================================================
# WORK ORDER MANAGEMENT
# ==========================================================

st.subheader("🧾 Work Order Management")

if orders.empty:

    st.info("No work orders available.")

else:

    st.dataframe(
        orders,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# STATUS UPDATE (CONTROL ONLY)
# ==========================================================

st.subheader("⚙ Update Work Order Status")

if not orders.empty:

    order_id = st.selectbox(
        "Select Work Order",
        orders["id"].tolist()
    )

    new_status = st.selectbox(
        "New Status",
        ["PENDING", "APPROVED", "IN_PROGRESS", "COMPLETED", "REJECTED"]
    )

    if st.button("Update Status", use_container_width=True):

        update_work_order_status(order_id, new_status)

        st.success("Status updated successfully.")
        st.rerun()

st.divider()

# ==========================================================
# SUMMARY VIEW
# ==========================================================

st.subheader("📊 Work Order Status Distribution")

if not orders.empty:
    st.bar_chart(orders["status"].value_counts())
else:
    st.info("No data available.")

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

st.subheader("👤 Session Information")

st.info(f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}

**Mode:** Maintenance Control Center
""")

# ==========================================================
# FOOTER
# ==========================================================

end_page()