from collections import deque
from datetime import datetime
import pandas as pd


class SensorHistory:
    """
    Stores the latest live sensor readings.
    Automatically keeps only the most recent 'max_points' records.
    """

    def __init__(self, max_points=50):
        self.history = deque(maxlen=max_points)

    def add(self, sensor_data, prediction, probability, health):
        """
        Add one new reading to history.
        """

        record = {
            "timestamp": datetime.now(),

            "temperature": sensor_data["temperature"],
            "pressure": sensor_data["pressure"],
            "vibration": sensor_data["vibration"],
            "current": sensor_data["current"],
            "rpm": sensor_data["rpm"],
            "running_hours": sensor_data["running_hours"],

            "prediction": prediction,
            "probability": probability,
            "health": health
        }

        self.history.append(record)

    def dataframe(self):
        """
        Return all stored readings as a pandas DataFrame.
        """

        return pd.DataFrame(self.history)

    def clear(self):
        """
        Remove all history.
        """

        self.history.clear()