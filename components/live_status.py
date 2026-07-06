import streamlit as st
from datetime import datetime


def show_live_status(refresh_count=0, interval=10):
    """
    Enterprise Live System Status Panel
    """

    st.subheader("🟢 Live Plant Status")

    left, right = st.columns(2)

    with left:

        st.success(f"""
**System Status**
- 🟢 ONLINE
- 🤖 AI Engine: ACTIVE
- 📡 Sensor Network: STREAMING
- 💾 Database: CONNECTED
""")

    with right:

        st.info(f"""
**Monitoring**
- 🔄 Refresh Count: {refresh_count}
- ⏱ Refresh Interval: {interval} sec
- 🕒 Last Update:
{datetime.now().strftime("%d %b %Y %H:%M:%S")}
""")