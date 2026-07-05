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

from utils.simulator import generate_sensor_data
from utils.plant import plant_status

from ml.predict import predict_failure

from database.work_orders import (
    get_work_orders,
    create_work_order,
    create_work_order_from_prediction,
    update_work_order_status
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Maintenance Engineer Dashboard",
    page_icon="🛠",
    layout="wide"
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="maintenance_dashboard_refresh"
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
    "Maintenance Engineer"
]

if user["role"] not in allowed_roles:

    st.error("Access Denied.")

    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "🛠 Maintenance Engineer Dashboard",
    "Enterprise Maintenance Operations & AI Diagnostics"
)

show_sidebar(user)

# ==========================================================
# LOAD DATABASE
# ==========================================================

try:
    orders = get_work_orders()
except Exception:
    orders = pd.DataFrame()

try:
    plants = plant_status()
except Exception:
    plants = pd.DataFrame()

# ==========================================================
# KPI CALCULATIONS
# ==========================================================

total_orders = len(orders)

pending = approved = completed = rejected = 0

if not orders.empty:

    pending = (orders["status"] == "PENDING").sum()
    approved = (orders["status"] == "APPROVED").sum()
    completed = (orders["status"] == "COMPLETED").sum()
    rejected = (orders["status"] == "REJECTED").sum()

critical_assets = warning_assets = normal_assets = 0

if not plants.empty and "Status" in plants.columns:

    status = plants["Status"].astype(str)

    normal_assets = status.str.contains(
        "NORMAL",
        case=False,
        na=False
    ).sum()

    warning_assets = status.str.contains(
        "WARNING",
        case=False,
        na=False
    ).sum()

    critical_assets = status.str.contains(
        "CRITICAL",
        case=False,
        na=False
    ).sum()

# ==========================================================
# KPI DASHBOARD
# ==========================================================

st.subheader("📊 Maintenance Operations Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Work Orders",
    total_orders
)

c2.metric(
    "Pending",
    pending
)

c3.metric(
    "Completed",
    completed
)

c4.metric(
    "Critical Assets",
    critical_assets
)

st.divider()

# ==========================================================
# PLANT STATUS
# ==========================================================

left, right = st.columns([2, 1])

with left:

    st.subheader("🏭 Live Plant Status")

    if plants.empty:

        st.info("No plant data available.")

    else:

        st.dataframe(
            plants,
            width="stretch",
            hide_index=True
        )

