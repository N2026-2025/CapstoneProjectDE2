import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db import get_data
from utils.sidebar import render_sidebar

st.set_page_config(page_title="CX Satisfaction", page_icon="⭐", layout="wide")
render_sidebar()

st.title("⭐ CX Satisfaction")
st.caption("Fuente: `main.mart_cx_satisfaction` — generado por dbt")
st.markdown("---")

df = get_data("SELECT * FROM main.mart_cx_satisfaction")

if df.empty:
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
avg_sat   = df["avg_satisfaction"].mean()
total     = int(df["total_tickets"].sum())
pct_close = df["closed_count"].sum() / total * 100 if total else 0

k1, k2, k3 = st.columns(3)
k1.metric("Satisfacción Promedio Global", f"{avg_sat:.2f} / 5")
k2.metric("Total Tickets",               f"{total:,}")
k3.metric("% Cerrados",                  f"{pct_close:.1f}%")

st.markdown("---")

# ── Row 1: Satisfacción por Canal | por Género ────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Satisfacción Promedio por Canal")
    by_ch = df.groupby("ticket_channel", as_index=False)["avg_satisfaction"].mean().sort_values("avg_satisfaction")
    fig = px.bar(by_ch, x="avg_satisfaction", y="ticket_channel", orientation="h",
                 color="avg_satisfaction", color_continuous_scale="RdYlGn", range_color=[1,5],
                 labels={"avg_satisfaction": "Rating promedio", "ticket_channel": "Canal"})
    fig.update_layout(coloraxis_showscale=False, height=320)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Satisfacción por Género")
    by_gen = df.groupby("customer_gender", as_index=False).agg(
        avg_satisfaction=("avg_satisfaction","mean"),
        total_tickets=("total_tickets","sum")
    )
    fig = px.bar(by_gen, x="customer_gender", y="avg_satisfaction",
                 color="customer_gender", text=by_gen["avg_satisfaction"].round(2),
                 labels={"avg_satisfaction": "Rating promedio", "customer_gender": "Género"},
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, yaxis_range=[0,5], height=320)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Satisfacción por Segmento de Edad | Scatter resolución vs rating ───
c3, c4 = st.columns(2)

with c3:
    st.subheader("Satisfacción por Segmento de Edad")
    age_order = ["Gen Z (<25)","Millennial (25-34)","Gen X (35-44)","Boomer (45-59)","Senior (60+)"]
    by_age = df.groupby("age_segment", as_index=False)["avg_satisfaction"].mean()
    by_age["age_segment"] = pd.Categorical(by_age["age_segment"], categories=age_order, ordered=True)
    by_age = by_age.sort_values("age_segment")
    fig = px.line(by_age, x="age_segment", y="avg_satisfaction", markers=True,
                  labels={"avg_satisfaction": "Rating promedio", "age_segment": "Segmento"},
                  range_y=[0,5])
    fig.update_traces(line_color="#00CC96", line_width=2.5, marker_size=9)
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Resolución vs Satisfacción (por bucket de tiempo)")
    bucket_order = ["0-6h","6-24h","1-3 days","3+ days"]
    by_bucket = df.groupby("resolution_bucket", as_index=False).agg(
        avg_satisfaction=("avg_satisfaction","mean"),
        total_tickets=("total_tickets","sum")
    )
    by_bucket["resolution_bucket"] = pd.Categorical(
        by_bucket["resolution_bucket"], categories=bucket_order, ordered=True)
    by_bucket = by_bucket.sort_values("resolution_bucket")
    fig = px.bar(by_bucket, x="resolution_bucket", y="avg_satisfaction",
                 color="avg_satisfaction", color_continuous_scale="RdYlGn", range_color=[1,5],
                 text=by_bucket["avg_satisfaction"].round(2),
                 labels={"avg_satisfaction": "Rating promedio", "resolution_bucket": "Tiempo de resolución"})
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, yaxis_range=[0,5.5], height=320)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Top 10 productos por satisfacción | Heatmap tipo × canal ───────────
c5, c6 = st.columns(2)

with c5:
    st.subheader("Top 10 Productos por Satisfacción Promedio")
    by_prod = df.groupby("product_purchased", as_index=False).agg(
        avg_satisfaction=("avg_satisfaction","mean"),
        total_tickets=("total_tickets","sum")
    ).sort_values("avg_satisfaction", ascending=False).head(10)
    fig = px.bar(by_prod, x="avg_satisfaction", y="product_purchased", orientation="h",
                 color="avg_satisfaction", color_continuous_scale="RdYlGn", range_color=[1,5],
                 labels={"avg_satisfaction": "Rating", "product_purchased": "Producto"})
    fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"}, height=380)
    st.plotly_chart(fig, use_container_width=True)

with c6:
    st.subheader("Heatmap: Tipo de Ticket × Prioridad (Satisfacción)")
    heat = df.groupby(["ticket_type","ticket_priority"], as_index=False)["avg_satisfaction"].mean()
    heat_pivot = heat.pivot(index="ticket_type", columns="ticket_priority", values="avg_satisfaction")
    fig = px.imshow(heat_pivot, text_auto=".2f", color_continuous_scale="RdYlGn",
                    zmin=1, zmax=5, labels={"color": "Rating"})
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)