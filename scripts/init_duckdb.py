"""
init_duckdb.py
==============
Crea los schemas iniciales en DuckDB y una vista de exploración rápida.
Ejecutar una vez antes de correr los flows de Kestra.

Uso:
    python3 scripts/init_duckdb.py
"""

import duckdb
import os

DB_PATH = os.environ.get("DUCKDB_PATH", "/shared/duckdb/support.duckdb")

con = duckdb.connect(DB_PATH)

print(f"Conectado a: {DB_PATH}")

# Crear schemas
for schema in ["raw", "staging", "marts", "streaming"]:
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    print(f"Schema '{schema}' listo.")

# Vista auxiliar de exploración (se llena después de la ingesta)
con.execute("""
    CREATE OR REPLACE VIEW marts.vw_ticket_overview AS
    SELECT
        'No data yet — run flow 01_ingest_csv first' AS status
""")

# Tabla de control de cargas
con.execute("""
    CREATE TABLE IF NOT EXISTS raw._load_log (
        run_id          VARCHAR,
        source          VARCHAR,
        rows_loaded     INTEGER,
        loaded_at       TIMESTAMP DEFAULT current_timestamp
    )
""")

print("\nSetup inicial completado.")
print("Schemas disponibles:")
print(con.execute("SHOW SCHEMAS").df().to_string(index=False))

con.close()
