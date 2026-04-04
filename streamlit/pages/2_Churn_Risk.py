import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db import get_data
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Churn Risk", page_icon="🚨", layout="wide")
render_sidebar()

st.title("🚨 Repeat Customers & Churn Risk")
st.markdown("---")

df = get_data("SELECT * FROM main_marts.mart_repeat_customers")

if df is None or df.empty:
    st.error("No hay datos disponibles. Verificá la tabla 'mart_repeat_customers'.")
    st.stop()

# ── NORMALIZACIÓN DE DATOS (Para evitar errores de mayúsculas/minúsculas) ──
# Convertimos a minúsculas para que las comparaciones funcionen siempre
df['churn_risk_clean'] = df['churn_risk'].str.lower()

# ── KPIs CORREGIDOS ──────────────────────────────────────────────────────────
total        = len(df)
repeat       = int((df["ticket_count"] >= 2).sum())
# Buscamos "inminente" sin importar si empieza con mayúscula
inminente    = int(df["churn_risk_clean"].str.contains("inminente", na=False).sum())
riesgo       = int(df["churn_risk_clean"].str.contains("riesgo", na=False).sum())

# Manejo de NaN para promedios
sat_repeat   = df[df["ticket_count"] >= 2]["avg_satisfaction"].mean()
sat_single   = df[df["ticket_count"] == 1]["avg_satisfaction"].mean()

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Clientes únicos", f"{total:,}")
k2.metric("Recurrentes", f"{repeat}", delta=f"{repeat/total*100:.1f}%")
k3.metric("🔴 Inminente", f"{inminente}")
k4.metric("🟡 Riesgo", f"{riesgo}")
k5.metric("Sat. Recurrente", f"{sat_repeat:.2f}" if not pd.isna(sat_repeat) else "N/A")

st.markdown("---")

# ── GRÁFICOS ────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Segmentación por Recurrencia")
    # Usamos value_counts para asegurar que se cuenten todas las categorías
    seg = df["recurrence_segment"].value_counts().reset_index()
    seg.columns = ["segmento", "clientes"]
    fig = px.bar(seg, x="segmento", y="clientes", color="segmento", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Distribución de Riesgo")
    # Agrupamos por el campo original para mantener los emojis si los tiene
    risk_dist = df["churn_risk"].value_counts().reset_index()
    risk_dist.columns = ["riesgo", "clientes"]
    fig = px.pie(risk_dist, values="clientes", names="riesgo", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# ── TABLA DE DETALLE ────────────────────────────────────────────────────────
st.subheader("📋 Clientes con Mayor Riesgo")
# Mostramos clientes con más de 1 ticket o satisfacción baja
top_risk = df.sort_values(by=["ticket_count", "avg_satisfaction"], ascending=[False, True]).head(20)
st.dataframe(top_risk[["customer_name", "ticket_count", "unresolved_count", "avg_satisfaction", "churn_risk"]], use_container_width=True)
