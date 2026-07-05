import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

# ==========================================================
# OPTIONAL AUTO REFRESH (SAFE IMPORT)
# ==========================================================
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=10000, key="engineer_dashboard_refresh")
except Exception:
    pass

# ==========================================================
# PROJECT ROOT
# ==========================================================

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# ==========================================================
# IMPORTS (SAFE LOADING)
# ==========================================================

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer

from utils.simulator import generate_sensor_data
from utils.plant import plant_status
from ml.predict import predict_failure

from database.work_orders import (
    get_work_orders,
    change_work_order_status   # ✅ FIXED (was wrong before)
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Engineer Dashboard",
    page_icon="🔧",
    layout="wide"
)

# ==========================================================
# AUTH CHECK
# ==========================================================

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

allowed_roles = ["Administrator", "Maintenance Engineer", "Engineer"]

if user["role"] not in allowed_roles:
    st.error("Access Denied")
    st.stop()

# ==========================================================
# UI HEADER
# ==========================================================

show_header(
    user,
    "🔧 Engineer Dashboard",
    "Maintenance & Diagnostics Center"
)

show_sidebar(user)

# ==========================================================
# LOAD DATA SAFELY
# ==========================================================

try:
    orders = get_work_orders()
except Exception:
    orders = pd.DataFrame()

try:
    plants = plant_status()
except Exception:
    plants = pd.DataFrame()
    # ==========================================================
# KPI CALCULATIONS (SAFE)
# ==========================================================

total_orders = len(orders)

pending = 0
approved = 0
completed = 0
rejected = 0

if not orders.empty and "status" in orders.columns:

    pending = (orders["status"] == "PENDING").sum()
    approved = (orders["status"] == "APPROVED").sum()
    completed = (orders["status"] == "COMPLETED").sum()
    rejected = (orders["status"] == "REJECTED").sum()

# ==========================================================
# PLANT STATUS COUNTERS (SAFE)
# ==========================================================

critical_assets = 0
warning_assets = 0
normal_assets = 0

if not plants.empty and "Status" in plants.columns:

    status = plants["Status"].astype(str)

    normal_assets = status.str.contains(
        "NORMAL", case=False, na=False
    ).sum()

    warning_assets = status.str.contains(
        "WARNING", case=False, na=False
    ).sum()

    critical_assets = status.str.contains(
        "CRITICAL", case=False, na=False
    ).sum()

# ==========================================================
# KPI DASHBOARD UI
# ==========================================================

st.subheader("📊 Maintenance Operations Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Work Orders", total_orders)
c2.metric("Pending", pending)
c3.metric("Completed", completed)
c4.metric("Critical Assets", critical_assets)

st.divider()

# ==========================================================
# PLANT STATUS SECTION
# ==========================================================

left, right = st.columns([2, 1])

with left:

    st.subheader("🏭 Live Plant Status")

    if plants.empty:
        st.info("No plant data available.")
    else:
        st.dataframe(
            plants,
            width="stretch",
            hide_index=True
        )

with right:

    st.subheader("📋 Work Order Summary")

    if orders.empty:
        st.info("No work orders available.")
    else:
        summary = (
            orders["status"]
            .value_counts()
            .reset_index()
        )

        summary.columns = ["Status", "Count"]

        st.dataframe(
            summary,
            width="stretch",
            hide_index=True
        )

st.divider()
# ==========================================================
# LIVE AI MACHINE MONITORING (SAFE + STABLE)
# ==========================================================

st.subheader("🤖 AI Machine Monitoring")

machines = [
    "Pump A1",
    "Compressor B2",
    "Generator C3",
    "Motor D4",
    "Cooling Unit E5"
]

records = []

for machine in machines:

    try:
        sensor = generate_sensor_data()

        prediction, probability = predict_failure(
            sensor["temperature"],
            sensor["pressure"],
            sensor["vibration"],
            sensor["current"],
            sensor["rpm"],
            sensor["running_hours"]
        )

        # safety check
        probability = float(probability)

        # auto work order trigger (safe call)
        try:
            from database.work_orders import create_work_order_from_prediction

            create_work_order_from_prediction(
                machine=machine,
                risk_score=probability,
                sensor_data=sensor
            )
        except Exception:
            pass

        records.append({
            "Machine": machine,
            "Temperature (°C)": round(sensor["temperature"], 2),
            "Pressure (bar)": round(sensor["pressure"], 2),
            "Vibration": round(sensor["vibration"], 2),
            "Current (A)": round(sensor["current"], 2),
            "RPM": int(sensor["rpm"]),
            "Prediction": "Failure" if prediction else "Normal",
            "Risk (%)": round(probability * 100, 2)
        })

    except Exception:
        # prevents dashboard crash if ML fails
        continue


