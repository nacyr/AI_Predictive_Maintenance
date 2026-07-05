import numpy as np

def predict_failure(temperature, pressure, vibration, current, rpm, running_hours):
    """
    Simple deterministic AI fallback model (safe for deployment).
    Replace later with real ML model if needed.
    """

    score = 0

    # Risk logic (simple but stable)
    if temperature > 80:
        score += 0.2
    if vibration > 0.7:
        score += 0.25
    if pressure > 8:
        score += 0.15
    if current > 15:
        score += 0.15
    if rpm > 3000:
        score += 0.1
    if running_hours > 1000:
        score += 0.15

    score = min(score, 1.0)

    prediction = score >= 0.5

    return prediction, float(score)