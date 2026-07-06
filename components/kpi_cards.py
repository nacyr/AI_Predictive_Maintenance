import streamlit as st


def show_kpi_cards(
    total_orders=0,
    pending=0,
    approved=0,
    completed=0,
    rejected=0,
    critical=0,
    warning=0,
    healthy=0,
    plant_health=None,
):
    """
    Enterprise KPI Cards

    Every dashboard can display only the KPIs it needs.
    """

    metrics = []

    metrics.append(("📋 Total", total_orders))

    if pending is not None:
        metrics.append(("🟡 Pending", pending))

    if approved is not None:
        metrics.append(("🔵 Approved", approved))

    if completed is not None:
        metrics.append(("🟢 Completed", completed))

    if rejected is not None:
        metrics.append(("🔴 Rejected", rejected))

    if critical is not None:
        metrics.append(("🚨 Critical", critical))

    if warning is not None:
        metrics.append(("⚠ Warning", warning))

    if healthy is not None:
        metrics.append(("✅ Healthy", healthy))

    if plant_health is not None:
        metrics.append(("💚 Plant Health", f"{plant_health:.1f}%"))

    cols = st.columns(len(metrics))

    for col, (title, value) in zip(cols, metrics):
        col.metric(title, value)