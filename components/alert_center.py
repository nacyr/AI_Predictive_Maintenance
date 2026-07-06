import streamlit as st
import pandas as pd


def show_alert_center(machine_df: pd.DataFrame):
    """
    Enterprise AI Alert Center

    Expected columns:
        Machine
        Failure Risk (%)
        Status
    """

    st.subheader("🚨 AI Alert Center")

    if machine_df is None or machine_df.empty:

        st.success("No machines are currently being monitored.")

        return

    critical = machine_df[
        machine_df["Failure Risk (%)"] >= 70
    ]

    warning = machine_df[
        (machine_df["Failure Risk (%)"] >= 40)
        &
        (machine_df["Failure Risk (%)"] < 70)
    ]

    healthy = machine_df[
        machine_df["Failure Risk (%)"] < 40
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🔴 Critical",
        len(critical)
    )

    c2.metric(
        "🟡 Warning",
        len(warning)
    )

    c3.metric(
        "🟢 Healthy",
        len(healthy)
    )

    st.divider()

    # =====================================================
    # CRITICAL MACHINES
    # =====================================================

    if not critical.empty:

        st.error(
            f"🚨 {len(critical)} critical machine(s) detected."
        )

        for _, row in critical.iterrows():

            st.error(
                f"""
Machine: {row['Machine']}

Failure Risk: {row['Failure Risk (%)']:.1f}%

Status: {row['Status']}

Recommended Action:
Immediate maintenance inspection required.
"""
            )

    # =====================================================
    # WARNING MACHINES
    # =====================================================

    elif not warning.empty:

        st.warning(
            f"⚠ {len(warning)} machine(s) require observation."
        )

        st.dataframe(
            warning,
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # HEALTHY
    # =====================================================

    else:

        st.success(
            "✅ All monitored machines are operating normally."
        )