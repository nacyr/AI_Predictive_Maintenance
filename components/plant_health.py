import streamlit as st
import pandas as pd


def show_plant_health(machine_df: pd.DataFrame):
    """
    Enterprise Plant Health Summary

    Expected columns:
        - Machine
        - Failure Risk (%)
    """

    st.subheader("🏭 Plant Health Overview")

    if machine_df is None or machine_df.empty:
        st.info("No machine data available.")
        return

    high = (machine_df["Failure Risk (%)"] >= 70).sum()

    medium = (
        (machine_df["Failure Risk (%)"] >= 40)
        &
        (machine_df["Failure Risk (%)"] < 70)
    ).sum()

    low = (
        machine_df["Failure Risk (%)"] < 40
    ).sum()

    total = len(machine_df)

    health = max(
        0,
        round((1 - (high / total)) * 100)
    ) if total else 100

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "🏭 Machines",
        total
    )

    c2.metric(
        "🟢 Healthy",
        low
    )

    c3.metric(
        "🟡 Warning",
        medium
    )

    c4.metric(
        "🔴 Critical",
        high
    )

    c5.metric(
        "💚 Plant Health",
        f"{health}%"
    )

    st.progress(health / 100)

    if health >= 90:

        st.success(
            "Plant is operating normally."
        )

    elif health >= 70:

        st.warning(
            "Plant is operational but requires attention."
        )

    else:

        st.error(
            "Critical plant condition detected."
        )