import pandas as pd

from database.work_orders import (
    get_work_orders,
    get_work_order_statistics,
    get_machine_failure_frequency,
    get_daily_work_order_trends,
    get_ai_vs_manual_breakdown,
)

from utils.plant import plant_status


# ==========================================================
# WORK ORDERS
# ==========================================================

def load_work_orders():
    try:
        df = get_work_orders()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:
        return pd.DataFrame()


# ==========================================================
# PLANT STATUS
# ==========================================================

def load_plant_status():
    try:
        df = plant_status()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:
        return pd.DataFrame()


# ==========================================================
# DASHBOARD STATISTICS
# ==========================================================

def load_statistics():
    try:
        stats = get_work_order_statistics()

        if stats is None:
            return {}

        return stats

    except Exception:
        return {}


# ==========================================================
# MACHINE FAILURE FREQUENCY
# ==========================================================

def load_machine_frequency():
    try:
        df = get_machine_failure_frequency()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:
        return pd.DataFrame()


# ==========================================================
# DAILY TRENDS
# ==========================================================

def load_daily_trends():
    try:
        df = get_daily_work_order_trends()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:
        return pd.DataFrame()


# ==========================================================
# AI VS MANUAL
# ==========================================================

def load_ai_breakdown():
    try:
        data = get_ai_vs_manual_breakdown()

        if data is None:
            return {}

        return data

    except Exception:
        return {}