import random

# ==========================================================
# MACHINE MEMORY
# ==========================================================

_machine_state = {}

# ==========================================================
# DEFAULT SENSOR VALUES
# ==========================================================

DEFAULT_SENSOR = {

    "temperature": 58.0,

    "pressure": 8.0,

    "vibration": 1.8,

    "current": 28.0,

    "rpm": 2200,

    "running_hours": 1000

}

# ==========================================================
# RANDOM WALK
# ==========================================================

def drift(value, minimum, maximum, step):

    value += random.uniform(-step, step)

    return round(
        max(minimum, min(maximum, value)),
        2
    )

# ==========================================================
# SENSOR GENERATOR
# ==========================================================

def generate_sensor_data(machine_name="DEFAULT"):

    if machine_name not in _machine_state:

        _machine_state[machine_name] = DEFAULT_SENSOR.copy()

        _machine_state[machine_name]["running_hours"] = random.randint(
            100,
            12000
        )

    sensor = _machine_state[machine_name]

    # ------------------------------------------------------
    # Small realistic changes
    # ------------------------------------------------------

    sensor["temperature"] = drift(
        sensor["temperature"],
        40,
        95,
        2
    )

    sensor["pressure"] = drift(
        sensor["pressure"],
        6,
        10,
        0.25
    )

    sensor["vibration"] = drift(
        sensor["vibration"],
        0.5,
        5,
        0.20
    )

    sensor["current"] = drift(
        sensor["current"],
        15,
        60,
        1.5
    )

    sensor["rpm"] = int(

        drift(
            sensor["rpm"],
            1500,
            3200,
            60
        )

    )

    sensor["running_hours"] += random.randint(1, 5)

    # ------------------------------------------------------
    # Occasionally simulate deterioration
    # ------------------------------------------------------

    if random.random() < 0.15:

        sensor["temperature"] += random.uniform(2, 6)

        sensor["vibration"] += random.uniform(0.2, 0.8)

    # ------------------------------------------------------
    # Occasionally simulate recovery
    # ------------------------------------------------------

    if random.random() < 0.10:

        sensor["temperature"] -= random.uniform(2, 5)

        sensor["vibration"] -= random.uniform(0.2, 0.6)

    # ------------------------------------------------------
    # Clamp values
    # ------------------------------------------------------

    sensor["temperature"] = round(

        max(40, min(95, sensor["temperature"])),

        2

    )

    sensor["pressure"] = round(

        max(6, min(10, sensor["pressure"])),

        2

    )

    sensor["vibration"] = round(

        max(0.5, min(5, sensor["vibration"])),

        2

    )

    sensor["current"] = round(

        max(15, min(60, sensor["current"])),

        2

    )

    sensor["rpm"] = int(

        max(1500, min(3200, sensor["rpm"]))

    )

    return sensor.copy()

# ==========================================================
# AI FAILURE RISK
# ==========================================================

def calculate_failure_risk(sensor):

    temp_score = max(
        0,
        sensor["temperature"] - 55
    ) * 1.0

    vibration_score = max(
        0,
        sensor["vibration"] - 2.2
    ) * 14

    pressure_score = abs(
        sensor["pressure"] - 8
    ) * 5

    current_score = max(
        0,
        sensor["current"] - 40
    ) * 0.7

    hour_score = max(
        0,
        sensor["running_hours"] - 6000
    ) / 700

    risk = round(

        min(

            100,

            temp_score
            + vibration_score
            + pressure_score
            + current_score
            + hour_score

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