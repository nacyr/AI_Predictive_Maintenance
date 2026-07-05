import pandas as pd

from database.work_orders import get_work_orders
from utils.simulator import generate_sensor_data
from ml.smart_maintenance_engine import predict_failure

# ==========================================================
# DATA LOADING
# ==========================================================

def load_work_orders():
    """
    Safe wrapper for work orders.
    Prevents None / crash issues across dashboards.
    """
    try:
        df = get_work_orders()
        if df is None:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


def generate_machine_data():
    """
    Simulated plant machine dataset (used across dashboards).
    """
    machines = ["Pump A1", "Compressor B2", "Generator C3", "Motor D4"]

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
            "Risk (%)": round(risk * 100, 2),
            "Status": "FAILURE" if prediction else "NORMAL"
        })

    return pd.DataFrame(records)

# ==========================================================
# KPI HELPERS
# ==========================================================

def show_work_order_kpis(orders):

    import streamlit as st

    st.subheader("📊 Work Order Overview")

    if orders is None or orders.empty:

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", 0)
        col2.metric("Pending", 0)
        col3.metric("Completed", 0)

        return

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", len(orders))
    col2.metric("Pending", (orders["status"] == "PENDING").sum())
    col3.metric("Completed", (orders["status"] == "COMPLETED").sum())

# ==========================================================
# MACHINE TABLE
# ==========================================================

def show_machine_table(df):

    import streamlit as st

    st.subheader("🏭 Machine Status")

    if df is None or df.empty:
        st.info("No machine data available.")
        return

    st.dataframe(df, use_container_width=True, hide_index=True)

    if "Risk (%)" in df.columns:
        st.bar_chart(df.set_index("Machine")["Risk (%)"])

# ==========================================================
# MACHINE HEALTH SUMMARY
# ==========================================================

def show_machine_health_summary(df):

    import streamlit as st

    st.subheader("📈 Machine Health Summary")

    if df is None or df.empty:
        st.info("No health data available.")
        return

    if "Risk (%)" not in df.columns:
        st.warning("Risk data missing.")
        return

    df = df.copy()
    df["Health (%)"] = 100 - df["Risk (%)"]

    st.dataframe(
        df[["Machine", "Risk (%)", "Health (%)"]],
        use_container_width=True,
        hide_index=True
    )

# ==========================================================
# SYSTEM STATUS
# ==========================================================

def show_system_status(df):

    import streamlit as st

    st.subheader("🟢 System Status")

    if df is None or df.empty:

        st.info("No system data available.")
        return

    high_risk = (df["Risk (%)"] >= 70).sum()

    if high_risk == 0:
        st.success("All systems operating normally.")
    elif high_risk <= 2:
        st.warning(f"{high_risk} machines need attention.")
    else:
        st.error(f"{high_risk} critical machines detected.")