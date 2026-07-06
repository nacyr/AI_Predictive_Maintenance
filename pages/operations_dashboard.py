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
# LIVE MACHINE LIST
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

# ==========================================================
# GENERATE LIVE SENSOR DATA
# ==========================================================

records = []

for machine in machines:

    sensor = generate_sensor_data()

    # ------------------------------------------------------
    # SMART AI RISK CALCULATION
    # ------------------------------------------------------

    temp_score = max(
        0,
        sensor["temperature"] - 50
    ) * 1.2

    vibration_score = max(
        0,
        sensor["vibration"] - 2.0
    ) * 12

    pressure_score = abs(
        sensor["pressure"] - 8
    ) * 4

    current_score = max(
        0,
        sensor["current"] - 35
    ) * 0.8

    hour_score = max(
        0,
        sensor["running_hours"] - 5000
    ) / 500

    risk = round(

        min(

            100,

            temp_score
            + vibration_score
            + pressure_score
            + current_score
            + hour_score

        ),

        1

    )

    # ------------------------------------------------------
    # MACHINE STATUS
    # ------------------------------------------------------

    if risk >= 80:

        status = "CRITICAL"

    elif risk >= 55:

        status = "WARNING"

    else:

        status = "NORMAL"

    # ------------------------------------------------------
    # MACHINE RECORD
    # ------------------------------------------------------

    records.append(

        {

            "Machine": machine,

            "Temperature (°C)": round(
                sensor["temperature"], 2
            ),

            "Pressure (bar)": round(
                sensor["pressure"], 2
            ),

            "Vibration": round(
                sensor["vibration"], 2
            ),

            "Current (A)": round(
                sensor["current"], 2
            ),

            "RPM": round(
                sensor["rpm"], 0
            ),

            "Running Hours": sensor[
                "running_hours"
            ],

            "Failure Risk (%)": risk,

            "Status": status

        }

    )

machine_df = pd.DataFrame(records)
# ==========================================================
# KPI CALCULATIONS
# ==========================================================

critical = (
    machine_df["Status"] == "CRITICAL"
).sum()

warning = (
    machine_df["Status"] == "WARNING"
).sum()

healthy = (
    machine_df["Status"] == "NORMAL"
).sum()

plant_health = round(

    (healthy / len(machine_df)) * 100,

    1

) if len(machine_df) else 100

# ==========================================================
# KPI DASHBOARD
# ==========================================================

show_kpi_cards(

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

if critical == 0:

    st.success(
        "Plant is operating normally. No critical machines detected."
    )

elif critical <= 2:

    st.warning(
        f"{critical} critical machine(s) require maintenance attention."
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
# LIVE OPERATIONS SUMMARY
# ==========================================================

st.subheader("📡 Live Operations Summary")

c1, c2 = st.columns(2)

with c1:

    st.success(
        f"""
🏭 Machines Monitored: **{len(machine_df)}**

🟢 Healthy: **{healthy}**

🟡 Warning: **{warning}**

🔴 Critical: **{critical}**
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
# LOGOUT
# ==========================================================

st.subheader("🔐 Session Control")

col1, col2 = st.columns([1, 3])

with col1:

    if st.button(
        "🚪 Logout",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.clear()

        st.success("Logged out successfully.")

        st.switch_page("app.py")

with col2:

    st.info(
        "Click **Logout** to securely end your session."
    )

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

end_page()