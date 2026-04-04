import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db import get_data
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Product Health", page_icon="🏥", layout="wide")
render_sidebar()

st.title("🏥 Product Health")
st.caption("Fuente: `main_marts.mart_product_health` — Análisis de salud por producto")
st.markdown("---")

# CORRECCIÓN: Se cambió main. por main_marts.
df = get_data("SELECT * FROM main_marts.mart_product_health")
if df is None or df.empty:
    st.warning("No se encontraron datos en mart_product_health.")
    st.stop()

# ... (El resto de tu código de procesamiento de 'prod' y KPIs se mantiene igual) ...
# Asegurate de mantener tu lógica de agrupación 'prod = df.groupby...'


prod = df.groupby("product_purchased", as_index=False).agg(
    total_tickets      = ("total_tickets",       "sum"),
    avg_satisfaction   = ("avg_satisfaction",    "mean"),
    pct_resolved       = ("pct_resolved",        "mean"),
    critical_unresolved= ("critical_unresolved", "sum"),
    no_response_count  = ("no_response_count",   "sum"),
    health_score       = ("health_score",        "mean"),
    risk_level         = ("risk_level",          "first"),
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
alto   = int(prod["risk_level"].str.contains("Alto",  na=False).sum())
medio  = int(prod["risk_level"].str.contains("medio", na=False).sum())
worst  = prod.sort_values("health_score").iloc[0]["product_purchased"].title()
best   = prod.sort_values("health_score", ascending=False).iloc[0]["product_purchased"].title()
t_crit = int(prod["critical_unresolved"].sum())

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Productos alto riesgo",  alto,   delta_color="inverse")
k2.metric("Productos riesgo medio", medio,  delta_color="inverse")
k3.metric("Críticos sin resolver",  t_crit, delta_color="inverse")
k4.metric("Peor health score",  worst[:20])
k5.metric("Mejor health score", best[:20])
st.markdown("---")

# ── Row 1: Health Score | Scatter resolución vs satisfacción ─────────────────
c1, c2 = st.columns(2)
with c1:
    st.subheader("🏆 Health Score por Producto")
    st.caption("Fórmula: resolución % × 0.5 + satisfacción normalizada × 0.5")
    top = prod.sort_values("health_score").head(20)
    color_map = {"🔴 Alto riesgo":"#EF553B","🟡 Riesgo medio":"#FFA15A","🟢 Estable":"#00CC96"}
    colors = [color_map.get(r, "#636EFA") for r in top["risk_level"]]
    fig = go.Figure(go.Bar(
        x=top["health_score"], y=top["product_purchased"].str.title(),
        orientation="h", marker_color=colors,
        text=top["health_score"].round(1), textposition="outside",
    ))
    fig.update_layout(height=500, xaxis_range=[0,100],
                      xaxis_title="Health Score (0=peor, 100=mejor)",
                      yaxis={"categoryorder":"total ascending"}, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("📍 Resolución vs Satisfacción")
    st.caption("Cuadrante inferior-izquierdo = mayor riesgo")
    fig = px.scatter(
        prod, x="pct_resolved", y="avg_satisfaction",
        size="total_tickets", color="risk_level",
        hover_name="product_purchased",
        color_discrete_map={"🔴 Alto riesgo":"#EF553B","🟡 Riesgo medio":"#FFA15A","🟢 Estable":"#00CC96"},
        labels={"pct_resolved":"% Resueltos","avg_satisfaction":"Satisfacción (1-5)","risk_level":"Riesgo"},
    )
    fig.add_vline(x=prod["pct_resolved"].mean(),   line_dash="dash", line_color="gray", opacity=.5)
    fig.add_hline(y=prod["avg_satisfaction"].mean(),line_dash="dash", line_color="gray", opacity=.5)
    fig.update_layout(height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Críticos sin resolver | Sin primera respuesta ─────────────────────
c3, c4 = st.columns(2)
with c3:
    st.subheader("🚨 Críticos Sin Resolver — Top 15")
    t = prod.sort_values("critical_unresolved", ascending=False).head(15)
    fig = px.bar(t, x="critical_unresolved", y="product_purchased", orientation="h",
                 color="critical_unresolved", color_continuous_scale="Reds", text="critical_unresolved",
                 labels={"critical_unresolved":"Críticos abiertos","product_purchased":"Producto"})
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, height=420,
                      yaxis={"categoryorder":"total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("📭 Sin Ninguna Respuesta — Top 15")
    t = prod.sort_values("no_response_count", ascending=False).head(15)
    fig = px.bar(t, x="no_response_count", y="product_purchased", orientation="h",
                 color="no_response_count", color_continuous_scale="Oranges", text="no_response_count",
                 labels={"no_response_count":"Sin respuesta","product_purchased":"Producto"})
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, height=420,
                      yaxis={"categoryorder":"total ascending"})
    st.plotly_chart(fig, use_container_width=True)

# ── Heatmap Producto × Tipo ───────────────────────────────────────────────────
st.subheader("🗺️ Heatmap: Producto × Tipo de Ticket (% Resuelto)")
heat = df.groupby(["product_purchased","ticket_type"], as_index=False)["pct_resolved"].mean()
pivot = heat.pivot(index="product_purchased", columns="ticket_type", values="pct_resolved").fillna(0)
fig = px.imshow(pivot, text_auto=".0f", color_continuous_scale="RdYlGn",
                zmin=0, zmax=80, labels={"color":"% Resuelto"}, aspect="auto")
fig.update_layout(height=620, xaxis_title="Tipo de ticket", yaxis_title="Producto")
st.plotly_chart(fig, use_container_width=True)

# ── Tabla filtrable ───────────────────────────────────────────────────────────
st.subheader("🔍 Detalle por producto")
risk_filter = st.multiselect("Filtrar por riesgo:",
    options=prod["risk_level"].unique().tolist(),
    default=prod["risk_level"].unique().tolist())
filtered = prod[prod["risk_level"].isin(risk_filter)].sort_values("health_score")
st.dataframe(
    filtered[["product_purchased","total_tickets","pct_resolved",
              "avg_satisfaction","critical_unresolved","health_score","risk_level"]]
    .rename(columns={"product_purchased":"Producto","total_tickets":"Tickets",
                     "pct_resolved":"% Resuelto","avg_satisfaction":"Satisfacción",
                     "critical_unresolved":"Críticos sin resolver",
                     "health_score":"Health Score","risk_level":"Riesgo"})
    .style.format({"% Resuelto":"{:.1f}%","Satisfacción":"{:.2f}","Health Score":"{:.1f}"}),
    use_container_width=True, height=350)