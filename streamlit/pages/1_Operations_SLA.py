import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db import get_data
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Operations & SLA", page_icon="🔧", layout="wide")
render_sidebar()

st.title("🔧 Operations & SLA")
st.caption("Fuente: `main.mart_operations_sla` — generado por dbt")
st.markdown("---")

df = get_data("SELECT * FROM main.mart_operations_sla")

if df.empty:
    st.stop()

# ── KPIs globales ──────────────────────────────────────────────────────────────
total       = int(df["total_tickets"].sum())
backlog     = int(df["backlog_count"].sum())
crit_unresl = int(df["critical_unresolved_count"].sum())
avg_frt     = df["avg_first_response_hrs"].mean()
pct_24h     = (df["tickets_resolved_under_24h"].sum() / total * 100) if total else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Tickets",           f"{total:,}")
k2.metric("Backlog (open/pending)",  f"{backlog:,}", delta=f"{backlog/total*100:.1f}% del total", delta_color="inverse")
k3.metric("Críticos sin resolver",   f"{crit_unresl:,}", delta_color="inverse")
k4.metric("Avg First Response",      f"{avg_frt:.1f} hrs")
k5.metric("Resueltos < 24h",         f"{pct_24h:.1f}%")

st.markdown("---")

# ── Row 1: Tickets por canal | Tickets por estado ─────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Tickets por Canal")
    by_channel = df.groupby("ticket_channel", as_index=False)["total_tickets"].sum().sort_values("total_tickets", ascending=True)
    fig = px.bar(by_channel, x="total_tickets", y="ticket_channel", orientation="h",
                 color="total_tickets", color_continuous_scale="Blues",
                 labels={"total_tickets": "Tickets", "ticket_channel": "Canal"})
    fig.update_layout(showlegend=False, coloraxis_showscale=False, height=320)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Distribución por Estado")
    by_status = df.groupby("ticket_status", as_index=False)["total_tickets"].sum()
    fig = px.pie(by_status, values="total_tickets", names="ticket_status",
                 hole=0.45, color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Avg FRT por canal | % resueltos <24h por prioridad ─────────────────
c3, c4 = st.columns(2)

with c3:
    st.subheader("Tiempo Promedio de Primera Respuesta por Canal")
    frt_ch = df.groupby("ticket_channel", as_index=False)["avg_first_response_hrs"].mean().sort_values("avg_first_response_hrs")
    fig = px.bar(frt_ch, x="ticket_channel", y="avg_first_response_hrs",
                 color="avg_first_response_hrs", color_continuous_scale="RdYlGn_r",
                 labels={"avg_first_response_hrs": "Horas promedio", "ticket_channel": "Canal"})
    fig.update_layout(coloraxis_showscale=False, height=320)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("% Resueltos en <24h por Prioridad")
    sla_prio = df.groupby("ticket_priority", as_index=False).apply(
        lambda x: (x["tickets_resolved_under_24h"].sum() / x["total_tickets"].sum() * 100)
    ).rename(columns={None: "pct_under_24h"}).reset_index()
    # Fix para distintas versiones de pandas
    if "pct_under_24h" not in sla_prio.columns:
        sla_prio = df.groupby("ticket_priority")[["tickets_resolved_under_24h","total_tickets"]].sum().reset_index()
        sla_prio["pct_under_24h"] = sla_prio["tickets_resolved_under_24h"] / sla_prio["total_tickets"] * 100
    fig = px.bar(sla_prio, x="ticket_priority", y="pct_under_24h",
                 color="pct_under_24h", color_continuous_scale="RdYlGn",
                 labels={"pct_under_24h": "% < 24h", "ticket_priority": "Prioridad"},
                 range_y=[0, 100])
    fig.update_layout(coloraxis_showscale=False, height=320)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Carga por día de semana | Heatmap canal × prioridad ────────────────
c5, c6 = st.columns(2)

with c5:
    st.subheader("Carga de Tickets por Día de la Semana")
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    by_dow = df.groupby("day_name", as_index=False)["total_tickets"].sum()
    by_dow["day_name"] = pd.Categorical(by_dow["day_name"], categories=dow_order, ordered=True)
    by_dow = by_dow.sort_values("day_name")
    fig = px.line(by_dow, x="day_name", y="total_tickets", markers=True,
                  labels={"total_tickets": "Tickets", "day_name": "Día"})
    fig.update_traces(line_color="#636EFA", line_width=2.5)
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

with c6:
    st.subheader("Heatmap: Canal × Prioridad (Tickets)")
    heat = df.groupby(["ticket_channel","ticket_priority"], as_index=False)["total_tickets"].sum()
    heat_pivot = heat.pivot(index="ticket_channel", columns="ticket_priority", values="total_tickets").fillna(0)
    fig = px.imshow(heat_pivot, text_auto=True, color_continuous_scale="Blues",
                    labels={"color": "Tickets"})
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

import pandas as pd  # aseguramos import al final del módulo