import streamlit as st
from utils.db import db_status

def render_sidebar():
    """Sidebar común con estado de la DB y navegación."""
    with st.sidebar:
        st.markdown("## 🗄️ Base de datos")
        status = db_status()

        if status["ok"]:
            st.success("DuckDB conectado ✅")
            st.caption(f"`{status['path']}`")
            with st.expander("Tablas disponibles"):
                for t in status["tables"]:
                    icon = "📋" if "mart_" in t else "🔵" if "stg_" in t else "⚫"
                    st.markdown(f"{icon} `{t}`")
        else:
            st.error("DuckDB no disponible ❌")
            st.caption(status.get("error", ""))
            st.info("Corré `make pipeline` para cargar los datos.")

        st.markdown("---")
        st.markdown("## 🔗 Navegación")
        st.page_link("app.py",                       label="🏠 Home")
        st.page_link("pages/1_Operations_SLA.py",    label="🔧 Operations & SLA")
        st.page_link("pages/2_CX_Satisfaction.py",   label="⭐ CX Satisfaction")
        st.page_link("pages/3_Priority_Subjects.py", label="🎯 Priority & Subjects")
        st.page_link("pages/4_Fairness.py",          label="⚖️ Fairness / Bias")
        st.page_link("pages/5_Explorer.py",          label="🗄️ SQL Explorer")

        st.markdown("---")
        st.caption("Capstone DE Zoomcamp 2025")