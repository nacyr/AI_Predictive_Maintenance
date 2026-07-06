import streamlit as st
import pandas as pd

from streamlit_autorefresh import st_autorefresh

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation
from utils.simulator import generate_sensor_data

from database.work_orders import (
    create_work_order_from_prediction
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
    title="🤖 AI Prediction Dashboard",
    icon="🤖",
    subtitle="Real-Time Predictive Maintenance",
    allowed_roles=[
        "Administrator",
        "Maintenance Engineer",
        "Operations Engineer",
        "Supervisor"
    ]
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

refresh_count = st_autorefresh(
    interval=10000,
    key="prediction_dashboard_refresh"
)

show_live_status(refresh_count)

st.divider()

# ==========================================================
# LIVE MACHINE SIMULATION
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

new_work_orders = 0

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

    probability = risk / 100

    created = create_work_order_from_prediction(
        machine,
        probability,
        sensor
    )

    if created:
        new_work_orders += 1

    if risk >= 70:
        status = "CRITICAL"

    elif risk >= 40:
        status = "WARNING"

    else:
        status = "NORMAL"

    records.append({

        "Machine": machine,

        "Temperature (°C)": round(sensor["temperature"],2),

        "Pressure (bar)": round(sensor["pressure"],2),

        "Vibration": round(sensor["vibration"],2),

        "Current (A)": round(sensor["current"],2),

        "RPM": round(sensor["rpm"],0),

        "Running Hours": sensor["running_hours"],

        "Failure Risk (%)": risk,

        "Status": status

    })

machine_df = pd.DataFrame(records)

# ==========================================================
# KPI CARDS
# ==========================================================

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
    critical=critical,
    warning=warning,
    healthy=healthy,
    plant_health=plant_health
)

st.divider()

# ==========================================================
# LIVE MACHINE TABLE
# ==========================================================

show_live_machine_table(machine_df)

st.divider()

# ==========================================================
# AI PREDICTION CHART
# ==========================================================

st.subheader("🤖 AI Failure Probability")

st.bar_chart(
    machine_df.set_index("Machine")["Failure Risk (%)"]
)

st.caption(
    "Predicted probability of equipment failure."
)

st.divider()
# ==========================================================
# AI DECISION SUMMARY
# ==========================================================

st.subheader("🧠 AI Decision Summary")

if critical == 0:

    st.success(
        "AI analysis indicates that all monitored machines are operating within acceptable limits."
    )

elif critical <= 2:

    st.warning(
        f"AI detected {critical} machine(s) with high failure probability."
    )

else:

    st.error(
        "AI has detected multiple critical machines. Immediate maintenance planning is recommended."
    )

st.divider()

# ==========================================================
# PLANT HEALTH
# ==========================================================

show_plant_health(machine_df)

st.divider()

# ==========================================================
# AI ALERT CENTER
# ==========================================================

show_alert_center(machine_df)

st.divider()

# ==========================================================
# AUTOMATIC WORK ORDERS
# ==========================================================

st.subheader("📋 AI Work Order Generator")

if new_work_orders == 0:

    st.success(
        "No new AI work orders were generated during this monitoring cycle."
    )

else:

    st.warning(
        f"{new_work_orders} new AI work order(s) were automatically created."
    )

st.divider()

# ==========================================================
# MACHINE RANKING
# ==========================================================

st.subheader("🏆 Highest Risk Machines")

ranking = (
    machine_df
    .sort_values(
        "Failure Risk (%)",
        ascending=False
    )
)

st.dataframe(

    ranking[
        [
            "Machine",
            "Failure Risk (%)",
            "Status"
        ]
    ],

    use_container_width=True,

    hide_index=True

)

st.divider()

# ==========================================================
# LIVE AI SUMMARY
# ==========================================================

st.subheader("📡 Live AI Monitoring")

left, right = st.columns(2)

with left:

    st.success(f"""
🤖 AI Engine: ACTIVE

🏭 Machines Analysed: {len(machine_df)}

📋 New Work Orders: {new_work_orders}

🔄 Refresh Count: {refresh_count}
""")

with right:

    st.info(f"""
🟢 Healthy: {healthy}

🟡 Warning: {warning}

🔴 Critical: {critical}

💚 Plant Health: {plant_health:.1f}%
""")

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

quick_navigation(

    prediction=False,

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

left, right = st.columns(2)

with left:

    st.info(f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}
""")

with right:

    st.info(f"""
**Dashboard:** AI Prediction

**Refresh Interval:** 10 Seconds

**Refresh Count:** {refresh_count}
""")

st.divider()

# ==========================================================
# END PAGE
# ==========================================================

end_page()