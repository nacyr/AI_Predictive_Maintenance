import streamlit as st
import pandas as pd

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation
from utils.simulator import generate_sensor_data

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
                sensor["temperature"] * 0.40 +
                sensor["vibration"] * 15 +
                sensor["pressure"] * 2
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

        "Temperature (°C)": sensor["temperature"],

        "Pressure (bar)": sensor["pressure"],

        "Vibration": sensor["vibration"],

        "Current (A)": sensor["current"],

        "RPM": sensor["rpm"],

        "Running Hours": sensor["running_hours"],

        "Failure Risk (%)": risk,

        "Status": status
    })

machine_df = pd.DataFrame(records)

# ==========================================================
# KPI SECTION
# ==========================================================

st.subheader("📊 Operations Overview")

high = (machine_df["Failure Risk (%)"] >= 70).sum()

medium = (
    (machine_df["Failure Risk (%)"] >= 40)
    &
    (machine_df["Failure Risk (%)"] < 70)
).sum()

low = (
    machine_df["Failure Risk (%)"] < 40
).sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Machines", len(machine_df))
c2.metric("High Risk", high)
c3.metric("Medium Risk", medium)
c4.metric("Low Risk", low)

st.divider()

# ==========================================================
# LIVE MACHINE TABLE
# ==========================================================

st.subheader("🏭 Live Machine Monitoring")

st.dataframe(
    machine_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# FAILURE RISK CHART
# ==========================================================

st.subheader("📈 Failure Risk")

st.bar_chart(
    machine_df.set_index("Machine")["Failure Risk (%)"]
)

st.divider()

# ==========================================================
# HEALTH SUMMARY
# ==========================================================

st.subheader("💚 Machine Health")

health_df = machine_df.copy()

health_df["Health (%)"] = (
    100 - health_df["Failure Risk (%)"]
).clip(lower=0)

st.dataframe(
    health_df[
        [
            "Machine",
            "Health (%)",
            "Failure Risk (%)",
            "Status"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# ALERT CENTER
# ==========================================================

st.subheader("🚨 Alert Center")

alerts = machine_df[
    machine_df["Failure Risk (%)"] >= 70
]

if alerts.empty:

    st.success(
        "No critical machines detected."
    )

else:

    st.error(
        f"{len(alerts)} critical machine(s) detected."
    )

    st.dataframe(
        alerts,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# SYSTEM STATUS
# ==========================================================

st.subheader("🟢 System Status")

if alerts.empty:

    st.success(
        "Plant operating within normal conditions."
    )

elif len(alerts) <= 2:

    st.warning(
        "Some machines require maintenance attention."
    )

else:

    st.error(
        "Critical maintenance intervention required."
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

    st.info(f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}
""")

with right:

    st.info("""
**Dashboard:** Operations Dashboard

**Monitoring:** Live

**Refresh:** Automatic
""")

# ==========================================================
# END PAGE
# ==========================================================

end_page()