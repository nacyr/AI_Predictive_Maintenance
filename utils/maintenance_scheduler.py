from datetime import datetime, timedelta
import random
import pandas as pd


# ==========================================================
# MAINTENANCE ENGINEERS
# ==========================================================

ENGINEERS = [

    {
        "name": "Engr. Ahmed Musa",
        "specialty": "Mechanical"
    },

    {
        "name": "Engr. Fatima Ibrahim",
        "specialty": "Electrical"
    },

    {
        "name": "Engr. David Samuel",
        "specialty": "Instrumentation"
    },

    {
        "name": "Engr. Aisha Bello",
        "specialty": "Predictive Maintenance"
    },

    {
        "name": "Engr. Ibrahim Yusuf",
        "specialty": "Reliability"
    },

    {
        "name": "Engr. Grace John",
        "specialty": "Automation"
    }

]


# ==========================================================
# ASSIGN ENGINEER
# ==========================================================

def assign_engineer():

    return random.choice(ENGINEERS)


# ==========================================================
# AUTO SCHEDULER
# ==========================================================

def create_schedule(machine, risk_level):

    engineer = assign_engineer()

    now = datetime.now()

    if risk_level == "LOW":

        schedule = now + timedelta(days=30)

        priority = "LOW"

        status = "Scheduled"

    elif risk_level == "MEDIUM":

        schedule = now + timedelta(days=7)

        priority = "MEDIUM"

        status = "Pending"

    elif risk_level == "HIGH":

        schedule = now + timedelta(days=1)

        priority = "HIGH"

        status = "Urgent"

    else:

        schedule = now

        priority = "CRITICAL"

        status = "Emergency"

    work_order = f"WO-{random.randint(10000,99999)}"

    return {

        "Work Order": work_order,

        "Machine": machine,

        "Engineer": engineer["name"],

        "Specialty": engineer["specialty"],

        "Priority": priority,

        "Scheduled Date": schedule.strftime("%d-%b-%Y"),

        "Scheduled Time": schedule.strftime("%I:%M %p"),

        "Status": status

    }


# ==========================================================
# CREATE PLANT SCHEDULE
# ==========================================================

def maintenance_dashboard(plant_df):

    schedules = []

    for _, row in plant_df.iterrows():

        if "CRITICAL" in row["Status"]:

            risk = "CRITICAL"

        elif "WARNING" in row["Status"]:

            risk = "MEDIUM"

        else:

            risk = "LOW"

        schedules.append(

            create_schedule(

                row["Machine"],

                risk

            )

        )

    return pd.DataFrame(schedules)