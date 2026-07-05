import streamlit as st
import pandas as pd
import numpy as np


def show_analytics():
    """
    Displays industrial analytics for predictive maintenance.
    Simulates failure trends, risk distribution, and insights.
    """

    st.subheader("🧠 Predictive Analytics")

    # Simulated dataset
    machines = [
        "Pump A1", "Compressor B2", "Generator C3",
        "Turbine D4", "Valve E5", "Cooling F6",
        "Boiler G7", "Motor H8"
    ]

    np.random.seed(42)

    df = pd.DataFrame({
        "Machine": machines,
        "Failure Probability": np.random.randint(5, 95, len(machines)),
        "Wear Level": np.random.randint(10, 100, len(machines)),
        "Efficiency Loss": np.random.randint(0, 50, len(machines))
    })

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚠️ Failure Probability by Machine")
        st.bar_chart(df.set_index("Machine")["Failure Probability"])

    with col2:
        st.markdown("### 🧱 Wear Level Distribution")
        st.bar_chart(df.set_index("Machine")["Wear Level"])

    st.markdown("### 📉 Efficiency Loss Overview")
    st.line_chart(df.set_index("Machine")["Efficiency Loss"])

    # Insight section (simple AI-like interpretation)
    st.markdown("---")
    st.markdown("### 🧠 System Insights")

    highest_risk = df.loc[df["Failure Probability"].idxmax()]

    st.error(
        f"""
🔴 High Risk Alert:
- Machine: {highest_risk['Machine']}
- Failure Probability: {highest_risk['Failure Probability']}%

Immediate inspection recommended.
"""
    )

    avg_risk = df["Failure Probability"].mean()

    if avg_risk > 60:
        st.warning(f"⚠️ System-wide risk is HIGH ({avg_risk:.1f}%)")
    else:
        st.success(f"🟢 System risk is within safe range ({avg_risk:.1f}%)")

    st.divider()