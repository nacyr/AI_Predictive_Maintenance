import pandas as pd
import numpy as np


def plant_status():

    machines = [
        "Pump-01",
        "Pump-02",
        "Compressor-01",
        "Compressor-02",
        "Generator-01",
        "Turbine-01"
    ]

    data = []

    for machine in machines:

        health = round(np.random.uniform(55, 100), 1)

        failure = round(100 - health, 1)

        if health >= 90:
            status = "🟢 NORMAL"

        elif health >= 75:
            status = "🟡 WARNING"

        else:
            status = "🔴 CRITICAL"

        data.append({
            "Machine": machine,
            "Status": status,
            "Health": health,
            "Failure": failure
        })

    return pd.DataFrame(data)