import streamlit as st
import pandas as pd
import numpy as np


def show_live_charts():
    """
    Displays simulated live charts for industrial monitoring.
    Later replaced with real sensor + ML prediction data.
    """

    st.subheader("📈 Live System Monitoring")

    # Simulated time series data
    time = pd.date_range("now", periods=50, freq="S")

    vibration = np.random.normal(50, 5, 50)
    temperature = np.random.normal(70, 3, 50)
    pressure = np.random.normal(100, 8, 50)

    df = pd.DataFrame({
        "Time": time,
        "Vibration": vibration,
        "Temperature": temperature,
        "Pressure": pressure
    })

    df = df.set_index("Time")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔵 Vibration Levels")
        st.line_chart(df["Vibration"])

    with col2:
        st.markdown("### 🔥 Temperature Trends")
        st.line_chart(df["Temperature"])

    st.markdown("### ⚙️ Pressure Monitoring")
    st.line_chart(df["Pressure"])

    st.divider()