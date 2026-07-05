import streamlit as st
from datetime import datetime

# ==========================================================
# ENTERPRISE FOOTER
# ==========================================================

def show_footer():

    st.divider()

    c1, c2, c3 = st.columns(3)

    # ------------------------------------------------------
    # SYSTEM STATUS
    # ------------------------------------------------------

    with c1:

        st.success("🟢 AI Prediction Engine Online")

    # ------------------------------------------------------
    # LAST REFRESH
    # ------------------------------------------------------

    with c2:

        st.info(
            f"🕒 Last Refresh\n\n{datetime.now().strftime('%d %b %Y  %H:%M:%S')}"
        )

    # ------------------------------------------------------
    # VERSION
    # ------------------------------------------------------

    with c3:

        st.info(
            """
🏭 Industrial AI Predictive Maintenance

Version **2.0 Enterprise**
"""
        )

    st.divider()

    st.caption(
        "© 2026 Industrial AI Predictive Maintenance System | Enterprise Edition | Powered by Streamlit & Machine Learning"
    )