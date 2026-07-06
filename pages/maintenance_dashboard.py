import streamlit as st
import pandas as pd

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation

from database.work_orders import (
    get_work_orders,
    create_work_order,
    update_work_order_status
)

from utils.simulator import generate_sensor_data

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="🛠 Maintenance Dashboard",
    icon="🛠",
    subtitle="Maintenance Control Center",
    allowed_roles=[
        "Administrator",
        "Maintenance Engineer"
    ]
)

# ==========================================================
# LOAD DATA
# ==========================================================

orders = get_work_orders()

if orders is None:
    orders = pd.DataFrame()

# ==========================================================
# MACHINE DATA
# ==========================================================

machines = [
    "Pump A1",
    "Compressor B2",
    "Motor C3"
]

machine_records = []

for machine in machines:

    sensor = generate_sensor_data()

    machine_records.append({
        "Machine": machine,
        "Temperature": sensor["temperature"],
        "Pressure": sensor["pressure"],
        "Vibration": sensor["vibration"],
        "Status": "RUNNING"
    })

machine_df = pd.DataFrame(machine_records)

# ==========================================================
# KPI SECTION
# ==========================================================

st.subheader("📊 Work Order Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Total Orders", len(orders))

c2.metric(
    "Pending",
    (orders["status"] == "PENDING").sum()
    if not orders.empty else 0
)

c3.metric(
    "Completed",
    (orders["status"] == "COMPLETED").sum()
    if not orders.empty else 0
)

st.divider()

# ==========================================================
# MACHINE OVERVIEW
# ==========================================================

st.subheader("🏭 Plant Overview")

st.dataframe(
    machine_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# CREATE WORK ORDER
# ==========================================================

st.subheader("➕ Create Work Order")

col1, col2 = st.columns(2)

with col1:

    machine = st.selectbox(
        "Select Machine",
        machine_df["Machine"].tolist()
    )

with col2:

    priority = st.selectbox(
        "Priority",
        ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    )

issue = st.text_area(
    "Issue Description",
    placeholder="Describe the maintenance issue..."
)

if st.button(
    "Create Work Order",
    use_container_width=True
):

    if issue.strip():

        create_work_order(
            machine=machine,
            issue=issue,
            priority=priority,
            created_by=user.get(
                "fullname",
                "SYSTEM"
            )
        )

        st.success(
            "Work order created successfully."
        )

        st.rerun()

    else:

        st.warning(
            "Please enter an issue description."
        )

st.divider()

# ==========================================================
# WORK ORDERS
# ==========================================================

st.subheader("🧾 Work Orders")

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
# UPDATE STATUS
# ==========================================================

st.subheader("⚙ Update Work Order Status")

if not orders.empty:

    order_id = st.selectbox(
        "Select Work Order",
        orders["id"].tolist()
    )

    new_status = st.selectbox(
        "New Status",
        [
            "PENDING",
            "APPROVED",
            "IN_PROGRESS",
            "COMPLETED",
            "REJECTED"
        ]
    )

    if st.button(
        "Update Status",
        use_container_width=True
    ):

        update_work_order_status(
            order_id,
            new_status
        )

        st.success(
            "Status updated successfully."
        )

        st.rerun()

st.divider()

# ==========================================================
# STATUS DISTRIBUTION
# ==========================================================

st.subheader("📈 Work Order Status Distribution")

if not orders.empty:

    st.bar_chart(
        orders["status"].value_counts()
    )

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