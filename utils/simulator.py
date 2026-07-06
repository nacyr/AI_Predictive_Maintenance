import random

# ==========================================================
# MACHINE MEMORY
# ==========================================================

_machine_state = {}

# ==========================================================
# DEFAULT MACHINE VALUES
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
# MACHINE PROFILES
# ==========================================================

MACHINE_PROFILE = {

    "Pump A1": 0.90,

    "Pump A2": 1.00,

    "Compressor B1": 1.30,

    "Compressor B2": 1.40,

    "Motor C1": 0.95,

    "Motor C2": 1.15,

    "Generator D1": 1.20,

    "Cooling Fan E1": 0.80,

    "DEFAULT": 1.00

}

# ==========================================================
# RANDOM WALK
# ==========================================================

def drift(value, minimum, maximum, step):

    value += random.uniform(-step, step)

    value = max(minimum, min(maximum, value))

    return round(value, 2)

# ==========================================================
# SENSOR GENERATOR
# ==========================================================

def generate_sensor_data(machine_name="DEFAULT"):

    if machine_name not in _machine_state:

        sensor = DEFAULT_SENSOR.copy()

        sensor["temperature"] += random.uniform(-5, 5)

        sensor["pressure"] += random.uniform(-0.5, 0.5)

        sensor["vibration"] += random.uniform(-0.4, 0.4)

        sensor["current"] += random.uniform(-5, 5)

        sensor["rpm"] += random.randint(-200, 200)

        sensor["running_hours"] = random.randint(500, 12000)

        _machine_state[machine_name] = sensor

    sensor = _machine_state[machine_name]

    # ------------------------------------------------------
    # NORMAL SENSOR DRIFT
    # ------------------------------------------------------

    sensor["temperature"] = drift(
        sensor["temperature"],
        40,
        90,
        1.5
    )

    sensor["pressure"] = drift(
        sensor["pressure"],
        6.5,
        9.5,
        0.20
    )

    sensor["vibration"] = drift(
        sensor["vibration"],
        0.5,
        4.5,
        0.15
    )

    sensor["current"] = drift(
        sensor["current"],
        15,
        55,
        1.2
    )

    sensor["rpm"] = int(

        drift(

            sensor["rpm"],

            1500,

            3200,

            40

        )

    )

    sensor["running_hours"] += random.randint(1, 5)

    # ------------------------------------------------------
    # OCCASIONAL DETERIORATION
    # ------------------------------------------------------

    if random.random() < 0.15:

        sensor["temperature"] += random.uniform(2, 5)

        sensor["vibration"] += random.uniform(0.2, 0.6)

        sensor["current"] += random.uniform(1, 3)

    # ------------------------------------------------------
    # OCCASIONAL RECOVERY
    # ------------------------------------------------------

    if random.random() < 0.10:

        sensor["temperature"] -= random.uniform(1, 4)

        sensor["vibration"] -= random.uniform(0.1, 0.4)

        sensor["current"] -= random.uniform(0.5, 2)

    return sensor.copy()

# ==========================================================
# AI FAILURE RISK
# ==========================================================

def calculate_failure_risk(sensor, machine_name="DEFAULT"):

    profile = MACHINE_PROFILE.get(

        machine_name,

        MACHINE_PROFILE["DEFAULT"]

    )

    temp_score = max(

        0,

        sensor["temperature"] - 50

    ) * 1.5

    vibration_score = max(

        0,

        sensor["vibration"] - 1.8

    ) * 18

    pressure_score = abs(

        sensor["pressure"] - 8

    ) * 6

    current_score = max(

        0,

        sensor["current"] - 30

    ) * 1.2

    hour_score = sensor["running_hours"] / 800

    random_score = random.uniform(-5, 10)

    risk = (

        temp_score

        + vibration_score

        + pressure_score

        + current_score

        + hour_score

        + random_score

    )

    risk *= profile

    risk = round(

        max(

            0,

            min(100, risk)

        ),

        1

    )

    return risk

# ==========================================================
# MACHINE STATUS
# ==========================================================

def get_machine_status(risk):

    if risk >= 75:

        return "CRITICAL"

    elif risk >= 50:

        return "WARNING"

    else:

        return "NORMAL"