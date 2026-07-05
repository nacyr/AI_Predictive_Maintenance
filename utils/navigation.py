import streamlit as st


def quick_navigation(
    prediction=False,
    analytics=False,
    maintenance=False,
    admin=False,
    operations=False
):

    st.divider()
    st.subheader("⚡ Quick Navigation")

    cols = st.columns(5)

    with cols[0]:
        if prediction and st.button("🤖 Prediction", use_container_width=True):
            st.switch_page("pages/prediction.py")

    with cols[1]:
        if analytics and st.button("📊 Analytics", use_container_width=True):
            st.switch_page("pages/analytics.py")

    with cols[2]:
        if maintenance and st.button("🛠 Maintenance", use_container_width=True):
            st.switch_page("pages/maintenance_dashboard.py")

    with cols[3]:
        if admin and st.button("⚙ Admin", use_container_width=True):
            st.switch_page("pages/admin_dashboard.py")

    with cols[4]:
        if operations and st.button("🏭 Operations", use_container_width=True):
            st.switch_page("pages/operations_dashboard.py")