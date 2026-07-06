import streamlit as st
import pandas as pd

from streamlit_autorefresh import st_autorefresh

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation

from utils.simulator import (
    generate_sensor_data,
    calculate_failure_risk,
    get_machine_status
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
# MACHINE FLEET
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
# AI LIVE SENSOR ENGINE
# ==========================================================

records = []


for machine in machines:


    sensor = generate_sensor_data(machine)


    risk = calculate_failure_risk(

        sensor,

        machine

    )


    status = get_machine_status(

        risk

    )


    records.append(

        {

            "Machine": machine,


            "Temperature (°C)": sensor["temperature"],


            "Pressure (bar)": sensor["pressure"],


            "Vibration": sensor["vibration"],


            "Current (A)": sensor["current"],


            "RPM": sensor["rpm"],


            "Running Hours": sensor["running_hours"],


            "Failure Risk (%)": risk,


            "Status": status

        }

    )



machine_df = pd.DataFrame(records)



# ==========================================================
# KPI CALCULATION
# ==========================================================

critical = (

    machine_df["Status"]

    .eq("CRITICAL")

    .sum()

)


warning = (

    machine_df["Status"]

    .eq("WARNING")

    .sum()

)


healthy = (

    machine_df["Status"]

    .eq("NORMAL")

    .sum()

)



plant_health = round(

    (healthy / len(machine_df)) * 100,

    1

) if len(machine_df) else 100



# ==========================================================
# KPI CARDS
# ==========================================================

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

show_live_machine_table(

    machine_df

)



st.divider()



# ==========================================================
# FAILURE RISK ANALYTICS
# ==========================================================

st.subheader(

    "📈 AI Failure Risk Analysis"

)


risk_chart = (

    machine_df

    .set_index("Machine")

    ["Failure Risk (%)"]

)



st.bar_chart(

    risk_chart

)



st.caption(

    "AI engine calculates equipment failure probability using live sensor intelligence."

)



st.divider()



# ==========================================================
# PLANT HEALTH
# ==========================================================

show_plant_health(

    machine_df

)


st.divider()



# ==========================================================
# ALERT CENTER
# ==========================================================

show_alert_center(

    machine_df

)



st.divider()



# ==========================================================
# OPERATIONS STATUS
# ==========================================================

st.subheader(

    "🟢 Operations Status"

)


if critical == 0:

    st.success(

        "Plant operating normally. No critical machines detected."

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

st.subheader(

    "👤 Session Information"

)



left, right = st.columns(2)



with left:

    st.info(

        f"""

**User:** {user.get('fullname','Unknown')}


**Role:** {user.get('role','Unknown')}

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

st.subheader(

    "📡 Live Operations Summary"

)



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

💚 Plant Health: **{plant_health}%**


🤖 AI Engine: **ACTIVE**


📡 Sensor Network: **ONLINE**


💾 Database: **CONNECTED**

"""

    )



st.divider()



# ==========================================================
# LOGOUT
# ==========================================================

st.subheader(

    "🔐 Session Control"

)



if st.button(

    "🚪 Logout",

    use_container_width=True,

    type="primary"

):

    st.session_state.clear()

    st.success(

        "Logged out successfully."

    )

    st.switch_page(

        "app.py"

    )



st.divider()



# ==========================================================
# FOOTER
# ==========================================================

end_page()