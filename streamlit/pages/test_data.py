import streamlit as st
from utils.db import get_data

st.title("🕵️ Inspección de Datos Reales")

df = get_data("SELECT * FROM main_marts.mart_repeat_customers LIMIT 100")

st.subheader("Valores únicos en columnas clave")
col1, col2 = st.columns(2)

with col1:
    st.write("**Segmentos de Recurrencia:**")
    st.write(df['recurrence_segment'].unique())

with col2:
    st.write("**Niveles de Riesgo:**")
    st.write(df['churn_risk'].unique())

st.subheader("Muestra de los primeros 10 datos")
st.write(df[['customer_name', 'ticket_count', 'recurrence_segment', 'churn_risk']].head(10))
