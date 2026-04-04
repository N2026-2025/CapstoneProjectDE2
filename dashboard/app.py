import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Capstone CX Dashboard", layout="wide")

st.title("📊 Dashboard de Soporte (Capstone Project)")

# Conexión a DuckDB (Modo Solo Lectura para evitar bloqueos)
DB_PATH = '/shared/duckdb/support.duckdb'

def get_data(query):
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(query).df()

# Sidebar para elegir el Mart
st.sidebar.header("Configuración")
table = st.sidebar.selectbox("Seleccioná un Mart:", 
    ["mart_cx_satisfaction", "mart_operations_sla", "mart_priority_subjects"])

try:
    df = get_data(f"SELECT * FROM {table}")
    
    st.subheader(f"Vista previa de: {table}")
    st.dataframe(df.head(10))

    # Ejemplo de gráfico dinámico (asumiendo que tenés columnas de fecha o categorías)
    st.subheader("Visualización Rápida")
    cols = df.columns.tolist()
    
    if len(cols) > 1:
        fig = px.bar(df, x=cols[0], y=cols[1], title=f"Distribución en {table}")
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error al conectar con DuckDB: {e}")
    st.info("Asegurate de haber corrido 'make pipeline' antes.")
