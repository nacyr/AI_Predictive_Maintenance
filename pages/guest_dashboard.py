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

from utils.plant import plant_status
from database.work_orders import get_work_orders

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Guest Dashboard",
    page_icon="👤",
    layout="wide"
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="guest_dashboard_refresh"
)

# ==========================================================
# LOGIN CHECK
# ==========================================================

if "user" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

if user is None:
    st.switch_page("app.py")
    st.stop()

# ==========================================================
# ROLE CHECK
# Administrator can also access this dashboard
# ==========================================================

allowed_roles = [
    "Administrator",
    "Guest"
]

if user["role"] not in allowed_roles:

    st.error("Access Denied")

    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "👤 Guest Dashboard",
    "Industrial AI Predictive Maintenance • Read-Only Monitoring"
)

show_sidebar(user)

# ==========================================================
# LOAD DATA
# ==========================================================

try:
    plants = plant_status()
except Exception:
    plants = pd.DataFrame()

try:
    work_orders = get_work_orders()
except Exception:
    work_orders = pd.DataFrame()

# ==========================================================
# WELCOME
# ==========================================================

st.success(f"Welcome, {user['fullname']}")

st.info(
    "This dashboard provides monitoring and reporting capabilities only. "
    "Guest users cannot modify records or perform maintenance operations."
)

# ==========================================================
# CALCULATE METRICS
# ==========================================================

total_plants = len(plants)
total_orders = len(work_orders)

normal = warning = critical = 0

if not plants.empty:

    status = plants["Status"].astype(str)

    normal = status.str.contains(
        "NORMAL",
        case=False,
        na=False
    ).sum()

    warning = status.str.contains(
        "WARNING",
        case=False,
        na=False
    ).sum()

    critical = status.str.contains(
        "CRITICAL",
        case=False,
        na=False
    ).sum()

pending = approved = completed = rejected = 0

if not work_orders.empty:

    pending = (
        work_orders["status"] == "PENDING"
    ).sum()

    approved = (
        work_orders["status"] == "APPROVED"
    ).sum()

    completed = (
        work_orders["status"] == "COMPLETED"
    ).sum()

    rejected = (
        work_orders["status"] == "REJECTED"
    ).sum()

# ==========================================================
# KPI DASHBOARD
# ==========================================================

st.subheader("📊 Enterprise Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Plants",
    total_plants
)

c2.metric(
    "Work Orders",
    total_orders
)

c3.metric(
    "Normal Assets",
    normal
)

c4.metric(
    "Critical Assets",
    critical
)

st.divider()

# ==========================================================
# WORK ORDER KPIs
# ==========================================================

a1, a2, a3, a4 = st.columns(4)

a1.metric("Pending", pending)
a2.metric("Approved", approved)
a3.metric("Completed", completed)
a4.metric("Rejected", rejected)

st.divider()

# ==========================================================
# PLANT STATUS
# ==========================================================

left, right = st.columns([2, 1])

with left:

    st.subheader("🏭 Live Plant Status")

    if plants.empty:

        st.info("No plant information available.")

    else:

        st.dataframe(
            plants,
            width="stretch",
            hide_index=True
        )

with right:

    st.subheader("📋 Work Order Summary")

    if work_orders.empty:

        st.info("No work orders available.")

    else:

        summary = (
            work_orders["status"]
            .value_counts()
            .reset_index()
        )

        summary.columns = [
            "Status",
            "Count"
        ]

        st.dataframe(
            summary,
            width="stretch",
            hide_index=True
        )

st.divider()
# ==========================================================
# RECENT WORK ORDERS
# ==========================================================

st.subheader("🛠 Recent Maintenance Activities")

if work_orders.empty:

    st.info("No maintenance work orders available.")

else:

    display_orders = work_orders[
        [
            "machine",
            "issue",
            "priority",
            "status",
            "created_at"
        ]
    ]

    st.dataframe(
        display_orders.head(10),
        width="stretch",
        hide_index=True
    )

st.divider()

# ==========================================================
# WORK ORDER STATUS CHART
# ==========================================================

st.subheader("📊 Work Order Distribution")

if work_orders.empty:

    st.info("No statistics available.")

else:

    st.bar_chart(
        work_orders["status"].value_counts()
    )

st.divider()

# ==========================================================
# PLANT HEALTH SUMMARY
# ==========================================================

st.subheader("🏭 Plant Health Summary")

s1, s2, s3 = st.columns(3)

s1.metric(
    "Healthy Assets",
    normal
)

s2.metric(
    "Assets Under Observation",
    warning
)

s3.metric(
    "Critical Assets",
    critical
)

st.divider()

# ==========================================================
# AI MONITORING STATUS
# ==========================================================

st.subheader("🤖 AI Monitoring Status")

if critical == 0:

    st.success(
        "All monitored assets are operating within safe parameters."
    )

elif critical <= 2:

    st.warning(
        f"{critical} critical machine(s) currently require maintenance."
    )

else:

    st.error(
        f"{critical} critical machine(s) require immediate intervention."
    )

if warning > 0:

    st.info(
        f"{warning} machine(s) are currently being monitored closely."
    )

st.divider()

# ==========================================================
# GUEST PERMISSIONS
# ==========================================================

st.subheader("🔒 Access Permissions")

left, right = st.columns(2)

with left:

    st.success("""
✅ View plant status

✅ View AI predictions

✅ View maintenance reports

✅ View work orders

✅ View historical analytics

✅ View dashboards
""")

with right:

    st.error("""
❌ Create work orders

❌ Update work orders

❌ Delete work orders

❌ Manage users

❌ Approve maintenance

❌ Change system settings
""")

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

st.subheader("⚡ Quick Navigation")

q1, q2, q3, q4 = st.columns(4)

with q1:

    if st.button(
        "🤖 AI Prediction",
        width="stretch"
    ):
        st.switch_page("pages/prediction.py")

with q2:

    if st.button(
        "📈 Analytics",
        width="stretch"
    ):
        st.switch_page("pages/analytics.py")

with q3:

    if st.button(
        "🛠 Work Orders",
        width="stretch"
    ):
        st.switch_page("pages/maintenance_work_orders.py")

with q4:

    if st.button(
        "🏠 Admin Dashboard",
        width="stretch"
    ):
        st.switch_page("pages/admin_dashboard.py")

st.divider()

# ==========================================================
# SESSION INFORMATION
# ==========================================================

st.subheader("ℹ️ Session Information")

st.info(
    f"""
Current User: **{user['fullname']}**

Role: **{user['role']}**

Dashboard Refresh: **Every 10 Seconds**

Current Time: **{datetime.now().strftime('%d %b %Y %H:%M:%S')}**
"""
)

st.divider()

# ==========================================================
# SYSTEM STATUS
# ==========================================================

st.subheader("🟢 Overall System Status")

if critical == 0:

    st.success("Industrial monitoring system is operating normally.")

elif critical <= 2:

    st.warning("Some assets require maintenance attention.")

else:

    st.error("Immediate engineering intervention is recommended.")

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

show_footer()