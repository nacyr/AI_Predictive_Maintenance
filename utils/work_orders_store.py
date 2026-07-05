import pandas as pd
from datetime import datetime

# ==========================================================
# GLOBAL WORK ORDER STORE (in-memory for now)
# later can be replaced with database table
# ==========================================================

_work_orders = []


def add_work_order(order: dict):
    order["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _work_orders.append(order)


def get_work_orders():
    return pd.DataFrame(_work_orders) if _work_orders else pd.DataFrame()


def clear_work_orders():
    global _work_orders
    _work_orders = []