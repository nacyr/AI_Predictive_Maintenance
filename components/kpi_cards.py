import streamlit as st
import random


def show_kpi_cards():
    """
    Displays key performance indicators (KPIs)
    for industrial predictive maintenance dashboard.
    """

    st.subheader("📊 System KPIs")

    col1, col2, col3, col4 = st.columns(4)

    # Simulated real-time values (later replaced with ML outputs / database)
    machine_health = random.randint(70, 100)
    active_alerts = random.randint(0, 5)
    downtime_risk = random.randint(0, 40)
    efficiency = random.randint(75, 99)

    with col1:
        st.metric(
            label="🟢 Machine Health",
            value=f"{machine_health}%",
            delta="+2%" if machine_health > 85 else "-3%"
        )

    with col2:
        st.metric(
            label="🚨 Active Alerts",
            value=active_alerts,
            delta="-1" if active_alerts > 0 else "0"
        )

    with col3:
        st.metric(
            label="⚠️ Downtime Risk",
            value=f"{downtime_risk}%",
            delta="+5%" if downtime_risk > 25 else "-2%"
        )

    with col4:
        st.metric(
            label="⚙️ Efficiency",
            value=f"{efficiency}%",
            delta="+3%" if efficiency > 85 else "-1%"
        )

    st.divider()