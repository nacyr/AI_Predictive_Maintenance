import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd

# ==========================================================
# DATABASE
# ==========================================================

DB_PATH = Path(__file__).resolve().parent / "plant.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# CREATE TABLE
# ==========================================================

def create_machine_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS machines (

        machine TEXT PRIMARY KEY,

        health REAL,
        failure_risk REAL,

        temperature REAL,
        pressure REAL,
        vibration REAL,
        current REAL,

        rpm INTEGER,
        running_hours INTEGER,

        status TEXT,
        failure_mode TEXT,

        last_update TEXT,
        last_repair TEXT

    )
    """)

    conn.commit()
    conn.close()


# ==========================================================
# INSERT MACHINE
# ==========================================================

def insert_machine(machine):

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT OR REPLACE INTO machines (

            machine,
            health,
            failure_risk,
            temperature,
            pressure,
            vibration,
            current,
            rpm,
            running_hours,
            status,
            failure_mode,
            last_update,
            last_repair

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        machine["Machine"],
        machine["Health (%)"],
        machine["Failure Risk (%)"],
        machine["Temperature (°C)"],
        machine["Pressure (bar)"],
        machine["Vibration"],
        machine["Current (A)"],
        machine["RPM"],
        machine["Running Hours"],
        machine["Status"],
        machine["Failure Mode"],
        now,
        now

    ))

    conn.commit()
    conn.close()


# ==========================================================
# UPDATE MACHINE
# ==========================================================

def update_machine(machine):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE machines

        SET

            health=?,
            failure_risk=?,
            temperature=?,
            pressure=?,
            vibration=?,
            current=?,
            rpm=?,
            running_hours=?,
            status=?,
            failure_mode=?,
            last_update=?

        WHERE machine=?

    """, (

        machine["Health (%)"],
        machine["Failure Risk (%)"],
        machine["Temperature (°C)"],
        machine["Pressure (bar)"],
        machine["Vibration"],
        machine["Current (A)"],
        machine["RPM"],
        machine["Running Hours"],
        machine["Status"],
        machine["Failure Mode"],
        datetime.now().isoformat(),
        machine["Machine"]

    ))

    conn.commit()
    conn.close()


# ==========================================================
# UPDATE LAST REPAIR
# ==========================================================

def update_last_repair(machine_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE machines

        SET last_repair=?

        WHERE machine=?

    """, (

        datetime.now().isoformat(),
        machine_name

    ))

    conn.commit()
    conn.close()


# ==========================================================
# GET MACHINE
# ==========================================================

def get_machine(machine_name):

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM machines

        WHERE machine=?

    """, conn, params=(machine_name,))

    conn.close()

    if df.empty:
        return None

    return df.iloc[0].to_dict()


# ==========================================================
# GET ALL MACHINES
# ==========================================================

def get_all_machines():

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM machines

        ORDER BY machine

    """, conn)

    conn.close()

    return df


# ==========================================================
# DELETE MACHINE
# ==========================================================

def delete_machine(machine_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM machines

        WHERE machine=?

    """, (machine_name,))

    conn.commit()
    conn.close()


# ==========================================================
# CLEAR DATABASE
# ==========================================================

def clear_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM machines

    """)

    conn.commit()
    conn.close()


# ==========================================================
# MACHINE COUNT
# ==========================================================

def machine_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT COUNT(*)

        FROM machines

    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

create_machine_table()