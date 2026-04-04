import streamlit as st

st.set_page_config(
    page_title="CX Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
# 📊 Customer Support Analytics
### Capstone DE Zoomcamp — Stack: DuckDB · dbt · Kestra · Streamlit
""")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("### 🔧 Operations & SLA\nTiempos de respuesta, backlog, SLA por canal y prioridad.")
    st.page_link("pages/1_Operations_SLA.py", label="Ir al dashboard →")

with col2:
    st.info("### ⭐ CX Satisfaction\nSatisfacción por canal, producto, edad y tiempo de resolución.")
    st.page_link("pages/2_CX_Satisfaction.py", label="Ir al dashboard →")

with col3:
    st.info("### 🎯 Priority & Subjects\nMatrix de prioridades, productos con más quejas, escalamientos.")
    st.page_link("pages/3_Priority_Subjects.py", label="Ir al dashboard →")

col4, col5, _ = st.columns(3)

with col4:
    st.info("### ⚖️ Fairness / Bias\nDetección de sesgos por género, edad y canal de atención.")
    st.page_link("pages/4_Fairness.py", label="Ir al dashboard →")

with col5:
    st.info("### 🗄️ Raw Explorer\nExplorá las tablas de DuckDB directamente con SQL.")
    st.page_link("pages/5_Explorer.py", label="Ir al dashboard →")

st.markdown("---")
st.caption("Datos: [Customer Support Ticket Dataset — Kaggle](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) | Pipeline: Kestra → DuckDB raw → dbt → Streamlit")