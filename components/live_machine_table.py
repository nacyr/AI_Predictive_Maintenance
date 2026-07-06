import streamlit as st
import pandas as pd


def show_live_machine_table(machine_df: pd.DataFrame):
    """
    Enterprise Live Machine Monitoring Table

    Expected columns

    Machine
    Temperature (°C)
    Pressure (bar)
    Vibration
    Current (A)
    RPM
    Failure Risk (%)
    Status
    """

    st.subheader("🏭 Live Machine Monitoring")

    if machine_df is None or machine_df.empty:

        st.info("No machine data available.")

        return

    df = machine_df.copy()

    # =====================================================
    # HEALTH SCORE
    # =====================================================

    df["Health (%)"] = (
        100 - df["Failure Risk (%)"]
    ).clip(lower=0)

    # =====================================================
    # SORT BY RISK
    # =====================================================

    df = df.sort_values(
        by="Failure Risk (%)",
        ascending=False
    )

    # =====================================================
    # STATUS ICON
    # =====================================================

    def icon(risk):

        if risk >= 70:
            return "🔴 Critical"

        elif risk >= 40:
            return "🟡 Warning"

        return "🟢 Healthy"

    df["Condition"] = df["Failure Risk (%)"].apply(icon)

    # =====================================================
    # DISPLAY
    # =====================================================

    st.dataframe(

        df[
            [
                "Machine",
                "Condition",
                "Health (%)",
                "Failure Risk (%)",
                "Temperature (°C)",
                "Pressure (bar)",
                "Vibration",
                "Current (A)",
                "RPM",
                "Status",
            ]
        ],

        use_container_width=True,

        hide_index=True,
    )

    st.caption(
        "Machines are automatically sorted by highest failure risk."
    )