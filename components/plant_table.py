import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta


def show_plant_table():
    """
    Displays simulated industrial equipment status table.
    Later replaced with real database + sensor + ML predictions.
    """

    st.subheader("🏭 Plant Equipment Status")

    # Simulated equipment list
    machines = [
        "Pump A1",
        "Compressor B2",
        "Generator C3",
        "Turbine D4",
        "Valve E5",
        "Cooling System F6",
        "Boiler G7",
        "Motor H8"
    ]

    statuses = ["Running", "Warning", "Fault", "Maintenance"]

    data = []

    for machine in machines:
        status = random.choice(statuses)
        health = random.randint(60, 100)
        failure_risk = random.randint(0, 100)
        last_maintenance = datetime.now() - timedelta(days=random.randint(1, 120))

        data.append({
            "Machine": machine,
            "Status": status,
            "Health (%)": health,
            "Failure Risk (%)": failure_risk,
            "Last Maintenance": last_maintenance.strftime("%Y-%m-%d")
        })

    df = pd.DataFrame(data)

    # Styling helper
    def highlight_status(val):
        if val == "Fault":
            return "background-color: red; color: white"
        elif val == "Warning":
            return "background-color: orange; color: black"
        elif val == "Maintenance":
            return "background-color: yellow; color: black"
        else:
            return "background-color: green; color: white"

    styled_df = df.style.applymap(
        highlight_status,
        subset=["Status"]
    )

    st.dataframe(styled_df, use_container_width=True)

    st.divider()