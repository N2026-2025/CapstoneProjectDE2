import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db import get_data
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Priority & Subjects", page_icon="🎯", layout="wide")
render_sidebar()

st.title("🎯 Priority Matrix & Subjects")
st.caption("Fuente: `main.mart_priority_subjects` — generado por dbt")
st.markdown("---")

df = get_data("SELECT * FROM main.mart_priority_subjects")

if df.empty:
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_critical = int(df["critical_count"].sum())
inconsistent   = int(df[df["priority_alignment"] != "Consistente"]["total_tickets"].sum())
total          = int(df["total_tickets"].sum())
avg_res        = df["avg_resolution_hrs"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Tickets Críticos",        f"{total_critical:,}")
k2.metric("Tickets con Prioridad Errónea", f"{inconsistent:,}", delta=f"{inconsistent/total*100:.1f}%", delta_color="inverse")
k3.metric("Avg Resolución Global",         f"{avg_res:.1f} hrs")
k4.metric("Subjects distintos",            f"{df['ticket_subject'].nunique()}")

st.markdown("---")

# ── Row 1: Top subjects críticos | Alignment pie ──────────────────────────────
c1, c2 = st.columns([2,1])

with c1:
    st.subheader("Top 15 Subjects con Tickets Críticos")
    top_subj = df.groupby("ticket_subject", as_index=False).agg(
        critical_count=("critical_count","sum"),
        total_tickets=("total_tickets","sum"),
        avg_satisfaction=("avg_satisfaction","mean")
    ).sort_values("critical_count", ascending=False).head(15)
    fig = px.bar(top_subj, x="critical_count", y="ticket_subject", orientation="h",
                 color="avg_satisfaction", color_continuous_scale="RdYlGn", range_color=[1,5],
                 text="critical_count",
                 labels={"critical_count":"Críticos","ticket_subject":"Subject","avg_satisfaction":"Satisfacción"})
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_colorbar_title="Rating", yaxis={"categoryorder":"total ascending"}, height=450)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Alineación de Prioridades")
    align = df.groupby("priority_alignment", as_index=False)["total_tickets"].sum()
    colors = {"Consistente":"#00CC96","Prioridad sobreasignada":"#FFA15A","Prioridad subasignada":"#EF553B"}
    fig = px.pie(align, values="total_tickets", names="priority_alignment",
                 color="priority_alignment", color_discrete_map=colors, hole=0.4)
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Escalamiento por tipo | Resolución por prioridad ───────────────────
c3, c4 = st.columns(2)

with c3:
    st.subheader("% Sin Resolver (Proxy Escalamiento) por Tipo de Ticket")
    by_type = df.groupby("ticket_type", as_index=False).agg(
        pct_unresolved=("pct_unresolved","mean"),
        total_tickets=("total_tickets","sum")
    ).sort_values("pct_unresolved", ascending=False)
    fig = px.bar(by_type, x="ticket_type", y="pct_unresolved",
                 color="pct_unresolved", color_continuous_scale="Reds",
                 text=by_type["pct_unresolved"].round(1),
                 labels={"pct_unresolved":"% sin resolver","ticket_type":"Tipo"})
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, yaxis_range=[0,100], height=350)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Tiempo de Resolución por Prioridad")
    by_prio = df.groupby("ticket_priority", as_index=False)["avg_resolution_hrs"].mean().sort_values("avg_resolution_hrs")
    fig = px.funnel(by_prio, x="avg_resolution_hrs", y="ticket_priority",
                    labels={"avg_resolution_hrs":"Horas promedio","ticket_priority":"Prioridad"})
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Top productos con tickets críticos ─────────────────────────────────
st.subheader("Top 10 Productos con Más Tickets Críticos")
by_prod = df.groupby("product_purchased", as_index=False).agg(
    critical_count=("critical_count","sum"),
    high_count=("high_count","sum"),
    avg_satisfaction=("avg_satisfaction","mean")
).sort_values("critical_count", ascending=False).head(10)

fig = px.bar(by_prod, x="product_purchased",
             y=["critical_count","high_count"],
             barmode="stack",
             color_discrete_map={"critical_count":"#EF553B","high_count":"#FFA15A"},
             labels={"value":"Tickets","product_purchased":"Producto","variable":"Prioridad"})
fig.update_layout(height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)