import streamlit as st
 
st.set_page_config(
    page_title="CX Support Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
st.markdown("""
# 📊 Customer Support Analytics
### Capstone DE Zoomcamp · DuckDB · dbt · Kestra · Streamlit
""")
st.markdown("---")
 
col1, col2, col3 = st.columns(3)
with col1:
    st.info("### 🏥 Product Health\nHealth score por producto, riesgo, críticos sin resolver.")
    st.page_link("pages/1_Product_Health.py", label="Ir →")
with col2:
    st.info("### 🚨 Churn Risk\nClientes recurrentes y riesgo de abandono.")
    st.page_link("pages/2_Churn_Risk.py", label="Ir →")
with col3:
    st.info("### 🗄️ SQL Explorer\nQuery libre sobre DuckDB + descarga CSV.")
    st.page_link("pages/3_Explorer.py", label="Ir →")
 
col4, col5, _ = st.columns(3)
with col4:
    st.info("### 📡 Channel Efficiency\n¿Qué canal resuelve mejor? Desvío vs benchmark global.")
    st.page_link("pages/4_Channel_Efficiency.py", label="Ir →")
with col5:
    st.info("### 🔽 Ticket Funnel\n¿Dónde se atascan los tickets? Dead-ends por subject.")
    st.page_link("pages/5_Ticket_Funnel.py", label="Ir →")
 
st.markdown("---")
st.caption(
    "Datos: [Customer Support Ticket Dataset — Kaggle](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) "
    "| Pipeline: Kestra → DuckDB raw → dbt → Streamlit"
)