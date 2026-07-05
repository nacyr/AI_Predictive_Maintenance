import sys
from pathlib import Path
from datetime import datetime

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
    get_work_orders,
    update_work_order_status,
    create_work_order_from_prediction
)

from utils.plant import plant_status
from utils.simulator import generate_sensor_data
from ml.predict import predict_failure

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Supervisor Dashboard",
    page_icon="🧑‍✈️",
    layout="wide"
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="supervisor_dashboard_refresh"
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
# ==========================================================

allowed_roles = [
    "Administrator",
    "Supervisor"
]

if user["role"] not in allowed_roles:

    st.error("Access Denied.")

    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "🧑‍✈️ Supervisor Dashboard",
    "Enterprise AI Maintenance Approval Center"
)

show_sidebar(user)

# ==========================================================
# LOAD PLANT STATUS
# ==========================================================

try:

    plant_df = plant_status()

except Exception:

    plant_df = pd.DataFrame()

# ==========================================================
# LIVE AI MONITORING
# ==========================================================

machines = [

    "Pump A1",
    "Compressor B2",
    "Generator C3",
    "Motor D4",
    "Cooling Unit E5"

]

records = []

for machine in machines:

    sensor = generate_sensor_data()

    prediction, probability = predict_failure(

        sensor["temperature"],
        sensor["pressure"],
        sensor["vibration"],
        sensor["current"],
        sensor["rpm"],
        sensor["running_hours"]

    )

    try:

        create_work_order_from_prediction(
            machine,
            probability,
            sensor
        )

    except Exception:
        pass

    records.append({

        "Machine": machine,
        "Temperature (°C)": round(sensor["temperature"],2),
        "Pressure (bar)": round(sensor["pressure"],2),
        "Vibration": round(sensor["vibration"],2),
        "Current (A)": round(sensor["current"],2),
        "Prediction": "Failure" if prediction else "Normal",
        "Risk (%)": round(probability*100,2)

    })

risk_df = pd.DataFrame(records)

# ==========================================================
# LOAD WORK ORDERS
# ==========================================================

try:

    orders = get_work_orders()

except Exception:

    orders = pd.DataFrame()

# ==========================================================
# KPI CALCULATIONS
# ==========================================================

pending = approved = completed = rejected = 0

if not orders.empty:

    pending = (orders["status"] == "PENDING").sum()

    approved = (orders["status"] == "APPROVED").sum()

    completed = (orders["status"] == "COMPLETED").sum()

    rejected = (orders["status"] == "REJECTED").sum()

normal = warning = critical = 0

if not plant_df.empty and "Status" in plant_df.columns:

    status = plant_df["Status"].astype(str)

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

# ==========================================================
# KPI DASHBOARD
# ==========================================================

st.subheader("📊 Supervisor Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Critical Assets",
    critical
)

c2.metric(
    "Pending Orders",
    pending
)

c3.metric(
    "Approved",
    approved
)

c4.metric(
    "Completed",
    completed
)

st.divider()

# ==========================================================
# PLANT STATUS
# ==========================================================

left, right = st.columns([2,1])

with left:

    st.subheader("🏭 Plant Status")

    if plant_df.empty:

        st.info("No plant data available.")

    else:

        st.dataframe(
            plant_df,
            width="stretch",
            hide_index=True
        )

with right:

    st.subheader("📋 Plant Summary")

    st.metric("Normal", normal)

    st.metric("Warning", warning)

    st.metric("Critical", critical)

st.divider()

# ==========================================================
# LIVE AI MONITORING
# ==========================================================

st.subheader("🤖 Live AI Risk Monitoring")

st.dataframe(
    risk_df,
    width="stretch",
    hide_index=True
)

high_risk = risk_df[
    risk_df["Risk (%)"] >= 70
]

if high_risk.empty:

    st.success("No critical machines detected.")

else:

    st.error(
        f"{len(high_risk)} high-risk machine(s) detected."
    )

    st.dataframe(
        high_risk,
        width="stretch",
        hide_index=True
    )

