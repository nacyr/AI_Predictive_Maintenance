import sys
from pathlib import Path

import streamlit as st
import pandas as pd
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
    get_all_work_orders,
    change_work_order_status,
    delete_work_order
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Maintenance Work Orders",
    page_icon="🛠",
    layout="wide"
)

st_autorefresh(interval=10000, key="work_orders_refresh")

# ==========================================================
# LOGIN CHECK
# ==========================================================

if "user" not in st.session_state:
    st.warning("Please login first.")
    st.switch_page("app.py")
    st.stop()

user = st.session_state.get("user", {})

if not isinstance(user, dict):
    user = {}

role = user.get("role", "")

allowed_roles = [
    "Administrator",
    "Supervisor",
    "Maintenance Engineer",
    "Operations Engineer"
]

if role not in allowed_roles:
    st.error("Access Denied.")
    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "🛠 Maintenance Work Orders",
    "Enterprise Maintenance Management"
)

show_sidebar(user)

# ==========================================================
# LOAD DATA
# ==========================================================

orders = get_all_work_orders()

# ==========================================================
# KPI SAFE CALC
# ==========================================================

if orders.empty:
    total = pending = approved = completed = rejected = 0
else:
    total = len(orders)
    pending = (orders["status"] == "PENDING").sum()
    approved = (orders["status"] == "APPROVED").sum()
    completed = (orders["status"] == "COMPLETED").sum()
    rejected = (orders["status"] == "REJECTED").sum()

st.subheader("📊 Work Order Overview")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total", total)
c2.metric("Pending", pending)
c3.metric("Approved", approved)
c4.metric("Completed", completed)
c5.metric("Rejected", rejected)

st.divider()

# ==========================================================
# FILTERS
# ==========================================================

left, right = st.columns(2)

with left:
    search = st.text_input("🔍 Search Machine", key="wo_search")

with right:
    status_options = (
        ["ALL"] +
        list(orders["status"].unique())
        if not orders.empty and "status" in orders.columns
        else ["ALL"]
    )

    status = st.selectbox("Filter Status", status_options, key="wo_status")

filtered = orders.copy()

if not filtered.empty:

    if search:
        filtered = filtered[
            filtered["machine"].astype(str).str.contains(search, case=False, na=False)
        ]

    if status != "ALL":
        filtered = filtered[filtered["status"] == status]

# ==========================================================
# TABLE
# ==========================================================

st.subheader("📋 Work Orders")

if filtered.empty:
    st.info("No work orders found.")
else:
    st.dataframe(filtered, use_container_width=True, hide_index=True)

st.divider()

# ==========================================================
# UPDATE STATUS (FIXED KEYS)
# ==========================================================

if user["role"] in ["Administrator", "Supervisor"] and not orders.empty:

    st.subheader("⚙ Update Work Order Status")

    selected_id = st.selectbox(
        "Select Work Order ID",
        orders["id"].tolist(),
        key="update_select"
    )

    new_status = st.selectbox(
        "New Status",
        ["PENDING", "APPROVED", "COMPLETED", "REJECTED"],
        key="update_status"
    )

    if st.button("Update Status", key="update_btn"):

        change_work_order_status(selected_id, new_status)

        st.success("Status updated successfully.")
        st.rerun()

# ==========================================================
# DELETE (ADMIN ONLY)
# ==========================================================

if user["role"] == "Administrator" and not orders.empty:

    st.divider()
    st.subheader("🗑 Delete Work Order")

    delete_id = st.selectbox(
        "Select Work Order to Delete",
        orders["id"].tolist(),
        key="delete_select"
    )

    if st.button("Delete Work Order", key="delete_btn"):

        delete_work_order(delete_id)

        st.success("Work order deleted.")
        st.rerun()

# ==========================================================
# CHART
# ==========================================================

st.divider()
st.subheader("📈 Status Distribution")

if not orders.empty:
    st.bar_chart(orders["status"].value_counts())
else:
    st.info("No data available.")

# ==========================================================
# FOOTER
# ==========================================================

show_footer()