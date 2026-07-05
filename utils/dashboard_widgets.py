import streamlit as st
import pandas as pd

# ==========================================================
# DATA TABLE
# ==========================================================

def show_table(
    title,
    dataframe,
    empty_message="No data available."
):
    """
    Display a dataframe with a title.
    """

    section(title)

    if dataframe is None or dataframe.empty:

        st.info(empty_message)

        return

    st.dataframe(
        dataframe,
        width="stretch",
        hide_index=True
    )

    divider()


# ==========================================================
# MACHINE TABLE
# ==========================================================

def show_machine_table(machine_df):

    show_table(
        "🏭 Live Machine Monitoring",
        machine_df,
        "No machine information available."
    )


# ==========================================================
# WORK ORDER TABLE
# ==========================================================

def show_work_order_table(orders):

    show_table(
        "🛠 Work Orders",
        orders,
        "No work orders available."
    )


# ==========================================================
# PLANT TABLE
# ==========================================================

def show_plant_table(plants):

    show_table(
        "🏭 Plant Status",
        plants,
        "No plant status available."
    )