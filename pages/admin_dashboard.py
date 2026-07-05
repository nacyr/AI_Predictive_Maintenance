from pathlib import Path
import sys

# ==========================================================
# FORCE PROJECT ROOT (STREAMLIT CLOUD SAFE)
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

# ==========================================================
# SAFE IMPORT (MODULE ALIAS STYLE - BEST FOR STREAMLIT CLOUD)
# ==========================================================

try:
    import database.work_orders as wo
except Exception as e:
    st.error("❌ Failed to import database module")
    st.code(str(e))
    st.stop()

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Industrial AI Predictive Maintenance",
    layout="wide"
)

st.title("🏭 Industrial Predictive Maintenance Dashboard")

# ==========================================================
# LOAD DATA SAFELY
# ==========================================================

try:
    stats = wo.get_work_order_statistics()
    df_all = wo.get_all_work_orders()
except Exception as e:
    st.error("❌ Failed to load data from database")
    st.code(str(e))
    st.stop()

# ==========================================================
# TABS
# ==========================================================

tab1, tab2, tab3 = st.tabs([
    "📊 Overview",
    "🛠️ Work Orders",
    "⚙️ Control Panel"
])

# ==========================================================
# TAB 1 — OVERVIEW
# ==========================================================

with tab1:
    st.subheader("System Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total", stats.get("total", 0))
    col2.metric("Pending", stats.get("pending", 0))
    col3.metric("Assigned", stats.get("assigned", 0))
    col4.metric("In Progress", stats.get("in_progress", 0))
    col5.metric("Completed", stats.get("completed", 0))

    st.divider()

    st.subheader("Recent Work Orders")

    if df_all is not None and not df_all.empty:
        st.dataframe(df_all.head(10), use_container_width=True)
    else:
        st.info("No work orders available.")

# ==========================================================
# TAB 2 — WORK ORDERS
# ==========================================================

with tab2:
    st.subheader("Work Orders Management")

    search = st.text_input("Search by machine name")

    if search:
        data = wo.search_work_orders_by_machine(search)
    else:
        data = df_all

    if data is not None and not data.empty:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No matching records found.")

# ==========================================================
# TAB 3 — CONTROL PANEL
# ==========================================================

with tab3:
    st.subheader("Control Center")

    col1, col2 = st.columns(2)

    # -------------------------
    # ASSIGN ENGINEER
    # -------------------------
    with col1:
        st.markdown("### Assign Engineer")

        work_id = st.number_input("Work Order ID", min_value=1, step=1)
        engineer = st.text_input("Engineer Name")

        if st.button("Assign Engineer"):
            if engineer.strip():
                wo.assign_work_order(work_id, engineer.strip())
                st.success("Engineer assigned successfully")
                st.rerun()
            else:
                st.warning("Please enter engineer name")

    # -------------------------
    # UPDATE STATUS
    # -------------------------
    with col2:
        st.markdown("### Update Status")

        status_id = st.number_input("Work Order ID", min_value=1, step=1)

        status = st.selectbox(
            "Status",
            ["PENDING", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "REJECTED"]
        )

        if st.button("Update Status"):
            wo.change_work_order_status(status_id, status)
            st.success("Status updated successfully")
            st.rerun()