# convert safely
monitor_df = pd.DataFrame(records)

if monitor_df.empty:
    st.warning("No sensor data available.")
    st.stop()

# ==========================================================
# DISPLAY TABLE
# ==========================================================

st.dataframe(
    monitor_df,
    width="stretch",
    hide_index=True
)

# ==========================================================
# RISK CHART
# ==========================================================

st.subheader("📈 Machine Failure Risk")

st.bar_chart(
    monitor_df.set_index("Machine")["Risk (%)"]
)

# ==========================================================
# HIGH RISK ALERTS
# ==========================================================

high_risk = monitor_df[monitor_df["Risk (%)"] >= 70]

if high_risk.empty:
    st.success("No high-risk machines detected.")
else:
    st.error(f"{len(high_risk)} machine(s) require attention.")

    st.dataframe(
        high_risk,
        width="stretch",
        hide_index=True
    )

st.divider()
# ==========================================================
# WORK ORDER STATUS MANAGEMENT (SAFE)
# ==========================================================

st.subheader("🛠 Work Order Management")

if orders.empty:
    st.info("No work orders available.")
else:

    editable = orders[orders["status"] != "COMPLETED"]

    if editable.empty:
        st.success("All work orders are completed.")
    else:

        # FIX: unique keys to avoid StreamlitDuplicateElementId
        selected_id = st.selectbox(
            "Select Work Order ID",
            editable["id"].tolist(),
            key="wo_select_engineer"
        )

        new_status = st.selectbox(
            "Update Status",
            ["PENDING", "APPROVED", "COMPLETED", "REJECTED"],
            key="wo_status_engineer"
        )

        if st.button("Update Work Order", key="update_btn_engineer"):

            try:
                from database.work_orders import change_work_order_status

                change_work_order_status(selected_id, new_status)

                st.success(f"Work Order #{selected_id} updated to {new_status}")
                st.rerun()

            except Exception as e:
                st.error(f"Update failed: {str(e)}")

st.divider()

# ==========================================================
# APPROVED WORK ORDERS
# ==========================================================

st.subheader("✔ Approved Work Orders")

if not orders.empty:

    approved = orders[orders["status"] == "APPROVED"]

    if approved.empty:
        st.info("No approved work orders.")
    else:
        st.dataframe(
            approved,
            width="stretch",
            hide_index=True
        )

st.divider()

# ==========================================================
# ENGINEER NOTES (FIXED)
# ==========================================================

st.subheader("📝 Engineer Notes")

notes = st.text_area(
    "Write maintenance notes",
    height=150,
    key="engineer_notes_box"
)

if st.button("Save Notes", key="save_notes_engineer"):

    if notes.strip():
        st.success("Notes saved successfully (demo mode).")
    else:
        st.warning("Please write something before saving.")

st.divider()

# ==========================================================
# QUICK NAVIGATION (FIXED DUPLICATE IDS)
# ==========================================================

st.subheader("⚡ Quick Navigation")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.button(
        "🤖 Prediction",
        on_click=lambda: st.switch_page("pages/prediction.py"),
        key="nav_pred_engineer"
    )

with c2:
    st.button(
        "📈 Analytics",
        on_click=lambda: st.switch_page("pages/analytics.py"),
        key="nav_analytics_engineer"
    )

with c3:
    st.button(
        "🛠 Work Orders",
        on_click=lambda: st.switch_page("pages/maintenance_work_orders.py"),
        key="nav_work_engineer"
    )

with c4:
    st.button(
        "🏠 Dashboard",
        on_click=lambda: st.switch_page("app.py"),
        key="nav_home_engineer"
    )

st.divider()

# ==========================================================
# SYSTEM STATUS (FINAL SECTION)
# ==========================================================

st.subheader("🟢 System Health")

if "high_risk" in locals() and len(high_risk) == 0:
    st.success("All machines are operating normally.")
elif "high_risk" in locals() and len(high_risk) <= 2:
    st.warning("Some machines require inspection.")
else:
    st.error("Immediate maintenance required.")

# ==========================================================
# FOOTER
# ==========================================================

show_footer()

st.caption(
    "Engineer Dashboard • Industrial AI Predictive Maintenance System"
)