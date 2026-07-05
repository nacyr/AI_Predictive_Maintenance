import joblib
import pandas as pd

# Load trained model
model = joblib.load("ml/model.pkl")


def predict_failure(temperature, pressure, vibration, current, rpm, running_hours):
    data = pd.DataFrame([{
        "temperature": temperature,
        "pressure": pressure,
        "vibration": vibration,
        "current": current,
        "rpm": rpm,
        "running_hours": running_hours
    }])

    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0][1]

    return prediction, probability