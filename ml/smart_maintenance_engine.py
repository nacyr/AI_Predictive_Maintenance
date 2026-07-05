from datetime import datetime, timedelta
import random

# ==========================================================
# ENGINEER POOL
# ==========================================================

ENGINEERS = [
    "John Okafor",
    "Amina Bello",
    "David Musa",
    "Sarah Ibrahim",
    "Mohammed Yusuf"
]

# ==========================================================
# FAILURE PREDICTION
# ==========================================================

def predict_failure(
    temperature,
    pressure,
    vibration,
    current,
    rpm,
    running_hours
):
    """
    Simple rule-based failure prediction.

    Returns:
        (prediction, probability)

        prediction -> True / False
        probability -> float (0.0 - 1.0)
    """

    score = 0.0

    # Temperature
    if temperature > 90:
        score += 0.25
    elif temperature > 75:
        score += 0.15

    # Pressure
    if pressure > 9:
        score += 0.20
    elif pressure > 7:
        score += 0.10

    # Vibration
    if vibration > 8:
        score += 0.25
    elif vibration > 5:
        score += 0.15

    # Current
    if current > 40:
        score += 0.15
    elif current > 30:
        score += 0.10

    # Running Hours
    if running_hours > 8000:
        score += 0.15
    elif running_hours > 5000:
        score += 0.10

    probability = min(score, 1.0)

    prediction = probability >= 0.70

    return prediction, probability


# ==========================================================
# PRIORITY LEVEL
# ==========================================================

def get_priority(health_score, failure_probability):

    if failure_probability >= 0.80 or health_score <= 30:
        return "CRITICAL"

    elif failure_probability >= 0.60 or health_score <= 60:
        return "HIGH"

    elif failure_probability >= 0.30:
        return "MEDIUM"

    return "LOW"


# ==========================================================
# MAINTENANCE SCHEDULER
# ==========================================================

def generate_maintenance_schedule(
    machine_name,
    health_score,
    failure_probability
):

    priority = get_priority(
        health_score,
        failure_probability
    )

    engineer = random.choice(ENGINEERS)

    now = datetime.now()

    if priority == "CRITICAL":
        scheduled_time = now + timedelta(hours=1)

    elif priority == "HIGH":
        scheduled_time = now + timedelta(hours=6)

    elif priority == "MEDIUM":
        scheduled_time = now + timedelta(days=1)

    else:
        scheduled_time = now + timedelta(days=3)

    return {
        "machine": machine_name,
        "priority": priority,
        "engineer": engineer,
        "scheduled_time": scheduled_time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "PENDING"
    }