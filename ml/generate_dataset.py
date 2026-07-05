import numpy as np
import pandas as pd

# Reproducible results
np.random.seed(42)

rows = 10000

temperature = np.random.normal(65, 5, rows)
pressure = np.random.normal(8.5, 0.4, rows)
vibration = np.random.normal(2.2, 0.6, rows)
current = np.random.normal(18, 2, rows)
rpm = np.random.normal(2950, 30, rows)
running_hours = np.random.randint(500, 8000, rows)

# Failure logic
failure = (
    (temperature > 72) |
    (pressure > 9.2) |
    (vibration > 3.2) |
    (current > 21) |
    (running_hours > 6500)
).astype(int)

df = pd.DataFrame({
    "temperature": temperature.round(2),
    "pressure": pressure.round(2),
    "vibration": vibration.round(2),
    "current": current.round(2),
    "rpm": rpm.round(0).astype(int),
    "running_hours": running_hours,
    "failure": failure
})

df.to_csv("dataset/sensor_data.csv", index=False)

print("=" * 60)
print("Dataset Generated Successfully")
print(df.head())
print("=" * 60)