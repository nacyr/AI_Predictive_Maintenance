import streamlit as st

# ==========================================================
# ENTERPRISE SIDEBAR
# ==========================================================

def show_sidebar(user):

    with st.sidebar:

        st.title("🏭 Control Center")

        st.divider()

        # ======================================================
        # USER
        # ======================================================

        st.subheader("👤 Logged In")

        st.write(f"**Name:** {user['fullname']}")
        st.write(f"**Role:** {user['role']}")

        st.divider()

        # ======================================================
        # PLANT SELECTION
        # ======================================================

        if "selected_plant" not in st.session_state:
            st.session_state.selected_plant = "Lagos Refinery"

        plant = st.selectbox(
            "🏭 Active Plant",
            [
                "Lagos Refinery",
                "Port Harcourt Plant",
                "Warri Depot"
            ],
            index=[
                "Lagos Refinery",
                "Port Harcourt Plant",
                "Warri Depot"
            ].index(st.session_state.selected_plant)
        )

        st.session_state.selected_plant = plant

        st.divider()

        # ======================================================
        # SYSTEM STATUS
        # ======================================================

        st.subheader("🖥 System Status")

        st.success("AI Engine Online")

        st.success("Database Connected")

        st.success("Prediction Service Running")

        st.divider()

        # ======================================================
        # QUICK INFO
        # ======================================================

        st.subheader("📊 Quick Information")

        st.info(
            f"""
Current Plant

**{plant}**
"""
        )

        st.caption(
            "Enterprise Industrial AI Predictive Maintenance System"
        )

        return {
            "plant": plant
        }