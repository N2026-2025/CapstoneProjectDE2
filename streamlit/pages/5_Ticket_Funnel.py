import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db import get_data
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Ticket Funnel", page_icon="🔽", layout="wide")
render_sidebar()

st.title("🔽 Ticket Funnel")
st.caption("Fuente: `main_marts.mart_ticket_funnel` — ¿Dónde se atascan los tickets?")
st.markdown("---")

# CORRECCIÓN: Se cambió main. por main_marts.
df = get_data("SELECT * FROM main_marts.mart_ticket_funnel")

if df is None or df.empty:
    st.warning("No se encontraron datos en mart_ticket_funnel. Verificá tu pipeline de dbt.")
    st.stop()

# Cálculos para el Funnel
total      = int(df["total_tickets"].sum())
got_resp   = int(df["got_first_response"].sum())
closed     = int(df["count_closed"].sum())
open_stuck = int(df["count_open"].sum())
pending    = int(df["count_pending"].sum())
dead_ends  = int(df["is_dead_end"].sum())

# ── Funnel visual ──────────────────────────────────────────────────────────────
st.subheader("📊 Funnel Global de Tickets")
col_f, col_k = st.columns([2,1])

with col_f:
    fig = go.Figure(go.Funnel(
        y=["Total tickets","Recibieron respuesta","En pendiente","Cerrados (resueltos)"],
        x=[total, got_resp, pending, closed],
        textinfo="value+percent initial",
        marker=dict(color=["#636EFA","#FFA15A","#FECB52","#00CC96"]),
    ))
    fig.update_layout(height=350, margin=dict(l=0,r=0))
    st.plotly_chart(fig, use_container_width=True)

with col_k:
    st.metric("Total tickets",          f"{total:,}")
    st.metric("Con primera respuesta",  f"{got_resp:,}",
              delta=f"{got_resp/total*100:.1f}%")
    st.metric("Cerrados (resueltos)",   f"{closed:,}",
              delta=f"{closed/total*100:.1f}%")
    st.metric("Abiertos sin respuesta", f"{open_stuck:,}",
              delta=f"-{open_stuck/total*100:.1f}%", delta_color="inverse")

st.markdown("---")

# ── Row 1: % Atascados por Subject | por Canal ────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    st.subheader("📌 % Tickets Open (Atascados) por Subject")
    by_subj = df.groupby("ticket_subject", as_index=False).agg({
        "total_tickets": "sum", 
        "count_open": "sum"
    })
    by_subj["pct_stuck"] = (by_subj["count_open"] / by_subj["total_tickets"] * 100).round(1)
    by_subj = by_subj.sort_values("pct_stuck", ascending=True)
    
    fig = px.bar(by_subj, x="pct_stuck", y="ticket_subject", orientation="h",
                 color="pct_stuck", color_continuous_scale="Reds",
                 text=by_subj["pct_stuck"].apply(lambda x:f"{x:.1f}%"))
    fig.update_layout(coloraxis_showscale=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("📡 Salud del Funnel por Canal")
    by_ch = df.groupby("ticket_channel", as_index=False).agg({
        "total_tickets": "sum", 
        "count_closed": "sum",
        "count_open": "sum", 
        "count_pending": "sum"
    })
    
    # Normalización para gráfico de barras apiladas
    for col in ["count_closed", "count_pending", "count_open"]:
        by_ch[f"pct_{col}"] = (by_ch[col] / by_ch["total_tickets"] * 100)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Cerrado", x=by_ch["ticket_channel"], y=by_ch["pct_count_closed"], marker_color="#00CC96"))
    fig.add_trace(go.Bar(name="Pendiente", x=by_ch["ticket_channel"], y=by_ch["pct_count_pending"], marker_color="#FFA15A"))
    fig.add_trace(go.Bar(name="Abierto", x=by_ch["ticket_channel"], y=by_ch["pct_count_open"], marker_color="#EF553B"))
    
    fig.update_layout(barmode="stack", height=400, legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

# ── Tabla dead-ends ────────────────────────────────────────────────────────────
st.subheader("💀 Combinaciones Dead-End (Baja resolución)")
dead = df[df["is_dead_end"] == True][
    ["ticket_channel","ticket_type","ticket_priority",
     "ticket_subject","total_tickets","pct_stuck_open","funnel_health"]
].sort_values("total_tickets", ascending=False)

if not dead.empty:
    st.dataframe(dead, use_container_width=True)
else:
    st.success("✅ No se detectaron cuellos de botella críticos (Dead-ends).")