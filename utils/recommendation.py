def maintenance_recommendation(prediction, probability):

    if probability < 0.20:
        return (
            "LOW",
            "Continue normal operation. No maintenance required."
        )

    elif probability < 0.50:
        return (
            "MEDIUM",
            "Schedule preventive maintenance during the next planned shutdown."
        )

    elif probability < 0.80:
        return (
            "HIGH",
            "Inspect bearings, lubrication system and alignment immediately."
        )

    return (
        "CRITICAL",
        "Immediate shutdown recommended. High probability of equipment failure."
    )