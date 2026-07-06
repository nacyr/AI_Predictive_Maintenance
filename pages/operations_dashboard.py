import streamlit as st
import pandas as pd

from streamlit_autorefresh import st_autorefresh

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation
from utils.simulator import generate_sensor_data

from components.live_status import show_live_status
from components.kpi_cards import show_kpi_cards
from components.live_machine_table import show_live_machine_table
from components.plant_health import show_plant_health
from components.alert_center import show_alert_center

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="⚙️ Operations Dashboard",
    icon="⚙️",
    subtitle="Enterprise Operations Monitoring Center",
    allowed_roles=[
        "Administrator",
        "Operations Engineer"
    ]
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

refresh_count = st_autorefresh(
    interval=10000,
    key="operations_dashboard_refresh"
)

show_live_status(refresh_count)

st.divider()

# ==========================================================
# GENERATE LIVE MACHINE DATA
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

    records.append(

        {

            "Machine": machine,

            "Temperature (°C)": round(sensor["temperature"], 2),

            "Pressure (bar)": round(sensor["pressure"], 2),

            "Vibration": round(sensor["vibration"], 2),

            "Current (A)": round(sensor["current"], 2),

            "RPM": round(sensor["rpm"], 0),

            "Running Hours": sensor["running_hours"],

            "Failure Risk (%)": risk,

            "Status": status,

        }

    )

machine_df = pd.DataFrame(records)

# ==========================================================
# KPI OVERVIEW
# ==========================================================

high = (
    machine_df["Failure Risk (%)"] >= 70
).sum()

medium = (
    (machine_df["Failure Risk (%)"] >= 40)
    &
    (machine_df["Failure Risk (%)"] < 70)
).sum()

low = (
    machine_df["Failure Risk (%)"] < 40
).sum()

plant_health = round(

    (low / len(machine_df)) * 100,

    1

) if len(machine_df) else 100

show_kpi_cards(

    critical=high,

    warning=medium,

    healthy=low,

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

st.subheader("📈 AI Failure Risk Analysis")

risk_chart = (
    machine_df
    .set_index("Machine")["Failure Risk (%)"]
)

st.bar_chart(risk_chart)

st.caption(
    "Live AI prediction of machine failure probability."
)

st.divider()
# ==========================================================
# PLANT HEALTH OVERVIEW
# ==========================================================

show_plant_health(machine_df)

st.divider()

# ==========================================================
# AI ALERT CENTER
# ==========================================================

show_alert_center(machine_df)

st.divider()

# ==========================================================
# OPERATIONS STATUS
# ==========================================================

st.subheader("🟢 Operations Status")

if high == 0:

    st.success(
        "Plant is operating normally. No critical machines detected."
    )

elif high <= 2:

    st.warning(
        f"{high} critical machine(s) require maintenance attention."
    )

else:

    st.error(
        "Critical plant condition detected. Immediate intervention required."
    )

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

quick_navigation(
    prediction=True,
    analytics=True,
    maintenance=True,
    admin=user.get("role") == "Administrator",
    operations=False
)

st.divider()

# ==========================================================
# SESSION INFORMATION
# ==========================================================

st.subheader("👤 Session Information")

left, right = st.columns(2)

with left:

    st.info(
        f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}
"""
    )

with right:

    st.info(
        f"""
**Dashboard:** Operations Dashboard

**Refresh Count:** {refresh_count}

**Refresh Interval:** 10 Seconds
"""
    )

st.divider()

# ==========================================================
# LIVE SUMMARY
# ==========================================================

st.subheader("📡 Live Operations Summary")

c1, c2 = st.columns(2)

with c1:

    st.success(
        f"""
🏭 Machines Monitored: **{len(machine_df)}**

🟢 Healthy: **{low}**

🟡 Warning: **{medium}**

🔴 Critical: **{high}**
"""
    )

with c2:

    st.info(
        f"""
💚 Plant Health: **{plant_health:.1f}%**

🤖 AI Engine: **ACTIVE**

📡 Sensor Network: **ONLINE**

💾 Database: **CONNECTED**
"""
    )

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

end_page()
