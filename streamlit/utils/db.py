import os
import duckdb
import pandas as pd
import streamlit as st

# ── Rutas candidatas en orden de prioridad ────────────────────────────────────
# 1. Docker volume  2. GitHub Codespaces  3. Relativa al repo
_CANDIDATES = [
    "/shared/duckdb/support.duckdb",
    "/workspaces/CapstoneProjectDE2/duckdb/support.duckdb",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "duckdb", "support.duckdb")
    ),
]

def _resolve_db_path() -> str:
    for p in _CANDIDATES:
        if os.path.exists(p):
            return p
    return _CANDIDATES[0]   # fallback — el error se muestra en get_data()

DB_PATH = _resolve_db_path()


@st.cache_data(ttl=300, show_spinner="Consultando DuckDB...")
def get_data(query: str) -> pd.DataFrame:
    """Lee de DuckDB en modo read-only con cache de 5 minutos."""
    try:
        with duckdb.connect(DB_PATH, read_only=True) as con:
            return con.execute(query).df()
    except Exception as e:
        st.error(f"❌ Error conectando a DuckDB: `{e}`")
        st.info(
            f"📁 Ruta buscada: `{DB_PATH}`\n\n"
            "Asegurate de haber corrido `make pipeline` antes de levantar Streamlit."
        )
        return pd.DataFrame()


def db_status() -> dict:
    """Devuelve estado de la DB para el sidebar."""
    try:
        with duckdb.connect(DB_PATH, read_only=True) as con:
            tables = con.execute("""
                SELECT table_schema || '.' || table_name AS full_name
                FROM information_schema.tables
                ORDER BY 1
            """).fetchall()
        return {"ok": True, "path": DB_PATH, "tables": [t[0] for t in tables]}
    except Exception as e:
        return {"ok": False, "path": DB_PATH, "error": str(e)}