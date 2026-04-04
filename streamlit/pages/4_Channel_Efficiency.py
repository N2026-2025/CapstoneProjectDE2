import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db import get_data
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Channel Efficiency", page_icon="📡", layout="wide")
render_sidebar()

st.title("📡 Channel Efficiency")
st.caption("Fuente: `main_marts.mart_channel_efficiency` — ¿Qué canal resuelve mejor?")
st.markdown("---")

# CORRECCIÓN: Se cambió main. por main_marts.
df = get_data("SELECT * FROM main_marts.mart_channel_efficiency")
if df is None or df.empty:
    st.warning("No se encontraron datos en mart_channel_efficiency.")
    st.stop()

# Agregación y cálculos
ch = df.groupby("ticket_channel", as_index=False).agg({
    "total_tickets": "sum",
    "resolved_count": "sum",
    "no_response_count": "sum",
    "critical_open": "sum",
    "avg_satisfaction": "mean",
    "resolution_vs_global": "mean",
    "satisfaction_vs_global": "mean"
})

ch["pct_resolved"] = (ch["resolved_count"] / ch["total_tickets"] * 100).round(1)
ch["pct_no_response"] = (ch["no_response_count"] / ch["total_tickets"] * 100).round(1)

# KPIs
col1, col2, col3 = st.columns(3)
best_ch = ch.sort_values("pct_resolved", ascending=False).iloc[0]
col1.metric("Mejor Canal (Resolución)", best_ch["ticket_channel"].title(), f"{best_ch['pct_resolved']}%")
col2.metric("Tickets Totales", f"{ch['total_tickets'].sum():,}")
col3.metric("Satisfacción Promedio", f"{ch['avg_satisfaction'].mean():.2f} ⭐")

st.markdown("---")

# Gráficos
c1, c2 = st.columns(2)
with c1:
    st.subheader("Distribución de Tickets por Canal")
    fig_pie = px.pie(ch, values='total_tickets', names='ticket_channel', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("% Resolución por Canal")
    fig_bar = px.bar(ch.sort_values("pct_resolved"), x="pct_resolved", y="ticket_channel", 
                     orientation='h', text="pct_resolved", color="pct_resolved",
                     color_continuous_scale="RdYlGn")
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📋 Detalle de Eficiencia por Canal")
st.dataframe(ch.sort_values("total_tickets", ascending=False), use_container_width=True)
