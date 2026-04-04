#!/usr/bin/env python3
# =============================================================================
# download_dataset.py — Descarga el CSV desde Kaggle
# Uso: python3 scripts/download_dataset.py
#
# Requiere: pip install kaggle
# Credenciales en ~/.kaggle/kaggle.json o variables de entorno:
#   export KAGGLE_USERNAME=tu_usuario
#   export KAGGLE_KEY=tu_api_key
#
# Obtener API key: https://www.kaggle.com/settings → API → Create New Token
# =============================================================================

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path

DATASET   = "suraj520/customer-support-ticket-dataset"
OUT_DIR   = Path("./data")
FILENAME  = "customer_support_tickets.csv"

def setup_kaggle_credentials():
    """Configura credenciales desde variables de entorno si no existe kaggle.json"""
    kaggle_dir  = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"

    if kaggle_json.exists():
        print("✅ Credenciales Kaggle encontradas en ~/.kaggle/kaggle.json")
        return True

    username = os.environ.get("KAGGLE_USERNAME", "")
    key      = os.environ.get("KAGGLE_KEY", "")

    if not username or not key:
        print("❌ Credenciales de Kaggle no encontradas.")
        print("")
        print("   Opción A — Variables de entorno:")
        print("     export KAGGLE_USERNAME=tu_usuario")
        print("     export KAGGLE_KEY=tu_api_key")
        print("")
        print("   Opción B — Archivo kaggle.json:")
        print("     1. Ir a https://www.kaggle.com/settings")
        print("     2. API → Create New Token")
        print("     3. Mover kaggle.json a ~/.kaggle/")
        print("     4. chmod 600 ~/.kaggle/kaggle.json")
        return False

    kaggle_dir.mkdir(parents=True, exist_ok=True)
    with open(kaggle_json, "w") as f:
        json.dump({"username": username, "key": key}, f)
    os.chmod(kaggle_json, 0o600)
    print(f"✅ Credenciales configuradas desde variables de entorno")
    return True


def download_with_kaggle_api():
    """Descarga usando la librería oficial kaggle"""
    try:
        import kaggle
    except ImportError:
        print("⚙️  Instalando kaggle...")
        os.system(f"{sys.executable} -m pip install kaggle --quiet")
        import kaggle

    print(f"⬇️  Descargando dataset: {DATASET}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    import kaggle.api
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(DATASET, path=str(OUT_DIR), unzip=True)
    print(f"✅ Dataset descargado en {OUT_DIR}/")


def download_with_subprocess():
    """Fallback: descarga usando el CLI de kaggle"""
    import subprocess
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["kaggle", "datasets", "download", "-d", DATASET,
         "-p", str(OUT_DIR), "--unzip"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ Descargado con CLI kaggle en {OUT_DIR}/")
    return True


def verify_csv():
    """Verifica que el CSV descargado sea el correcto"""
    csv_path = OUT_DIR / FILENAME
    if not csv_path.exists():
        # Buscar cualquier CSV en la carpeta
        csvs = list(OUT_DIR.glob("*.csv"))
        if csvs:
            csv_path = csvs[0]
            print(f"⚠️  CSV encontrado con nombre distinto: {csv_path.name}")
        else:
            print("❌ No se encontró ningún CSV en ./data/")
            return False

    import csv
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows   = sum(1 for _ in reader)

    expected_cols = [
        "Ticket ID", "Customer Name", "Customer Email", "Customer Age",
        "Customer Gender", "Product Purchased", "Date of Purchase",
        "Ticket Type", "Ticket Subject", "Ticket Status",
        "Ticket Priority", "Ticket Channel", "Customer Satisfaction Rating"
    ]
    missing = [c for c in expected_cols if c not in header]

    print(f"📊 CSV: {rows:,} filas × {len(header)} columnas")
    if missing:
        print(f"⚠️  Columnas faltantes: {missing}")
    else:
        print(f"✅ Todas las columnas requeridas presentes")

    if csv_path.name != FILENAME:
        target = OUT_DIR / FILENAME
        shutil.copy(csv_path, target)
        print(f"✅ Renombrado a: {target}")

    return True


def main():
    print("=" * 60)
    print("  Kaggle Dataset Downloader — Customer Support Tickets")
    print("=" * 60)
    print(f"  Dataset : {DATASET}")
    print(f"  Destino : {OUT_DIR.resolve()}/{FILENAME}")
    print("=" * 60)
    print()

    # Si ya existe, no descargar de nuevo
    existing = OUT_DIR / FILENAME
    if existing.exists():
        size = existing.stat().st_size / 1024
        print(f"✅ CSV ya existe ({size:.0f} KB). Omitiendo descarga.")
        print(f"   Para forzar re-descarga: rm {existing}")
        verify_csv()
        return

    if not setup_kaggle_credentials():
        sys.exit(1)

    try:
        download_with_kaggle_api()
    except Exception as e:
        print(f"⚠️  API falló ({e}), intentando con CLI...")
        if not download_with_subprocess():
            sys.exit(1)

    if not verify_csv():
        sys.exit(1)

    print()
    print("✅ Listo. Siguiente paso:")
    print("   make ingest   ← carga el CSV a DuckDB")


if __name__ == "__main__":
    main()