with right:

    st.subheader("📋 Work Order Summary")

    if orders.empty:

        st.info("No work orders available.")

    else:

        summary = (
            orders["status"]
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
# LIVE AI MACHINE MONITORING
# ==========================================================

st.subheader("🤖 AI Machine Monitoring")

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

    # Automatically create work order for high-risk machines
    create_work_order_from_prediction(
        machine=machine,
        risk_score=probability,
        sensor_data=sensor
    )

    records.append({

        "Machine": machine,
        "Temperature (°C)": round(sensor["temperature"], 2),
        "Pressure (bar)": round(sensor["pressure"], 2),
        "Vibration": round(sensor["vibration"], 2),
        "Current (A)": round(sensor["current"], 2),
        "RPM": int(sensor["rpm"]),
        "Prediction": "Failure" if prediction else "Normal",
        "Risk (%)": round(probability * 100, 2)

    })

monitor_df = pd.DataFrame(records)

st.dataframe(
    monitor_df,
    width="stretch",
    hide_index=True
)

st.subheader("📈 Machine Failure Risk")

st.bar_chart(
    monitor_df.set_index("Machine")["Risk (%)"]
)

high_risk = monitor_df[
    monitor_df["Risk (%)"] >= 70
]

if high_risk.empty:

    st.success("No high-risk machines detected.")

else:

    st.error(f"{len(high_risk)} machine(s) require immediate maintenance.")

    st.dataframe(
        high_risk,
        width="stretch",
        hide_index=True
    )

st.divider()
# ==========================================================
# CREATE MANUAL WORK ORDER
# ==========================================================

st.subheader("➕ Create Maintenance Work Order")

machine = st.selectbox(
    "Select Machine",
    machines
)

issue = st.text_area(
    "Issue Description",
    placeholder="Describe the maintenance issue..."
)

priority = st.selectbox(
    "Priority",
    [
        "LOW",
        "MEDIUM",
        "HIGH"
    ]
)

if st.button(
    "Create Work Order",
    width="stretch"
):

    if issue.strip() == "":

        st.warning("Please enter an issue description.")

    else:

        create_work_order(
            machine=machine,
            issue=issue,
            priority=priority,
            created_by=user["fullname"]
        )

        st.success("Maintenance work order created successfully.")

        st.rerun()

st.divider()

# ==========================================================
# WORK ORDER MANAGEMENT
# ==========================================================

st.subheader("🛠 Maintenance Work Orders")

if orders.empty:

    st.info("No work orders available.")

else:

    st.dataframe(
        orders,
        width="stretch",
        hide_index=True
    )

st.divider()

# ==========================================================
# WORK ORDER STATUS CHART
# ==========================================================

st.subheader("📊 Work Order Status Distribution")

if not orders.empty:

    st.bar_chart(
        orders["status"].value_counts()
    )

else:

    st.info("No work order statistics available.")

st.divider()

# ==========================================================
# UPDATE WORK ORDER STATUS
# ==========================================================

if not orders.empty:

    st.subheader("✅ Update Work Order Status")

    editable_orders = orders[
        orders["status"] != "COMPLETED"
    ]

    if editable_orders.empty:

        st.success(
            "All maintenance work orders have already been completed."
        )

    else:

        selected_id = st.selectbox(
            "Work Order ID",
            editable_orders["id"].tolist()
        )

        new_status = st.selectbox(
            "Select New Status",
            [
                "PENDING",
                "APPROVED",
                "COMPLETED",
                "REJECTED"
            ]
        )

        if st.button(
            "Update Work Order",
            width="stretch"
        ):

            update_work_order_status(
                selected_id,
                new_status
            )

            st.success(
                f"Work Order #{selected_id} updated successfully."
            )

            st.rerun()

st.divider()

# ==========================================================
# APPROVED WORK ORDERS
# ==========================================================

st.subheader("✔ Approved Maintenance Jobs")

if orders.empty:

    st.info("No work orders available.")

else:

    approved_jobs = orders[
        orders["status"] == "APPROVED"
    ]

    if approved_jobs.empty:

        st.info("No approved maintenance jobs.")

    else:

        st.dataframe(
            approved_jobs,
            width="stretch",
            hide_index=True
        )

st.divider()

# ==========================================================
# CRITICAL MACHINE SUMMARY
# ==========================================================

st.subheader("🚨 Critical Machine Summary")

if high_risk.empty:

    st.success(
        "All monitored equipment is operating within acceptable limits."
    )

else:

    st.error(
        f"{len(high_risk)} machine(s) currently require urgent maintenance."
    )

    st.dataframe(
        high_risk[
            [
                "Machine",
                "Prediction",
                "Risk (%)"
            ]
        ],
        width="stretch",
        hide_index=True
    )

st.divider()
# ==========================================================
# RECENT MAINTENANCE ACTIVITIES
# ==========================================================

st.subheader("📋 Recent Maintenance Activities")

if orders.empty:

    st.info("No maintenance activities available.")

else:

    recent_orders = orders.sort_values(
        by="id",
        ascending=False
    ).head(5)

    for _, row in recent_orders.iterrows():

        status = str(row["status"]).upper()

        message = (
            f"#{row['id']} • "
            f"{row['machine']} • "
            f"{row['issue']}"
        )

        if status == "COMPLETED":

            st.success(f"✔ {message}")

        elif status == "APPROVED":

            st.info(f"🔧 {message}")

        elif status == "REJECTED":

            st.error(f"✖ {message}")

        else:

            st.warning(f"⏳ {message}")

st.divider()

# ==========================================================
# ENGINEER NOTES
# ==========================================================

st.subheader("📝 Engineer Notes")

notes = st.text_area(
    "Maintenance observations",
    placeholder="Record inspection findings, repairs performed, recommendations, spare parts used, etc.",
    height=180
)

if st.button(
    "Save Notes",
    width="stretch"
):

    if notes.strip():

        # Future enhancement:
        # Save notes into the database.

        st.success(
            "Maintenance notes saved successfully."
        )

    else:

        st.warning(
            "Please enter maintenance notes first."
        )

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

st.subheader("⚡ Quick Navigation")

col1, col2, col3, col4 = st.columns(4)

with col1:

    if st.button(
        "🤖 Prediction",
        width="stretch"
    ):
        st.switch_page("pages/prediction.py")

with col2:

    if st.button(
        "📈 Analytics",
        width="stretch"
    ):
        st.switch_page("pages/analytics.py")

with col3:

    if st.button(
        "🛠 Work Orders",
        width="stretch"
    ):
        st.switch_page("pages/maintenance_work_orders.py")

with col4:

    if st.button(
        "🏠 Dashboard",
        width="stretch"
    ):
        st.rerun()

st.divider()

# ==========================================================
# LIVE SYSTEM STATUS
# ==========================================================

st.subheader("🟢 System Health")

if critical_assets == 0:

    st.success(
        "All monitored equipment is operating normally."
    )

elif critical_assets <= 2:

    st.warning(
        f"{critical_assets} critical asset(s) currently require maintenance."
    )

else:

    st.error(
        f"{critical_assets} critical assets require immediate intervention."
    )

if warning_assets > 0:

    st.info(
        f"{warning_assets} equipment unit(s) are currently under observation."
    )

st.divider()

# ==========================================================
# SESSION INFORMATION
# ==========================================================

st.subheader("👤 Session Information")

info1, info2 = st.columns(2)

with info1:

    st.info(
        f"""
**Engineer:** {user['fullname']}

**Role:** {user['role']}

**Department:** Maintenance Engineering
"""
    )

with info2:

    st.info(
        f"""
**Dashboard:** Maintenance Engineer

**Auto Refresh:** Every 10 Seconds

**Last Updated:** {datetime.now().strftime('%d %B %Y %H:%M:%S')}
"""
    )

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

show_footer()