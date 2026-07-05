import numpy as np


def generate_sensor_data():
    """
    Simulate live industrial sensor readings.
    """

    return {
        "temperature": np.random.normal(65, 2),
        "pressure": np.random.normal(8.5, 0.3),
        "vibration": np.random.normal(2.2, 0.2),
        "current": np.random.normal(18, 1),
        "rpm": np.random.normal(2950, 20),
        "running_hours": np.random.randint(500, 8000)
    }