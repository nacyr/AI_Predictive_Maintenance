import pandas as pd
import numpy as np
import plotly.express as px


def sensor_history(current_value, sensor_name):

    values = np.random.normal(
        current_value,
        current_value * 0.02,
        40
    )

    df = pd.DataFrame({

        "Sample": range(40),

        sensor_name: values

    })

    fig = px.line(
        df,
        x="Sample",
        y=sensor_name,
        title=f"{sensor_name} Trend"
    )

    return fig

import plotly.graph_objects as go


def health_gauge(health):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health,
        title={"text": "Machine Health (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "green"},
            "steps": [
                {"range": [0, 50], "color": "#ff4d4d"},
                {"range": [50, 80], "color": "#ffcc00"},
                {"range": [80, 100], "color": "#00cc66"}
            ]
        }
    ))

    fig.update_layout(height=320)

    return fig


def failure_gauge(probability):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability,
        title={"text": "Failure Risk (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "red"},
            "steps": [
                {"range": [0, 20], "color": "#00cc66"},
                {"range": [20, 60], "color": "#ffcc00"},
                {"range": [60, 100], "color": "#ff4d4d"}
            ]
        }
    ))

    fig.update_layout(height=320)

    return fig