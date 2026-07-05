import pandas as pd

from utils.simulator import generate_sensor_data
from ml.predict import predict_failure


# ==========================================================
# DEFAULT MACHINES
# ==========================================================

DEFAULT_MACHINES = [
    "Pump A1",
    "Compressor B2",
    "Generator C3",
    "Motor D4",
    "Cooling Unit E5"
]


# ==========================================================
# GENERATE LIVE MACHINE DATA
# ==========================================================

def generate_machine_data(machines=None):
    """
    Generate live sensor readings together with AI predictions.

    Returns:
        pandas.DataFrame
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
            "Running Hours": sensor["running_hours"],
            "Prediction": "Failure" if prediction else "Normal",
            "Failure Risk (%)": round(probability * 100, 2),
            "Health (%)": health,
            "Status": status,
        })

    return pd.DataFrame(records)


# ==========================================================
# FILTERS
# ==========================================================

def get_critical_machines(machine_df):
    if machine_df.empty:
        return machine_df

    return machine_df[
        machine_df["Failure Risk (%)"] >= 70
    ]


def get_warning_machines(machine_df):
    if machine_df.empty:
        return machine_df

    return machine_df[
        (machine_df["Failure Risk (%)"] >= 40)
        &
        (machine_df["Failure Risk (%)"] < 70)
    ]


def get_normal_machines(machine_df):
    if machine_df.empty:
        return machine_df

    return machine_df[
        machine_df["Failure Risk (%)"] < 40
    ]


# ==========================================================
# COUNTS
# ==========================================================

def machine_summary(machine_df):
    """
    Returns a dictionary of machine health statistics.
    """

    if machine_df.empty:

        return {
            "total": 0,
            "critical": 0,
            "warning": 0,
            "normal": 0,
            "average_health": 0,
            "average_risk": 0,
        }

    return {
        "total": len(machine_df),
        "critical": len(get_critical_machines(machine_df)),
        "warning": len(get_warning_machines(machine_df)),
        "normal": len(get_normal_machines(machine_df)),
        "average_health": round(
            machine_df["Health (%)"].mean(),
            1,
        ),
        "average_risk": round(
            machine_df["Failure Risk (%)"].mean(),
            1,
        ),
    }