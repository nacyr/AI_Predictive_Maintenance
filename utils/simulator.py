import random


# ==========================================================
# SENSOR SIMULATOR
# ==========================================================

def generate_sensor_data():

    return {

        "temperature": round(random.uniform(45, 85), 2),

        "pressure": round(random.uniform(6.5, 9.5), 2),

        "vibration": round(random.uniform(0.8, 4.2), 2),

        "current": round(random.uniform(18, 55), 2),

        "rpm": random.randint(1400, 3200),

        "running_hours": random.randint(100, 15000)

    }


# ==========================================================
# AI FAILURE RISK CALCULATION
# ==========================================================

def calculate_failure_risk(sensor):

    # -------------------------------
    # Temperature
    # -------------------------------

    temp_score = max(
        0,
        sensor["temperature"] - 50
    ) * 1.2

    # -------------------------------
    # Vibration
    # -------------------------------

    vibration_score = max(
        0,
        sensor["vibration"] - 2.0
    ) * 12

    # -------------------------------
    # Pressure
    # -------------------------------

    pressure_score = abs(
        sensor["pressure"] - 8
    ) * 4

    # -------------------------------
    # Electrical Current
    # -------------------------------

    current_score = max(
        0,
        sensor["current"] - 35
    ) * 0.8

    # -------------------------------
    # Running Hours (Machine Age)
    # -------------------------------

    running_hour_score = max(
        0,
        sensor["running_hours"] - 5000
    ) / 500

    # -------------------------------
    # Final AI Risk Score
    # -------------------------------

    risk = round(

        min(

            100,

            temp_score
            + vibration_score
            + pressure_score
            + current_score
            + running_hour_score

        ),

        1

    )

    return risk


# ==========================================================
# MACHINE STATUS
# ==========================================================

def get_machine_status(risk):

    if risk >= 80:

        return "CRITICAL"

    elif risk >= 55:

        return "WARNING"

    else:

        return "NORMAL"