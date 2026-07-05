import sqlite3
from pathlib import Path
import pandas as pd

# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================

DB_PATH = Path(__file__).resolve().parent / "maintenance.db"

# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():
    """
    Returns a connection to the prediction database.
    """

    return sqlite3.connect(DB_PATH)


# ==========================================================
# CREATE TABLE
# ==========================================================

def create_predictions_table():
    """
    Creates the predictions table if it does not exist.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT NOT NULL,

            machine TEXT NOT NULL,

            temperature REAL,

            pressure REAL,

            vibration REAL,

            current REAL,

            rpm INTEGER,

            running_hours INTEGER,

            failure_probability REAL,

            machine_health REAL,

            remaining_life INTEGER,

            recommendation TEXT

        )
    """)

    conn.commit()
    conn.close()


# ==========================================================
# SAVE PREDICTION
# ==========================================================

def save_prediction(
    timestamp,
    machine,
    temperature,
    pressure,
    vibration,
    current,
    rpm,
    running_hours,
    failure_probability,
    machine_health,
    remaining_life,
    recommendation
):
    """
    Saves an AI prediction into the database.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO predictions(

            timestamp,
            machine,
            temperature,
            pressure,
            vibration,
            current,
            rpm,
            running_hours,
            failure_probability,
            machine_health,
            remaining_life,
            recommendation

        )

        VALUES(
            ?,?,?,?,?,?,?,?,?,?,?,?
        )

    """, (

        timestamp,
        machine,
        temperature,
        pressure,
        vibration,
        current,
        rpm,
        running_hours,
        failure_probability,
        machine_health,
        remaining_life,
        recommendation

    ))

    conn.commit()
    conn.close()


# ==========================================================
# GET ALL PREDICTIONS
# ==========================================================

def get_predictions():
    """
    Returns every prediction ordered from newest to oldest.
    """

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM predictions

        ORDER BY id DESC

    """, conn)

    conn.close()

    return df


# ==========================================================
# GET SINGLE PREDICTION
# ==========================================================

def get_prediction(prediction_id):
    """
    Returns a single prediction by ID.
    """

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM predictions

        WHERE id = ?

    """, conn, params=(prediction_id,))

    conn.close()

    return df


# ==========================================================
# SEARCH BY MACHINE
# ==========================================================

def search_predictions(machine):
    """
    Searches prediction history by machine name.
    """

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM predictions

        WHERE machine LIKE ?

        ORDER BY id DESC

    """, conn, params=(f"%{machine}%",))

    conn.close()

    return df
# ==========================================================
# HIGH RISK PREDICTIONS
# ==========================================================

def high_risk_predictions(threshold=70):
    """
    Returns predictions whose failure probability is
    greater than or equal to the specified threshold.
    """

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM predictions

        WHERE failure_probability >= ?

        ORDER BY failure_probability DESC

    """, conn, params=(threshold,))

    conn.close()

    return df


# ==========================================================
# RECENT PREDICTIONS
# ==========================================================

def get_latest_predictions(limit=10):
    """
    Returns the most recent predictions.
    """

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM predictions

        ORDER BY id DESC

        LIMIT ?

    """, conn, params=(limit,))

    conn.close()

    return df


# ==========================================================
# FILTER PREDICTIONS BY DATE
# ==========================================================

def predictions_between(start_date, end_date):
    """
    Returns predictions between two dates.
    """

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM predictions

        WHERE DATE(timestamp)
        BETWEEN DATE(?) AND DATE(?)

        ORDER BY id DESC

    """, conn, params=(start_date, end_date))

    conn.close()

    return df


# ==========================================================
# DELETE PREDICTION
# ==========================================================

def delete_prediction(prediction_id):
    """
    Deletes a prediction by ID.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        DELETE

        FROM predictions

        WHERE id = ?

    """, (prediction_id,))

    conn.commit()
    conn.close()


# ==========================================================
# CLEAR PREDICTION HISTORY
# ==========================================================

def clear_predictions():
    """
    Deletes every prediction from the database.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        DELETE

        FROM predictions

    """)

    conn.commit()
    conn.close()


# ==========================================================
# TOTAL PREDICTIONS
# ==========================================================

def total_predictions():
    """
    Returns the total number of predictions.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT COUNT(*)

        FROM predictions

    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total
# ==========================================================
# AVERAGE FAILURE PROBABILITY
# ==========================================================

def average_failure_probability():
    """
    Returns the average failure probability.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT AVG(failure_probability)

        FROM predictions

    """)

    value = cursor.fetchone()[0]

    conn.close()

    return round(value or 0, 2)


# ==========================================================
# AVERAGE MACHINE HEALTH
# ==========================================================

def average_machine_health():
    """
    Returns the average machine health score.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT AVG(machine_health)

        FROM predictions

    """)

    value = cursor.fetchone()[0]

    conn.close()

    return round(value or 0, 2)


# ==========================================================
# MACHINE STATISTICS
# ==========================================================

def machine_statistics():
    """
    Returns the number of predictions recorded
    for each machine.
    """

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT

            machine,

            COUNT(*) AS total_predictions,

            AVG(failure_probability) AS average_failure_probability,

            AVG(machine_health) AS average_machine_health

        FROM predictions

        GROUP BY machine

        ORDER BY machine

    """, conn)

    conn.close()

    return df


# ==========================================================
# DATABASE SUMMARY
# ==========================================================

def database_summary():
    """
    Returns summary statistics for the prediction database.
    """

    return {

        "total_predictions": total_predictions(),

        "average_failure_probability":
            average_failure_probability(),

        "average_machine_health":
            average_machine_health()

    }


# ==========================================================
# EXPORT PREDICTIONS
# ==========================================================

def export_predictions():
    """
    Returns all prediction records as a DataFrame.
    Useful for CSV export.
    """

    return get_predictions()


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

create_predictions_table()