import streamlit as st
import pandas as pd

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation

from utils.simulator import generate_sensor_data
from ml.smart_maintenance_engine import predict_failure

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="AI Prediction Dashboard",
    icon="🤖",
    allowed_roles=[
        "Administrator",
        "Maintenance Engineer",
        "Operations Engineer",
        "Supervisor"
    ],
    subtitle="Machine Failure Prediction & Risk Analytics"
)

# ==========================================================
# INTRO
# ==========================================================

st.info(
    "This dashboard is AI-only. It does not create or modify work orders."
)

# ==========================================================
# MACHINE SIMULATION
# ==========================================================

machines = [
    "Pump A1",
    "Compressor B2",
    "Generator C3",
    "Motor D4",
    "Cooling Unit E5"
]

records = []

for m in machines:

    sensor = generate_sensor_data()

    prediction, risk = predict_failure(
        sensor["temperature"],
        sensor["pressure"],
        sensor["vibration"],
        sensor["current"],
        sensor["rpm"],
        sensor["running_hours"]
    )

    records.append({
        "Machine": m,
        "Temperature": round(sensor["temperature"], 2),
        "Pressure": round(sensor["pressure"], 2),
        "Vibration": round(sensor["vibration"], 2),
        "Current": round(sensor["current"], 2),
        "RPM": int(sensor["rpm"]),
        "Running Hours": sensor["running_hours"],
        "Prediction": "FAILURE" if prediction else "NORMAL",
        "Risk (%)": round(risk * 100, 2)
    })

df = pd.DataFrame(records)

# ==========================================================
# KPI SECTION
# ==========================================================

st.subheader("📊 AI Risk Overview")

high = (df["Risk (%)"] >= 70).sum()
medium = ((df["Risk (%)"] >= 40) & (df["Risk (%)"] < 70)).sum()
low = (df["Risk (%)"] < 40).sum()

c1, c2, c3 = st.columns(3)

c1.metric("High Risk", high)
c2.metric("Medium Risk", medium)
c3.metric("Low Risk", low)

st.divider()

# ==========================================================
# FULL PREDICTION TABLE
# ==========================================================

st.subheader("🤖 Machine Failure Predictions")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# RISK VISUALIZATION
# ==========================================================

st.subheader("📈 Risk Analysis")

st.bar_chart(df.set_index("Machine")["Risk (%)"])

st.divider()

# ==========================================================
# HIGH RISK ALERTS (READ ONLY)
# ==========================================================

st.subheader("🚨 High Risk Machines")

high_risk = df[df["Risk (%)"] >= 70]

if high_risk.empty:
    st.success("No high-risk machines detected.")
else:
    st.error(f"{len(high_risk)} machine(s) require attention.")
    st.dataframe(high_risk, use_container_width=True, hide_index=True)

st.divider()

# ==========================================================
# INSIGHTS SECTION
# ==========================================================

st.subheader("🧠 AI Insights")

if high == 0:
    st.success("All machines are currently operating within safe limits.")
elif high <= 2:
    st.warning("Early warning: some machines are approaching failure threshold.")
else:
    st.error("Critical: multiple machines show high failure probability.")

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

quick_navigation(
    prediction=False,
    analytics=True,
    maintenance=True,
    admin=user.get("role") == "Administrator"
)

st.divider()

# ==========================================================
# SESSION INFO
# ==========================================================

st.subheader("👤 Session Information")

st.info(f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}

**Mode:** AI Analysis Only
""")

# ==========================================================
# FOOTER
# ==========================================================

end_page()