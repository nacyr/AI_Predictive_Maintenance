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
    title="Guest Dashboard",
    icon="👤",
    allowed_roles=[
        "Administrator",
        "Guest"
    ],
    subtitle="Industrial Monitoring (Read Only)"
)

# ==========================================================
# LOAD DATA
# ==========================================================

orders = load_work_orders()
machine_df = generate_machine_data()

# ==========================================================
# OVERVIEW
# ==========================================================

st.success(
    f"Welcome, {user.get('fullname', 'Guest')}"
)

st.info(
    "Guest users have read-only access. "
    "You can monitor plant conditions and maintenance activities, "
    "but cannot modify records."
)

# ==========================================================
# KPIs
# ==========================================================

show_work_order_kpis(orders)

st.divider()

# ==========================================================
# LIVE MACHINE STATUS
# ==========================================================

show_machine_table(machine_df)

st.divider()

# ==========================================================
# RECENT WORK ORDERS
# ==========================================================

st.subheader("🛠 Recent Maintenance Activities")

if orders.empty:

    st.info("No work orders available.")

else:

    st.dataframe(
        orders.head(10),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# WORK ORDER DISTRIBUTION
# ==========================================================

st.subheader("📈 Work Order Distribution")

if orders.empty:

    st.info("No statistics available.")

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
# ACCESS PERMISSIONS
# ==========================================================

st.subheader("🔒 Guest Permissions")

left, right = st.columns(2)

with left:

    st.success("""
✅ View AI Monitoring

✅ View Machine Health

✅ View Analytics

✅ View Work Orders

✅ View Reports

✅ View Dashboards
""")

with right:

    st.error("""
❌ Create Work Orders

❌ Update Status

❌ Delete Work Orders

❌ Manage Users

❌ Approve Maintenance

❌ Change Settings
""")

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
# SESSION INFORMATION
# ==========================================================

st.subheader("👤 Session Information")

left, right = st.columns(2)

with left:

    st.info(f"""
**User:** {user.get('fullname', 'Guest')}

**Role:** {user.get('role', 'Guest')}
""")

with right:

    st.info("""
**Dashboard:** Guest Dashboard

**Access Level:** Read Only

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