st.divider()
# ==========================================================
# PENDING WORK ORDERS
# ==========================================================

st.subheader("🛠 Pending Maintenance Approvals")

if orders.empty:

    st.info("No work orders available.")

else:

    pending_orders = orders[
        orders["status"] == "PENDING"
    ]

    if pending_orders.empty:

        st.success("There are no pending approvals.")

    else:

        st.dataframe(
            pending_orders,
            width="stretch",
            hide_index=True
        )

st.divider()

# ==========================================================
# APPROVAL CENTER
# ==========================================================

if (
    not orders.empty
    and not pending_orders.empty
):

    st.subheader("✅ Supervisor Approval Center")

    selected_order = st.selectbox(
        "Select Work Order",
        pending_orders["id"].tolist()
    )

    decision = st.radio(
        "Approval Decision",
        [
            "APPROVED",
            "REJECTED"
        ]
    )

    if st.button(
        "Save Decision",
        width="stretch"
    ):

        update_work_order_status(
            selected_order,
            decision
        )

        st.success(
            "Work order updated successfully."
        )

        st.rerun()

st.divider()

# ==========================================================
# WORK ORDER STATUS CHART
# ==========================================================

st.subheader("📈 Work Order Distribution")

if not orders.empty:

    st.bar_chart(
        orders["status"].value_counts()
    )

else:

    st.info(
        "No work order statistics available."
    )

st.divider()

# ==========================================================
# RECENT ACTIVITIES
# ==========================================================

st.subheader("📋 Recent Maintenance Activities")

if orders.empty:

    st.info("No maintenance records found.")

else:

    recent_orders = orders.head(5)

    for _, row in recent_orders.iterrows():

        status = str(row["status"]).upper()

        if status == "COMPLETED":

            st.success(
                f"✔ #{row['id']} • {row['machine']} • {row['issue']}"
            )

        elif status == "APPROVED":

            st.info(
                f"🔧 #{row['id']} • {row['machine']} • {row['issue']}"
            )

        elif status == "REJECTED":

            st.error(
                f"✖ #{row['id']} • {row['machine']} • {row['issue']}"
            )

        else:

            st.warning(
                f"⏳ #{row['id']} • {row['machine']} • {row['issue']}"
            )

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

st.subheader("⚡ Quick Navigation")

c1, c2, c3, c4 = st.columns(4)

with c1:

    if st.button(
        "🤖 Prediction",
        width="stretch"
    ):
        st.switch_page(
            "pages/prediction.py"
        )

with c2:

    if st.button(
        "📊 Analytics",
        width="stretch"
    ):
        st.switch_page(
            "pages/analytics.py"
        )

with c3:

    if st.button(
        "🛠 Work Orders",
        width="stretch"
    ):
        st.switch_page(
            "pages/maintenance_work_orders.py"
        )

with c4:

    if st.button(
        "🏠 Dashboard",
        width="stretch"
    ):

        if user["role"] == "Administrator":

            st.switch_page(
                "pages/admin_dashboard.py"
            )

        else:

            st.rerun()

st.divider()

# ==========================================================
# SYSTEM STATUS
# ==========================================================

st.subheader("🟢 Plant Health Status")

if critical == 0:

    st.success(
        "All production assets are operating normally."
    )

elif critical <= 2:

    st.warning(
        f"{critical} critical asset(s) require supervisor attention."
    )

else:

    st.error(
        f"{critical} critical assets require immediate intervention."
    )

if warning > 0:

    st.info(
        f"{warning} asset(s) are currently under observation."
    )

st.divider()

# ==========================================================
# SESSION INFORMATION
# ==========================================================

st.subheader("👤 Session Information")

st.info(
    f"""
Current User: **{user['fullname']}**

Role: **{user['role']}**

Dashboard: **Supervisor Control Center**

Auto Refresh: **Every 10 Seconds**

Last Updated: **{datetime.now().strftime('%d %B %Y %H:%M:%S')}**
"""
)

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

show_footer()

st.caption(
    "Industrial AI Predictive Maintenance System • "
    "Supervisor Dashboard • Enterprise Edition"
)