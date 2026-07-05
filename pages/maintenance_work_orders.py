import streamlit as st
import pandas as pd

from utils.page_config import setup_page, end_page

from database.work_orders import (
    get_work_orders,
    search_work_orders_by_machine,
    update_work_order_status
)

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="🛠 Maintenance Work Orders",
    icon="🛠",
    subtitle="Work Order Management Center",
    allowed_roles=[
        "Maintenance Engineer",
        "Administrator",
        "Supervisor"
    ],
)

# ==========================================================
# LOAD DATA
# ==========================================================

orders = get_work_orders()

if orders is None or orders.empty:
    orders = pd.DataFrame()

# ==========================================================
# WORK ORDER TABLE
# ==========================================================

st.subheader("📋 All Work Orders")

if orders.empty:
    st.info("No work orders available.")
else:
    st.dataframe(orders, use_container_width=True, hide_index=True)

st.divider()

# ==========================================================
# SEARCH WORK ORDERS
# ==========================================================

st.subheader("🔍 Search Work Orders")

search_text = st.text_input("Search by Machine")

if search_text.strip():
    filtered = search_work_orders_by_machine(search_text)
else:
    filtered = orders

st.dataframe(filtered, use_container_width=True, hide_index=True)

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

    if st.button("Update Status", use_container_width=True):

        update_work_order_status(order_id, new_status)

        st.success("Work order updated successfully.")
        st.rerun()

else:
    st.info("No work orders to update.")

# ==========================================================
# SUMMARY
# ==========================================================

st.divider()

st.subheader("📊 Quick Summary")

if not orders.empty:

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", len(orders))
    col2.metric("Pending", (orders["status"] == "PENDING").sum())
    col3.metric("Completed", (orders["status"] == "COMPLETED").sum())

else:
    st.info("No data available.")

# ==========================================================
# END PAGE
# ==========================================================

end_page()