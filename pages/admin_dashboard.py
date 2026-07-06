import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from utils.page_config import setup_page, end_page
from utils.data_loader import (
    load_statistics,
    load_work_orders,
    load_daily_trends,
    load_machine_frequency,
    load_ai_breakdown,
)

from utils.dashboard_widgets import (
    section_title,
    metric_row,
    dataframe_card,
)

from utils.charts import line_chart, bar_chart

from database.work_orders import (
    search_work_orders_by_machine,
    update_work_order_status,
    delete_work_order,
)

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="🏭 Administrator Dashboard",
    icon="🏭",
    subtitle="Enterprise System Control Center",
    allowed_roles=["Administrator"],
)

# ==========================================================
# LIVE REFRESH
# ==========================================================

st.subheader("🟢 Live Dashboard")

live_mode = st.toggle("Enable Live Monitoring (10s refresh)", value=True)

if live_mode:
    refresh_count = st_autorefresh(
        interval=10_000,
        key="admin_dashboard_refresh",
    )

    st.success(
        f"""
Live Monitoring Active  
Last Updated: {datetime.now().strftime('%d %b %Y %H:%M:%S')}  
Refresh Count: {refresh_count}
"""
    )
else:
    st.warning("Live monitoring paused.")

st.divider()

# ==========================================================
# LOAD DATA (SAFE)
# ==========================================================

stats = load_statistics()
orders = load_work_orders()
daily_trends = load_daily_trends()
machine_frequency = load_machine_frequency()
ai_breakdown = load_ai_breakdown()

if orders is None:
    orders = pd.DataFrame()

# ==========================================================
# KPI SECTION
# ==========================================================

section_title("📊 Enterprise Overview")

metric_row(
    ("Total Orders", stats.get("total", 0)),
    ("Pending", stats.get("pending", 0)),
    ("Approved", stats.get("approved", 0)),
    ("Completed", stats.get("completed", 0)),
    ("Rejected", stats.get("rejected", 0)),
)

st.divider()

# ==========================================================
# TABS
# ==========================================================

tab1, tab2, tab3 = st.tabs([
    "📈 Daily Trends",
    "🏭 Machine Failures",
    "🤖 AI vs Manual"
])

with tab1:
    st.subheader("Daily Trends")

    if not daily_trends.empty:
        line_chart(daily_trends, x="date", y="count", title="Daily Work Orders")
        dataframe_card(daily_trends)
    else:
        st.info("No trend data available.")

with tab2:
    st.subheader("Machine Failures")

    if not machine_frequency.empty:
        bar_chart(machine_frequency, x="machine", y="count", title="Machine Failures")
        dataframe_card(machine_frequency)
    else:
        st.info("No machine data available.")

with tab3:
    st.subheader("AI vs Manual")

    if ai_breakdown:
        ai_df = pd.DataFrame({
            "Source": list(ai_breakdown.keys()),
            "Count": list(ai_breakdown.values())
        })
        bar_chart(ai_df, x="Source", y="Count", title="AI vs Manual")
        dataframe_card(ai_df)
    else:
        st.info("No AI data available.")

st.divider()

# ==========================================================
# SEARCH
# ==========================================================

section_title("🔍 Search Work Orders")

search_text = st.text_input("Search by Machine")

if search_text.strip():
    filtered = search_work_orders_by_machine(search_text)
else:
    filtered = orders

dataframe_card(filtered)

st.divider()

# ==========================================================
# UPDATE STATUS (SAFE FIX)
# ==========================================================

section_title("⚙ Update Work Order Status")

if not orders.empty:

    order_ids = orders["id"].tolist()

    order_id = st.selectbox("Select Work Order", order_ids, key="admin_order")

    selected_row = orders[orders["id"] == order_id]

    current = (
        selected_row["status"].iloc[0]
        if not selected_row.empty
        else "UNKNOWN"
    )

    st.caption(f"Current Status: **{current}**")

    new_status = st.selectbox(
        "New Status",
        ["PENDING", "APPROVED", "IN_PROGRESS", "COMPLETED", "REJECTED"],
        key="admin_status"
    )

    if st.button("Update Status", use_container_width=True):

        update_work_order_status(order_id, new_status)
        st.success("Work order updated successfully.")
        st.rerun()

st.divider()

# ==========================================================
# DELETE (SAFE FIX)
# ==========================================================

section_title("🗑 Delete Work Order")

if not orders.empty:

    delete_id = st.selectbox("Select Work Order", orders["id"].tolist(), key="delete_order")
    confirm = st.checkbox("Confirm deletion")

    if st.button("Delete Work Order", use_container_width=True):

        if confirm:
            delete_work_order(delete_id)
            st.success("Work order deleted.")
            st.rerun()
        else:
            st.warning("Please confirm deletion.")

st.divider()

# ==========================================================
# TABLE
# ==========================================================

section_title("📋 Enterprise Work Orders")

if not orders.empty:
    st.dataframe(orders, use_container_width=True, hide_index=True)
else:
    st.info("No work orders found.")

st.divider()

# ==========================================================
# STATUS SUMMARY
# ==========================================================

section_title("🟢 Enterprise Status")

if not orders.empty:

    pending = (orders["status"] == "PENDING").sum()
    approved = (orders["status"] == "APPROVED").sum()
    completed = (orders["status"] == "COMPLETED").sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Pending", pending)
    col2.metric("Approved", approved)
    col3.metric("Completed", completed)

    total = len(orders)
    completion = (completed / total) * 100 if total else 0

    st.progress(completion / 100)
    st.caption(f"Completion Rate: {completion:.1f}%")

st.divider()

end_page()