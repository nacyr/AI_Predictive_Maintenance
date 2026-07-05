import pandas as pd

from database.work_orders import get_work_orders
from utils.plant import plant_status
from utils.simulator import generate_sensor_data
from ml.predict import predict_failure


# ==========================================================
# LOAD WORK ORDERS
# ==========================================================

def load_work_orders():

    try:

        df = get_work_orders()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:

        return pd.DataFrame()


# ==========================================================
# LOAD PLANT STATUS
# ==========================================================

def load_plant_status():

    try:

        df = plant_status()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:

        return pd.DataFrame()
    # ==========================================================
# LIVE MACHINE MONITORING
# ==========================================================

DEFAULT_MACHINES = [
    "Pump A1",
    "Compressor B2",
    "Generator C3",
    "Motor D4",
    "Cooling Unit E5"
]


def generate_machine_data(machines=None):
    """
    Generate simulated sensor data and AI predictions
    for all machines.
    """

    if machines is None:
        machines = DEFAULT_MACHINES

    records = []

    for machine in machines:

        sensor = generate_sensor_data()

        prediction, probability = predict_failure(
            sensor["temperature"],
            sensor["pressure"],
            sensor["vibration"],
            sensor["current"],
            sensor["rpm"],
            sensor["running_hours"]
        )

        health = round((1 - probability) * 100, 1)

        if probability >= 0.70:
            status = "Critical"

        elif probability >= 0.40:
            status = "Warning"

        else:
            status = "Normal"

        records.append({

            "Machine": machine,

            "Temperature (°C)": round(sensor["temperature"], 2),

            "Pressure (bar)": round(sensor["pressure"], 2),

            "Vibration": round(sensor["vibration"], 2),

            "Current (A)": round(sensor["current"], 2),

            "RPM": int(sensor["rpm"]),

            "Running Hours": round(
                sensor["running_hours"],
                1
            ),

            "Prediction": (
                "Failure"
                if prediction
                else "Normal"
            ),

            "Failure Risk (%)": round(
                probability * 100,
                2
            ),

            "Health (%)": health,

            "Status": status

        })

    return pd.DataFrame(records)
# ==========================================================
# WORK ORDER KPI
# ==========================================================

def work_order_summary(orders):
    """
    Calculate work order statistics.
    """

    if orders is None or orders.empty:

        return {
            "total": 0,
            "pending": 0,
            "approved": 0,
            "completed": 0,
            "rejected": 0,
        }

    status = orders["status"].astype(str).str.upper()

    return {

        "total": len(orders),

        "pending": (status == "PENDING").sum(),

        "approved": (status == "APPROVED").sum(),

        "completed": (status == "COMPLETED").sum(),

        "rejected": (status == "REJECTED").sum()

    }


# ==========================================================
# MACHINE KPI
# ==========================================================

def machine_summary(machine_df):
    """
    Calculate live machine statistics.
    """

    if machine_df is None or machine_df.empty:

        return {

            "machines": 0,
            "normal": 0,
            "warning": 0,
            "critical": 0,
            "avg_health": 0,
            "avg_risk": 0

        }

    status = machine_df["Status"].astype(str)

    return {

        "machines": len(machine_df),

        "normal": status.str.contains(
            "Normal",
            case=False,
            na=False
        ).sum(),

        "warning": status.str.contains(
            "Warning",
            case=False,
            na=False
        ).sum(),

        "critical": status.str.contains(
            "Critical",
            case=False,
            na=False
        ).sum(),

        "avg_health": round(
            machine_df["Health (%)"].mean(),
            1
        ),

        "avg_risk": round(
            machine_df["Failure Risk (%)"].mean(),
            1
        )

    }


# ==========================================================
# PLANT KPI
# ==========================================================

def plant_summary(plants):
    """
    Calculate plant status statistics.
    """

    if plants is None or plants.empty:

        return {
            "normal": 0,
            "warning": 0,
            "critical": 0
        }

    if "Status" not in plants.columns:

        return {
            "normal": 0,
            "warning": 0,
            "critical": 0
        }

    status = plants["Status"].astype(str)

    return {

        "normal": status.str.contains(
            "NORMAL",
            case=False,
            na=False
        ).sum(),

        "warning": status.str.contains(
            "WARNING",
            case=False,
            na=False
        ).sum(),

        "critical": status.str.contains(
            "CRITICAL",
            case=False,
            na=False
        ).sum()

    }
