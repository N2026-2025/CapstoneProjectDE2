import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db import get_data, DB_PATH, db_status
from utils.sidebar import render_sidebar

st.set_page_config(page_title="SQL Explorer", page_icon="🗄️", layout="wide")
render_sidebar()

st.title("🗄️ SQL Explorer")
st.caption(f"Conectado a: `{DB_PATH}`")
st.markdown("---")

status = db_status()
if status["ok"]:
    st.success(f"✅ DuckDB disponible — {len(status['tables'])} tablas encontradas")
else:
    st.error(status.get("error","DB no disponible"))
    st.stop()

# ── Queries de ejemplo ────────────────────────────────────────────────────────
PRESETS = {
    "── Seleccioná una query ──": "",
    "📋 Todas las tablas":
        "SELECT table_schema, table_name FROM information_schema.tables ORDER BY 1,2",
    "🏥 mart_product_health (10 filas)":
        "SELECT * FROM main.mart_product_health LIMIT 10",
    "🚨 mart_repeat_customers (10 filas)":
        "SELECT * FROM main.mart_repeat_customers LIMIT 10",
    "📡 mart_channel_efficiency (10 filas)":
        "SELECT * FROM main.mart_channel_efficiency LIMIT 10",
    "🔽 mart_ticket_funnel (10 filas)":
        "SELECT * FROM main.mart_ticket_funnel LIMIT 10",
    "🔵 stg_tickets (10 filas)":
        "SELECT * FROM main.stg_tickets LIMIT 10",
    "📊 Tickets críticos sin resolver por canal":
        """SELECT ticket_channel,
       SUM(critical_unresolved_count) AS criticos_abiertos
FROM main.mart_operations_sla
GROUP BY 1
ORDER BY 2 DESC""",
    "🏆 Top 10 productos por health score":
        """SELECT product_purchased, ROUND(AVG(health_score),1) AS health_score,
       ROUND(AVG(pct_resolved),1) AS pct_resolved,
       any_value(risk_level) AS risk
FROM main.mart_product_health
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10""",
    "🔎 Clientes con más de 1 ticket":
        """SELECT customer_name, ticket_count, churn_risk, avg_satisfaction
FROM main.mart_repeat_customers
WHERE ticket_count >= 2
ORDER BY ticket_count DESC, avg_satisfaction ASC
LIMIT 20""",
}

preset = st.selectbox("Queries de ejemplo:", list(PRESETS.keys()))
sql = st.text_area(
    "Escribí tu consulta SQL (DuckDB dialect):",
    value=PRESETS[preset],
    height=130,
    placeholder="SELECT * FROM main.mart_product_health LIMIT 10",
)

col_run, col_dl, _ = st.columns([1,1,5])
with col_run:
    run = st.button("▶ Ejecutar", type="primary", use_container_width=True)

if run and sql.strip():
    with st.spinner("Ejecutando..."):
        df = get_data(sql.strip())

    if not df.empty:
        st.success(f"{len(df):,} filas devueltas")
        st.dataframe(df, use_container_width=True, height=420)

        with col_dl:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ CSV", csv, "query_result.csv",
                               "text/csv", use_container_width=True)

        # Mini-viz automática
        num_cols = df.select_dtypes("number").columns.tolist()
        cat_cols = df.select_dtypes("object").columns.tolist()
        if num_cols and cat_cols and len(df) <= 200:
            st.markdown("---")
            st.subheader("Vista rápida")
            vc1, vc2 = st.columns(2)
            x_col = vc1.selectbox("Eje X:", cat_cols, key="vx")
            y_col = vc2.selectbox("Eje Y:", num_cols, key="vy")
            fig = px.bar(df, x=x_col, y=y_col)
            st.plotly_chart(fig, use_container_width=True)