import streamlit as st

from utils.page_config import setup_page, end_page
from utils.dashboard_widgets import (
    load_work_orders,
    generate_machine_data,
    show_work_order_kpis,
    show_machine_table,
    show_machine_health_summary,
    show_system_status
)
from utils.navigation import quick_navigation

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="Supervisor Dashboard",
    icon="👨‍💼",
    allowed_roles=[
        "Administrator",
        "Supervisor"
    ],
    subtitle="Maintenance Supervision & Operations"
)

# ==========================================================
# LOAD DATA
# ==========================================================

orders = load_work_orders()
machine_df = generate_machine_data()

# ==========================================================
# WORK ORDER KPI
# ==========================================================

show_work_order_kpis(orders)

st.divider()

# ==========================================================
# LIVE MACHINE STATUS
# ==========================================================

show_machine_table(machine_df)

st.divider()

# ==========================================================
# APPROVAL QUEUE
# ==========================================================

st.subheader("📝 Pending Work Orders")

if orders.empty:

    st.info("No work orders available.")

else:

    pending = orders[
        orders["status"] == "PENDING"
    ]

    if pending.empty:

        st.success("There are no pending work orders.")

    else:

        st.dataframe(
            pending,
            use_container_width=True,
            hide_index=True
        )

st.divider()

# ==========================================================
# APPROVED WORK ORDERS
# ==========================================================

st.subheader("✅ Approved Work Orders")

if orders.empty:

    st.info("No work orders available.")

else:

    approved = orders[
        orders["status"] == "APPROVED"
    ]

    if approved.empty:

        st.info("No approved work orders.")

    else:

        st.dataframe(
            approved,
            use_container_width=True,
            hide_index=True
        )

st.divider()

# ==========================================================
# COMPLETED WORK ORDERS
# ==========================================================

st.subheader("✔ Completed Work Orders")

if orders.empty:

    st.info("No work orders available.")

else:

    completed = orders[
        orders["status"] == "COMPLETED"
    ]

    if completed.empty:

        st.info("No completed work orders.")

    else:

        st.dataframe(
            completed,
            use_container_width=True,
            hide_index=True
        )

st.divider()

# ==========================================================
# WORK ORDER STATUS
# ==========================================================

st.subheader("📈 Work Order Distribution")

if orders.empty:

    st.info("No work order data available.")

else:

    st.bar_chart(
        orders["status"].value_counts()
    )

st.divider()

# ==========================================================
# MACHINE HEALTH
# ==========================================================

show_machine_health_summary(machine_df)

st.divider()

# ==========================================================
# SUPERVISOR NOTES
# ==========================================================

st.subheader("📝 Supervisor Notes")

notes = st.text_area(
    "Observations",
    placeholder="Enter inspection comments, recommendations, approvals, or follow-up actions.",
    height=180
)

if st.button(
    "Save Notes",
    use_container_width=True
):

    if notes.strip():

        st.success(
            "Supervisor notes saved successfully (Demo Mode)."
        )

    else:

        st.warning(
            "Please enter some notes first."
        )

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

quick_navigation(
    prediction=True,
    analytics=True,
    maintenance=True,
    admin=user.get("role") == "Administrator"
)

st.divider()

# ==========================================================
# SESSION INFORMATION
# ==========================================================

st.subheader("👤 Session Information")

left, right = st.columns(2)

with left:

    st.info(f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}
""")

with right:

    st.info("""
**Dashboard:** Supervisor Dashboard

**Auto Refresh:** Every 10 Seconds
""")

st.divider()

# ==========================================================
# SYSTEM STATUS
# ==========================================================

show_system_status(machine_df)

# ==========================================================
# FOOTER
# ==========================================================

end_page()