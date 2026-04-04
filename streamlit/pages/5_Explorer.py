import streamlit as st
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
    st.error(f"❌ {status.get('error', 'DB no disponible')}")
    st.stop()

# ── Queries de ejemplo ────────────────────────────────────────────────────────
PRESETS = {
    "── Seleccioná una query ──": "",
    "📋 Todas las tablas": "SELECT table_schema, table_name FROM information_schema.tables ORDER BY 1,2",
    "🔵 stg_tickets (10 filas)": "SELECT * FROM main.stg_tickets LIMIT 10",
    "📊 mart_operations_sla (10 filas)": "SELECT * FROM main.mart_operations_sla LIMIT 10",
    "⭐ mart_cx_satisfaction (10 filas)": "SELECT * FROM main.mart_cx_satisfaction LIMIT 10",
    "🎯 mart_priority_subjects (10 filas)": "SELECT * FROM main.mart_priority_subjects LIMIT 10",
    "⚖️ mart_fairness (10 filas)": "SELECT * FROM main.mart_fairness LIMIT 10",
    "📈 Tickets por canal y prioridad": """
SELECT ticket_channel, ticket_priority,
       SUM(total_tickets) as total,
       ROUND(AVG(avg_satisfaction),2) as avg_sat
FROM main.mart_cx_satisfaction
GROUP BY 1,2
ORDER BY total DESC
""",
    "🔍 Tickets críticos sin resolver": """
SELECT ticket_channel, SUM(critical_unresolved_count) as criticos_abiertos
FROM main.mart_operations_sla
GROUP BY 1
ORDER BY 2 DESC
""",
}

preset = st.selectbox("Queries de ejemplo:", list(PRESETS.keys()))
default_sql = PRESETS[preset]

sql = st.text_area(
    "Escribí tu consulta SQL (DuckDB dialect):",
    value=default_sql,
    height=140,
    placeholder="SELECT * FROM main.mart_cx_satisfaction LIMIT 10",
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
            st.download_button("⬇ CSV", csv, "query_result.csv", "text/csv", use_container_width=True)

        # Mini-viz automática si hay columnas numéricas
        num_cols = df.select_dtypes("number").columns.tolist()
        cat_cols = df.select_dtypes("object").columns.tolist()

        if num_cols and cat_cols and len(df) <= 200:
            st.markdown("---")
            st.subheader("Vista rápida")
            vc1, vc2 = st.columns(2)
            x_col = vc1.selectbox("Eje X (categoría):", cat_cols, key="x")
            y_col = vc2.selectbox("Eje Y (número):", num_cols, key="y")

            import plotly.express as px
            fig = px.bar(df, x=x_col, y=y_col)
            st.plotly_chart(fig, use_container_width=True)