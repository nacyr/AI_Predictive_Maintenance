import streamlit as st
import pandas as pd

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

from utils.charts import (
    line_chart,
    bar_chart,
)

from database.work_orders import (
    search_work_orders_by_machine,
    update_work_order_status,
    delete_work_order
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
# LOAD DATA
# ==========================================================

stats = load_statistics()
orders = load_work_orders()
daily_trends = load_daily_trends()
machine_frequency = load_machine_frequency()
ai_breakdown = load_ai_breakdown()

if orders is None or orders.empty:
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
# ANALYTICS TABS
# ==========================================================

tab1, tab2, tab3 = st.tabs([
    "📈 Daily Trends",
    "🏭 Machine Failures",
    "🤖 AI vs Manual"
])

# --------------------------
# DAILY TRENDS
# --------------------------

with tab1:
    st.subheader("Daily Work Order Trends")

    if daily_trends.empty:
        st.info("No trend data available.")
    else:
        line_chart(
            daily_trends,
            x="date",
            y="count",
            title="Daily Work Orders"
        )
        dataframe_card(daily_trends)

# --------------------------
# MACHINE FAILURES
# --------------------------

with tab2:
    st.subheader("Machine Failure Frequency")

    if machine_frequency.empty:
        st.info("No machine statistics available.")
    else:
        bar_chart(
            machine_frequency,
            x="machine",
            y="count",
            title="Machine Failure Frequency"
        )
        dataframe_card(machine_frequency)

# --------------------------
# AI BREAKDOWN
# --------------------------

with tab3:
    st.subheader("AI vs Manual Work Orders")

    if not ai_breakdown:
        st.info("No AI work order data available.")
    else:
        ai_df = pd.DataFrame({
            "Source": list(ai_breakdown.keys()),
            "Count": list(ai_breakdown.values())
        })

        bar_chart(
            ai_df,
            x="Source",
            y="Count",
            title="AI vs Manual"
        )

        dataframe_card(ai_df)

st.divider()

# ==========================================================
# SEARCH WORK ORDERS
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
# UPDATE STATUS
# ==========================================================

section_title("⚙ Update Work Order")

if not orders.empty:

    order_id = st.selectbox(
        "Select Work Order",
        orders["id"].tolist(),
        key="admin_order"
    )

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
# DELETE WORK ORDER
# ==========================================================

section_title("🗑 Delete Work Order")

if not orders.empty:

    delete_id = st.selectbox(
        "Select Work Order",
        orders["id"].tolist(),
        key="delete_order"
    )

    if st.button("Delete Work Order", use_container_width=True):

        delete_work_order(delete_id)
        st.success("Work order deleted successfully.")
        st.rerun()

st.divider()

# ==========================================================
# FULL TABLE
# ==========================================================

st.subheader("📋 All Work Orders")

if orders.empty:
    st.info("No work orders available.")
else:
    st.dataframe(orders, use_container_width=True, hide_index=True)

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

st.subheader("⚡ Quick Navigation")

c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🤖 Prediction", use_container_width=True):
        st.switch_page("pages/prediction.py")

with c2:
    if st.button("📈 Analytics", use_container_width=True):
        st.switch_page("pages/analytics.py")

with c3:
    if st.button("🛠 Maintenance", use_container_width=True):
        st.switch_page("pages/maintenance_dashboard.py")

with c4:
    if st.button("⚙ Operations", use_container_width=True):
        st.switch_page("pages/operations_dashboard.py")

st.divider()

# ==========================================================
# SYSTEM STATUS
# ==========================================================

st.subheader("🟢 System Status")

if orders.empty:
    st.info("No maintenance records available.")
else:
    pending = (orders["status"] == "PENDING").sum()

    if pending == 0:
        st.success("All work orders are up to date.")
    else:
        st.warning(f"{pending} work order(s) are still pending.")

# ==========================================================
# END PAGE
# ==========================================================

end_page()