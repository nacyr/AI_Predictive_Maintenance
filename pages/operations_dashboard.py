import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
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

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Operations Dashboard",
    page_icon="⚙️",
    layout="wide"
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="operations_dashboard_refresh"
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
    "Operations Engineer"
]

if user["role"] not in allowed_roles:

    st.error("Access Denied.")

    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "⚙️ Operations Dashboard",
    "Enterprise Operations Monitoring Center"
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
# LIVE SENSOR SIMULATION
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

    records.append({

        "Machine": machine,
        "Temperature (°C)": round(sensor["temperature"],2),
        "Pressure (bar)": round(sensor["pressure"],2),
        "Vibration": round(sensor["vibration"],2),
        "Current (A)": round(sensor["current"],2),
        "RPM": int(sensor["rpm"]),
        "Running Hours": sensor["running_hours"],
        "Prediction": "Failure" if prediction else "Normal",
        "Risk (%)": round(probability*100,2)

    })

sensor_df = pd.DataFrame(records)

# ==========================================================
# KPI CALCULATIONS
# ==========================================================

high = (sensor_df["Risk (%)"] >= 70).sum()

medium = (

    (sensor_df["Risk (%)"] >= 40)
    &
    (sensor_df["Risk (%)"] < 70)

).sum()

low = (

    sensor_df["Risk (%)"] < 40

).sum()

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

st.subheader("📊 Operations Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Machines",
    len(sensor_df)
)

c2.metric(
    "High Risk",
    high
)

c3.metric(
    "Medium Risk",
    medium
)

c4.metric(
    "Low Risk",
    low
)

st.divider()

# ==========================================================
# LIVE SENSOR TABLE
# ==========================================================

st.subheader("📡 Live Machine Monitoring")

st.dataframe(

    sensor_df,

    width="stretch",

    hide_index=True

)

st.divider()

# ==========================================================
# PLANT STATUS
# ==========================================================

left, right = st.columns([2,1])

with left:

    st.subheader("🏭 Plant Status")

    if plant_df.empty:

        st.info("No plant information available.")

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
# ALERT CENTER
# ==========================================================

st.subheader("🚨 Operations Alert Center")

alerts = sensor_df[
    sensor_df["Risk (%)"] >= 70
]

if alerts.empty:

    st.success(
        "No critical machines detected."
    )

else:

    st.error(
        f"{len(alerts)} high-risk machine(s) require immediate attention."
    )

    st.dataframe(
        alerts,
        width="stretch",
        hide_index=True
    )

st.divider()

# ==========================================================
# FAILURE RISK CHART
# ==========================================================

st.subheader("📈 AI Failure Risk Analysis")

fig = go.Figure()

fig.add_trace(

    go.Bar(

        x=sensor_df["Machine"],
        y=sensor_df["Risk (%)"],
        text=sensor_df["Risk (%)"],
        textposition="outside",
        name="Failure Risk"

    )

)

fig.update_layout(

    title="Machine Failure Probability",

    xaxis_title="Machine",

    yaxis_title="Failure Risk (%)",

    height=450

)

st.plotly_chart(
    fig,
    width="stretch"
)

st.divider()

# ==========================================================
# MACHINE HEALTH SUMMARY
# ==========================================================

st.subheader("🏭 Machine Health Summary")

summary = sensor_df.copy()

summary["Health Score (%)"] = (
    100 - summary["Risk (%)"]
).clip(lower=0)

st.dataframe(

    summary[
        [
            "Machine",
            "Prediction",
            "Risk (%)",
            "Health Score (%)"
        ]
    ],

    width="stretch",

    hide_index=True

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
        "📈 Analytics",
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

    if user["role"] == "Administrator":

        if st.button(
            "🏭 Admin Dashboard",
            width="stretch"
        ):
            st.switch_page(
                "pages/admin_dashboard.py"
            )

    else:

        st.button(
            "🏭 Admin Dashboard",
            disabled=True,
            width="stretch"
        )

st.divider()

# ==========================================================
# SYSTEM HEALTH
# ==========================================================

st.subheader("🟢 Operations Status")

if high == 0:

    st.success(
        "All monitored machines are operating normally."
    )

elif high <= 2:

    st.warning(
        f"{high} machine(s) require inspection."
    )

else:

    st.error(
        f"{high} machine(s) require immediate maintenance."
    )

if warning > 0:

    st.info(
        f"{warning} plant unit(s) are currently under observation."
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

Dashboard: **Operations Monitoring**

Auto Refresh: **10 Seconds**

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
    "Operations Dashboard • Enterprise Edition"
)