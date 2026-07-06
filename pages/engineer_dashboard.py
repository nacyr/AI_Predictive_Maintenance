import streamlit as st
import pandas as pd

from streamlit_autorefresh import st_autorefresh

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation
from utils.simulator import generate_sensor_data

from database.work_orders import (
    get_work_orders,
    update_work_order_status
)

from components.live_status import show_live_status
from components.kpi_cards import show_kpi_cards
from components.live_machine_table import show_live_machine_table
from components.plant_health import show_plant_health
from components.alert_center import show_alert_center

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="🔧 Engineer Dashboard",
    icon="🔧",
    subtitle="Diagnostics & Work Execution Center",
    allowed_roles=[
        "Maintenance Engineer",
        "Administrator",
        "Supervisor"
    ],
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

refresh_count = st_autorefresh(
    interval=10000,
    key="engineer_dashboard_refresh"
)

show_live_status(refresh_count)

st.divider()

# ==========================================================
# LOAD WORK ORDERS
# ==========================================================

orders = get_work_orders()

if orders is None:
    orders = pd.DataFrame()

# ==========================================================
# LIVE MACHINE DATA
# ==========================================================

machines = [
    "Pump A1",
    "Pump A2",
    "Compressor B1",
    "Compressor B2",
    "Motor C1",
    "Motor C2",
    "Generator D1",
    "Cooling Fan E1"
]

records = []

for machine in machines:

    sensor = generate_sensor_data()

    risk = min(
        100,
        round(
            (
                sensor["temperature"] * 0.40
                + sensor["vibration"] * 15
                + sensor["pressure"] * 2
            ),
            1
        )
    )

    if risk >= 70:
        status = "CRITICAL"

    elif risk >= 40:
        status = "WARNING"

    else:
        status = "NORMAL"

    records.append({

        "Machine": machine,

        "Temperature (°C)": round(sensor["temperature"], 2),

        "Pressure (bar)": round(sensor["pressure"], 2),

        "Vibration": round(sensor["vibration"], 2),

        "Current (A)": round(sensor["current"], 2),

        "RPM": round(sensor["rpm"], 0),

        "Running Hours": sensor["running_hours"],

        "Failure Risk (%)": risk,

        "Status": status

    })

machine_df = pd.DataFrame(records)

# ==========================================================
# KPI CARDS
# ==========================================================

pending = (
    orders["status"] == "PENDING"
).sum() if not orders.empty else 0

completed = (
    orders["status"] == "COMPLETED"
).sum() if not orders.empty else 0

critical = (
    machine_df["Failure Risk (%)"] >= 70
).sum()

warning = (
    (machine_df["Failure Risk (%)"] >= 40)
    &
    (machine_df["Failure Risk (%)"] < 70)
).sum()

healthy = (
    machine_df["Failure Risk (%)"] < 40
).sum()

plant_health = round(
    healthy / len(machine_df) * 100,
    1
)

show_kpi_cards(
    total_orders=len(orders),
    pending=pending,
    completed=completed,
    critical=critical,
    warning=warning,
    healthy=healthy,
    plant_health=plant_health
)

st.divider()

# ==========================================================
# LIVE MACHINE MONITORING
# ==========================================================

show_live_machine_table(machine_df)

st.divider()

# ==========================================================
# FAILURE RISK ANALYSIS
# ==========================================================

st.subheader("📈 Failure Risk Analysis")

st.bar_chart(
    machine_df.set_index("Machine")["Failure Risk (%)"]
)

st.caption(
    "Live AI-assisted monitoring of machine failure risk."
)

st.divider()
# ==========================================================
# WORK ORDER EXECUTION
# ==========================================================

st.subheader("🛠 Work Order Execution")

if orders.empty:

    st.info("No work orders available.")

else:

    order_id = st.selectbox(
        "Select Work Order",
        orders["id"].tolist()
    )

    new_status = st.selectbox(
        "Update Status",
        [
            "IN_PROGRESS",
            "COMPLETED",
            "REJECTED"
        ]
    )

    if st.button(
        "Update Status",
        use_container_width=True
    ):

        update_work_order_status(
            order_id,
            new_status
        )

        st.success(
            "Work order updated successfully."
        )

        st.rerun()

st.divider()

# ==========================================================
# PLANT HEALTH
# ==========================================================

show_plant_health(machine_df)

st.divider()

# ==========================================================
# ALERT CENTER
# ==========================================================

show_alert_center(machine_df)

st.divider()

# ==========================================================
# ASSIGNED WORK ORDERS
# ==========================================================

st.subheader("📋 Assigned Work Orders")

if orders.empty:

    st.info(
        "No assigned work orders."
    )

else:

    st.dataframe(
        orders,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# ENGINEER SUMMARY
# ==========================================================

st.subheader("🔧 Engineer Summary")

left, right = st.columns(2)

with left:

    st.success(f"""
📋 Total Work Orders: **{len(orders)}**

🟡 Pending: **{pending}**

✅ Completed: **{completed}**
""")

with right:

    st.info(f"""
🔴 Critical Machines: **{critical}**

🟡 Warning Machines: **{warning}**

🟢 Healthy Machines: **{healthy}**

💚 Plant Health: **{plant_health:.1f}%**
""")

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

quick_navigation(
    prediction=True,
    analytics=True,
    maintenance=True,
    operations=True,
    admin=user.get("role") == "Administrator"
)

st.divider()

# ==========================================================
# SESSION INFORMATION
# ==========================================================

st.subheader("👤 Session Information")

col1, col2 = st.columns(2)

with col1:

    st.info(f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}
""")

with col2:

    st.info(f"""
**Dashboard:** Engineer Dashboard

**Refresh Interval:** 10 Seconds

**Refresh Count:** {refresh_count}
""")

st.divider()

# ==========================================================
# LIVE SYSTEM STATUS
# ==========================================================

st.subheader("🟢 Live System Status")

if critical == 0:

    st.success(
        "All monitored machines are operating normally."
    )

elif critical <= 2:

    st.warning(
        "Some machines require maintenance attention."
    )

else:

    st.error(
        "Critical machine failures detected. Immediate intervention is required."
    )

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

end_page()