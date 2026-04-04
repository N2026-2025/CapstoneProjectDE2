import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db import get_data
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Fairness / Bias", page_icon="⚖️", layout="wide")
render_sidebar()

st.title("⚖️ Fairness & Bias Analysis")
st.caption("Fuente: `main.mart_fairness` — generado por dbt")
st.info("💡 **Cómo leer los desvíos:** Positivo (+) = peor servicio que el promedio. Negativo (−) = mejor servicio.")
st.markdown("---")

df = get_data("SELECT * FROM main.mart_fairness")

if df.empty:
    st.stop()

# ── Tabs por dimensión de análisis ────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["👤 Por Género", "📅 Por Edad", "📡 Por Canal"])

# ── TAB 1: Género ──────────────────────────────────────────────────────────────
with tab1:
    by_gender = df.groupby("customer_gender", as_index=False).agg(
        avg_resolution_hrs=("avg_resolution_hrs","mean"),
        avg_first_response_hrs=("avg_first_response_hrs","mean"),
        avg_satisfaction=("avg_satisfaction","mean"),
        resolution_bias=("resolution_bias","mean"),
        frt_bias=("frt_bias","mean"),
        satisfaction_bias=("satisfaction_bias","mean"),
        pct_critical=("pct_critical","mean"),
        ticket_count=("ticket_count","sum"),
    )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Desvío de Resolución respecto al Promedio Global")
        fig = px.bar(by_gender, x="customer_gender", y="resolution_bias",
                     color="resolution_bias", color_continuous_scale="RdBu_r",
                     text=by_gender["resolution_bias"].round(2),
                     labels={"resolution_bias":"Desvío (hrs)","customer_gender":"Género"})
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Satisfacción Promedio por Género")
        fig = px.bar(by_gender, x="customer_gender", y="avg_satisfaction",
                     color="avg_satisfaction", color_continuous_scale="RdYlGn", range_color=[1,5],
                     text=by_gender["avg_satisfaction"].round(2),
                     labels={"avg_satisfaction":"Rating","customer_gender":"Género"})
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False, yaxis_range=[0,5.5], height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("% Tickets Clasificados como Críticos por Género")
    fig = px.bar(by_gender, x="customer_gender", y="pct_critical",
                 text=by_gender["pct_critical"].round(1),
                 labels={"pct_critical":"% Críticos","customer_gender":"Género"},
                 color_discrete_sequence=["#EF553B"])
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(yaxis_range=[0,50], height=300)
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 2: Edad ────────────────────────────────────────────────────────────────
with tab2:
    age_order = ["Gen Z (<25)","Millennial (25-34)","Gen X (35-44)","Boomer (45-59)","Senior (60+)"]
    by_age = df.groupby("age_segment", as_index=False).agg(
        resolution_bias=("resolution_bias","mean"),
        frt_bias=("frt_bias","mean"),
        satisfaction_bias=("satisfaction_bias","mean"),
        pct_critical=("pct_critical","mean"),
        avg_satisfaction=("avg_satisfaction","mean"),
    )
    by_age["age_segment"] = pd.Categorical(by_age["age_segment"], categories=age_order, ordered=True)
    by_age = by_age.sort_values("age_segment")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Desvío de FRT por Segmento de Edad")
        fig = px.bar(by_age, x="age_segment", y="frt_bias",
                     color="frt_bias", color_continuous_scale="RdBu_r",
                     text=by_age["frt_bias"].round(2),
                     labels={"frt_bias":"Desvío FRT (hrs)","age_segment":"Segmento"})
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Satisfacción por Segmento de Edad")
        fig = px.line(by_age, x="age_segment", y="avg_satisfaction", markers=True,
                      labels={"avg_satisfaction":"Rating","age_segment":"Segmento"},
                      range_y=[0,5])
        fig.update_traces(line_color="#636EFA", line_width=2.5, marker_size=9)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 3: Canal ───────────────────────────────────────────────────────────────
with tab3:
    by_channel = df.groupby("ticket_channel", as_index=False).agg(
        resolution_bias=("resolution_bias","mean"),
        frt_bias=("frt_bias","mean"),
        satisfaction_bias=("satisfaction_bias","mean"),
        pct_critical=("pct_critical","mean"),
    )

    st.subheader("Desvíos vs Promedio Global por Canal (Resolución | FRT | Satisfacción)")
    fig = go.Figure()
    metrics = [
        ("resolution_bias",    "Resolución (hrs)"),
        ("frt_bias",           "FRT (hrs)"),
        ("satisfaction_bias",  "Satisfacción (pts)"),
    ]
    for col, label in metrics:
        fig.add_trace(go.Bar(
            name=label,
            x=by_channel["ticket_channel"],
            y=by_channel[col],
            text=by_channel[col].round(2),
            textposition="outside",
        ))
    fig.add_hline(y=0, line_dash="dash", line_color="black")
    fig.update_layout(barmode="group", height=400,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("% Tickets Críticos por Canal")
    fig = px.bar(by_channel, x="ticket_channel", y="pct_critical",
                 color="pct_critical", color_continuous_scale="Reds",
                 text=by_channel["pct_critical"].round(1),
                 labels={"pct_critical":"% Críticos","ticket_channel":"Canal"})
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, yaxis_range=[0,50], height=320)
    st.plotly_chart(fig, use_container_width=True)