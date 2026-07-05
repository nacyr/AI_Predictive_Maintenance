import sys
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd
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
from ml.predict import predict_failure
from utils.recommendation import maintenance_recommendation

from database.predictions import save_prediction
from database.work_orders import create_work_order_from_prediction

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Prediction Engine",
    page_icon="🔮",
    layout="wide"
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="prediction_refresh"
)

# ==========================================================
# LOGIN CHECK
# ==========================================================

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Please login first.")
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "🔮 AI Failure Prediction",
    "Real-Time Predictive Maintenance Engine"
)

show_sidebar(user)

# ==========================================================
# MACHINE SELECTION
# ==========================================================

machine = st.selectbox(
    "Select Machine",
    [
        "Pump A1",
        "Compressor B2",
        "Generator C3",
        "Motor D4",
        "Cooling System E5"
    ]
)

# ==========================================================
# LIVE SENSOR DATA
# ==========================================================

sensor = generate_sensor_data()

prediction, probability = predict_failure(
    sensor["temperature"],
    sensor["pressure"],
    sensor["vibration"],
    sensor["current"],
    sensor["rpm"],
    sensor["running_hours"]
)

risk_level, recommendation = maintenance_recommendation(
    prediction,
    probability
)

health = max(0, (1 - probability) * 100)
remaining_life = int(health * 10)

# ==========================================================
# SAVE PREDICTION
# ==========================================================

try:

    save_prediction(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        machine,
        sensor["temperature"],
        sensor["pressure"],
        sensor["vibration"],
        sensor["current"],
        sensor["rpm"],
        sensor["running_hours"],
        probability,
        health,
        remaining_life,
        recommendation
    )

except Exception:
    pass

# ==========================================================
# AUTO CREATE WORK ORDER
# ==========================================================

try:

    create_work_order_from_prediction(
        machine,
        probability,
        sensor
    )

except Exception:
    pass

# ==========================================================
# KPI CARDS
# ==========================================================

st.subheader("AI Prediction Results")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Prediction",
    "FAILURE" if prediction else "NORMAL"
)

c2.metric(
    "Failure Risk",
    f"{probability*100:.2f}%"
)

c3.metric(
    "Machine Health",
    f"{health:.1f}%"
)

c4.metric(
    "Remaining Life",
    f"{remaining_life} hrs"
)

st.divider()

# ==========================================================
# SENSOR TABLE
# ==========================================================

st.subheader("📡 Live Sensor Values")

sensor_df = pd.DataFrame({
    "Sensor":[
        "Temperature",
        "Pressure",
        "Vibration",
        "Current",
        "RPM",
        "Running Hours"
    ],
    "Value":[
        sensor["temperature"],
        sensor["pressure"],
        sensor["vibration"],
        sensor["current"],
        sensor["rpm"],
        sensor["running_hours"]
    ]
})

st.dataframe(
    sensor_df,
    width="stretch",
    hide_index=True
)

st.divider()

# ==========================================================
# HEALTH GAUGE
# ==========================================================

st.subheader("Machine Health")

fig = go.Figure(go.Indicator(

    mode="gauge+number",

    value=health,

    title={"text":"Health %"},

    gauge={
        "axis":{"range":[0,100]},
        "bar":{"color":"green"},
        "steps":[
            {"range":[0,40],"color":"red"},
            {"range":[40,70],"color":"orange"},
            {"range":[70,100],"color":"lightgreen"}
        ]
    }
))

st.plotly_chart(
    fig,
    width="stretch"
)

st.divider()

# ==========================================================
# RISK ANALYSIS
# ==========================================================

st.subheader("Maintenance Recommendation")

if risk_level == "LOW":
    st.success(recommendation)

elif risk_level == "MEDIUM":
    st.warning(recommendation)

else:
    st.error(recommendation)

# ==========================================================
# TECHNICAL SUMMARY
# ==========================================================

st.subheader("Prediction Summary")

summary = pd.DataFrame({

    "Metric":[
        "Machine",
        "Prediction",
        "Failure Probability",
        "Health",
        "Remaining Life",
        "Recommendation"
    ],

    "Value":[
        machine,
        "FAILURE" if prediction else "NORMAL",
        f"{probability*100:.2f}%",
        f"{health:.1f}%",
        f"{remaining_life} hrs",
        recommendation
    ]
})

st.dataframe(
    summary,
    width="stretch",
    hide_index=True
)

# ==========================================================
# FOOTER
# ==========================================================

show_footer()