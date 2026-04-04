import duckdb
import pandas as pd
import streamlit as st
import os

# Soporta tanto Docker como desarrollo local / GitHub Codespaces
_CANDIDATES = [
    "/shared/duckdb/support.duckdb",                        # Docker volume
    "/workspaces/CapstoneProjectDE2/duckdb/support.duckdb", # Codespaces
    os.path.join(os.path.dirname(__file__), "..", "..", "duckdb", "support.duckdb"),  # relativo
]

def _resolve_db_path() -> str:
    for p in _CANDIDATES:
        resolved = os.path.abspath(p)
        if os.path.exists(resolved):
            return resolved
    # Fallback: devuelve el primero (el error se maneja en get_data)
    return _CANDIDATES[0]

DB_PATH = _resolve_db_path()


@st.cache_data(ttl=300, show_spinner="Consultando DuckDB...")
def get_data(query: str) -> pd.DataFrame:
    """Lee datos de DuckDB en modo read-only con cache de 5 minutos."""
    try:
        with duckdb.connect(DB_PATH, read_only=True) as con:
            return con.execute(query).df()
    except Exception as e:
        st.error(f"❌ Error conectando a DuckDB: `{e}`")
        st.info(f"📁 Ruta buscada: `{DB_PATH}`\n\nAsegurate de haber corrido `make pipeline` antes.")
        return pd.DataFrame()


def db_status() -> dict:
    """Retorna info del estado de la DB para el sidebar."""
    try:
        with duckdb.connect(DB_PATH, read_only=True) as con:
            tables = con.execute("""
                SELECT table_schema || '.' || table_name as full_name
                FROM information_schema.tables
                ORDER BY 1
            """).fetchall()
        return {"ok": True, "path": DB_PATH, "tables": [t[0] for t in tables]}
    except Exception as e:
        return {"ok": False, "path": DB_PATH, "error": str(e)}