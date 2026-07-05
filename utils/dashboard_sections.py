from datetime import datetime

import streamlit as st

from utils.dashboard_widgets import (
    metric_row,
    dataframe_card,
)

from utils.charts import (
    work_order_status_chart,
    machine_risk_chart,
)

from utils.alerts import (
    machine_status,
    no_data,
)

from utils.navigation import quick_navigation


# ==========================================================
# MACHINE TABLE
# ==========================================================

def show_machine_table(machine_df):

    st.subheader("🏭 Live Machine Monitoring")

    if machine_df.empty:

        no_data("No machine data available.")

        return

    dataframe_card(machine_df)


# ==========================================================
# WORK ORDER TABLE
# ==========================================================

def show_work_orders(orders):

    st.subheader("🛠 Work Orders")

    if orders.empty:

        no_data("No work orders available.")

        return

    dataframe_card(orders)


# ==========================================================
# MACHINE SUMMARY
# ==========================================================

def show_machine_summary(summary):

    metric_row(

        ("Machines", summary["total"]),

        ("Normal", summary["normal"]),

        ("Warning", summary["warning"]),

        ("Critical", summary["critical"])

    )


# ==========================================================
# HEALTH SUMMARY
# ==========================================================

def show_health_summary(summary):

    metric_row(

        ("Average Health", f"{summary['average_health']}%"),

        ("Average Risk", f"{summary['average_risk']}%")

    )


# ==========================================================
# MACHINE ALERTS
# ==========================================================

def show_machine_alerts(summary):

    st.subheader("🚨 System Status")

    machine_status(

        summary["critical"],

        summary["warning"]

    )


# ==========================================================
# WORK ORDER CHART
# ==========================================================

def show_work_order_chart(orders):

    st.subheader("📊 Work Order Distribution")

    work_order_status_chart(orders)


# ==========================================================
# MACHINE RISK CHART
# ==========================================================

def show_risk_chart(machine_df):

    st.subheader("📈 AI Failure Risk")

    machine_risk_chart(machine_df)


# ==========================================================
# SESSION INFO
# ==========================================================

def show_session(user):

    st.subheader("👤 Session")

    st.info(

        f"""

User: **{user.get('fullname','User')}**

Role: **{user.get('role','Unknown')}**

Updated: **{datetime.now().strftime('%d %b %Y %H:%M:%S')}**

"""

    )


# ==========================================================
# QUICK NAVIGATION
# ==========================================================

def show_navigation(buttons):

    quick_navigation(buttons)