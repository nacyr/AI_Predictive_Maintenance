import streamlit as st
import pandas as pd

from database.work_orders import (
    get_all_work_orders,
    get_work_order_statistics,
    get_machine_failure_frequency,
    get_daily_work_order_trends,
    get_ai_vs_manual_breakdown,
    search_work_orders_by_machine,
    assign_work_order,
    change_work_order_status
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Industrial Maintenance System",
    layout="wide"
)

st.title("🏭 Industrial Predictive Maintenance System")


# ==========================================================
# LOAD DATA
# ==========================================================

stats = get_work_order_statistics()
df_all = get_all_work_orders()


# ==========================================================
# TABS (PROFESSIONAL UI STRUCTURE)
# ==========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📈 Analytics",
    "🧠 AI Insights",
    "🛠️ Work Orders"
])


# ==========================================================
# TAB 1 — OVERVIEW (KPI DASHBOARD)
# ==========================================================

with tab1:
    st.subheader("System Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Orders", stats["total"])
    col2.metric("Pending", stats["pending"])
    col3.metric("Assigned", stats["assigned"])
    col4.metric("In Progress", stats["in_progress"])
    col5.metric("Completed", stats["completed"])

    st.divider()

    st.subheader("Recent Work Orders")
    st.dataframe(df_all.head(10), use_container_width=True)


# ==========================================================
# TAB 2 — ANALYTICS (CHARTS)
# ==========================================================

with tab2:
    st.subheader("Maintenance Analytics")

    # Machine failure frequency
    st.markdown("### 🔧 Machine Failure Frequency")
    freq = get_machine_failure_frequency()
    st.bar_chart(freq.set_index("machine"))

    st.divider()

    # Daily trends
    st.markdown("### 📈 Daily Work Order Trends")
    trends = get_daily_work_order_trends()
    st.line_chart(trends.set_index("date"))


# ==========================================================
# TAB 3 — AI INSIGHTS
# ==========================================================

with tab3:
    st.subheader("AI System Insights")

    ai_breakdown = get_ai_vs_manual_breakdown()

    ai_df = pd.DataFrame({
        "Source": list(ai_breakdown.keys()),
        "Count": list(ai_breakdown.values())
    })

    st.markdown("### 🤖 AI vs Manual Work Orders")
    st.bar_chart(ai_df.set_index("Source"))

    st.info("AI-generated work orders are automatically created when risk score exceeds threshold.")


# ==========================================================
# TAB 4 — WORK ORDERS MANAGEMENT
# ==========================================================

with tab4:
    st.subheader("Work Order Control Center")

    # SEARCH
    search = st.text_input("Search by machine")

    if search:
        data = search_work_orders_by_machine(search)
    else:
        data = df_all

    st.dataframe(data, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    # -------------------------
    # ASSIGN ENGINEER
    # -------------------------
    with col1:
        st.markdown("### Assign Engineer")

        wid = st.number_input("Work Order ID", min_value=1, step=1)
        engineer = st.text_input("Engineer Name")

        if st.button("Assign"):
            if engineer:
                assign_work_order(wid, engineer)
                st.success("Engineer assigned successfully")
                st.rerun()
            else:
                st.warning("Enter engineer name")


    # -------------------------
    # CHANGE STATUS
    # -------------------------
    with col2:
        st.markdown("### Update Status")

        sid = st.number_input("Work Order ID ", min_value=1, step=1)

        status = st.selectbox(
            "Status",
            ["PENDING", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "REJECTED"]
        )

        if st.button("Update"):
            change_work_order_status(sid, status)
            st.success("Status updated successfully")
            st.rerun()