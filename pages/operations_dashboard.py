import streamlit as st

from utils.page_config import setup_page, end_page
from utils.dashboard_widgets import (
    generate_machine_data,
    show_machine_table,
    show_machine_health_summary,
    show_system_status
)

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="Operations Dashboard",
    icon="⚙️",
    allowed_roles=[
        "Administrator",
        "Operations Engineer"
    ],
    subtitle="Enterprise Operations Monitoring Center"
)

# ==========================================================
# LIVE MACHINE DATA
# ==========================================================

machine_df = generate_machine_data()

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

show_machine_table(machine_df)

# ==========================================================
# HEALTH SUMMARY
# ==========================================================

show_machine_health_summary(machine_df)

st.divider()

# ==========================================================
# ALERTS
# ==========================================================

st.subheader("🚨 Operations Alert Center")

alerts = machine_df[
    machine_df["Failure Risk (%)"] >= 70
]

if alerts.empty:

    st.success(
        "No critical machines detected."
    )

else:

    st.error(
        f"{len(alerts)} machine(s) require immediate attention."
    )

    st.dataframe(
        alerts,
        use_container_width=True,
        hide_index=True
    )

st.divider()
# ==========================================================
# FAILURE RISK CHART
# ==========================================================

st.subheader("📈 AI Failure Risk Analysis")

chart_df = (
    machine_df
    .set_index("Machine")["Failure Risk (%)"]
)

st.bar_chart(chart_df)

st.divider()

# ==========================================================
# MACHINE HEALTH DETAILS
# ==========================================================

st.subheader("🏭 Machine Health Details")

health_df = machine_df.copy()

health_df["Health (%)"] = (
    100 - health_df["Failure Risk (%)"]
).clip(lower=0)

st.dataframe(
    health_df[
        [
            "Machine",
            "Temperature (°C)",
            "Pressure (bar)",
            "Vibration",
            "Current (A)",
            "RPM",
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
# QUICK NAVIGATION
# ==========================================================

from utils.navigation import quick_navigation

quick_navigation(
    prediction=True,
    analytics=True,
    maintenance=True,
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
**Dashboard:** Operations Dashboard

**Auto Refresh:** Every 10 Seconds
""")

st.divider()

# ==========================================================
# SYSTEM STATUS
# ==========================================================

show_system_status(machine_df)

# ==========================================================
# END PAGE
# ==========================================================

end_page()