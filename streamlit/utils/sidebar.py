import streamlit as st
from utils.db import db_status


def render_sidebar():
    """Sidebar común: estado de DB + navegación a las 5 páginas."""
    with st.sidebar:
        st.markdown("## 🗄️ Base de datos")
        status = db_status()

        if status["ok"]:
            st.success("DuckDB conectado ✅")
            st.caption(f"`{status['path']}`")
            with st.expander("Tablas disponibles"):
                for t in status["tables"]:
                    if "mart_" in t:
                        icon = "📋"
                    elif "stg_" in t:
                        icon = "🔵"
                    elif "streaming" in t:
                        icon = "⚡"
                    else:
                        icon = "⚫"
                    st.markdown(f"{icon} `{t}`")
        else:
            st.error("DuckDB no disponible ❌")
            st.caption(status.get("error", ""))
            st.warning("Corré `make pipeline` para cargar los datos.")

        st.markdown("---")
        st.markdown("## 🔗 Páginas")
        st.page_link("app.py",                        label="🏠 Home")
        st.page_link("pages/1_Product_Health.py",     label="🏥 Product Health")
        st.page_link("pages/2_Churn_Risk.py",         label="🚨 Churn Risk")
        st.page_link("pages/3_Explorer.py",           label="🗄️ SQL Explorer")
        st.page_link("pages/4_Channel_Efficiency.py", label="📡 Channel Efficiency")
        st.page_link("pages/5_Ticket_Funnel.py",      label="🔽 Ticket Funnel")

        st.markdown("---")
        st.caption("Capstone DE Zoomcamp 2026")