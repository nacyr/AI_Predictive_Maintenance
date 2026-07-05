from datetime import datetime, timedelta
import random


# ==========================================================
# ENGINEER POOL (can later come from database)
# ==========================================================

ENGINEERS = [
    "John Okafor",
    "Amina Bello",
    "David Musa",
    "Sarah Ibrahim",
    "Mohammed Yusuf"
]


# ==========================================================
# PRIORITY LEVELS
# ==========================================================

def get_priority(health_score, failure_probability):

    if failure_probability > 0.8 or health_score < 30:
        return "CRITICAL"

    elif failure_probability > 0.5 or health_score < 60:
        return "HIGH"

    elif failure_probability > 0.2:
        return "MEDIUM"

    return "LOW"


# ==========================================================
# AUTO SCHEDULER
# ==========================================================

def generate_maintenance_schedule(machine_name, health_score, failure_probability):

    priority = get_priority(health_score, failure_probability)

    # assign engineer (simple intelligent load balancing)
    engineer = random.choice(ENGINEERS)

    # schedule timing based on priority
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