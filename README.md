# Capstone: Customer Support Ticket Analytics
**Data Engineering Zoomcamp — Proyecto Final**

---

## Stack tecnológico

| Capa | Herramienta | Por qué |
|------|-------------|---------|
| Orquestación | Kestra | Flows YAML, UI web, sin código extra |
| Storage | DuckDB | OLAP embebido, perfecto para <5M filas |
| Transform | dbt-duckdb | Modelos ya hechos, lineage, tests |
| Visualización | Streamlit o Apache Superset | Conecta a DuckDB directo |
| Streaming (opcional) | Kafka nativo (bitnami) | ~300MB vs ~600MB de Redpanda |
| Exploración | Jupyter | Notebooks de análisis |

**¿Por qué NO Redpanda?**
Redpanda pesa ~600MB de imagen y corre un proceso pesado. `bitnami/kafka:3.7` hace exactamente lo mismo para este proyecto usando ~300MB. Si no necesitás streaming en producción, dejalo comentado en el docker-compose.

**¿Por qué NO Spark ni Postgres?**
El dataset tiene entre 8K y 200K filas. DuckDB corre queries analíticas a esa escala en milisegundos. Spark sería over-engineering y Postgres es OLTP, no OLAP.

---

## Dataset

**Primary:** [Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) — CSV, ~8,469 filas

**Columnas clave:**
- `Ticket ID`, `Customer Name`, `Customer Email`, `Customer Age`
- `Customer Gender`, `Product Purchased`, `Date of Purchase`
- `Ticket Type`, `Ticket Subject`, `Ticket Description`
- `Ticket Status` (Open / Closed / Pending Customer Response)
- `Resolution`, `Ticket Priority` (Critical / High / Medium / Low)
- `Ticket Channel` (Email / Chat / Phone / Social media)
- `First Response Time`, `Time to Resolution`
- `Customer Satisfaction Rating` (1-5)

**Alternativa batch mayor:**
[200K Records Version](https://www.kaggle.com/datasets/mirzayasirabdullah07/customer-support-tickets-dataset-200k-records)

---

## Preguntas analíticas que podés responder



---

## Estructura del proyecto

```
capstone_support/
├── Makefile                    ← All
├── docker-compose.yml          ← Stack completo
├── .env                        ← Credenciales (no commitear)
├── flows/
│   ├── 01_ingest_csv.yml       ← Extract + Load → DuckDB raw
│   ├── 02_run_dbt.yml          ← Trigger dbt tras ingesta
│   └── 03_kafka_stream.yml     ← Streaming opcional
├── dbt/
│   └── capstone_support/       ← Tu proyecto dbt existente
│         ├─ models
|             └── marts
|               └── mart_cx_satisfaction.sql
|               └── mart_fairness.sql
|               └── mart_operations_sla.sql
|               └── mart_priority.sql
|         ├─ staging
|               └── schema.yml
|               └── sources.yml
|               └── stg_tickets.sql
|               └── stg_users.sql
|         ├─ seeds
                └──customer_support_tickets.csv
|         ├─ target
|         ├─ tests
|         ├─ dbt_project.yml
|         ├─ packages.yml
|         ├─ packages-lock.yml
|    ├─ Dockerfile.dbt
|    ├─ dockerfile
|    ├─ package-lock.yml
|    ├─ profiles.yml
├── scripts/
│   └── init_duckdb.py          ← Setup inicial de schemas
├── notebooks/
│   ├── 1_ingestion.ipynb 
│   ├── 2_batch_processing_tickets.ipynb
│   ├── 2_transformation.ipynb
│   ├── 3_analytics_and_output.ipynb
│   └── customer_service1.ipynb
├── duckdb/
│   └── support.duckdb          ← Generado automáticamente
└── data/
    └── customer_support_tickets.csv
```

---

## Capas de DuckDB

```
raw.*          ← Datos tal cual vienen del CSV (sin transformar)
staging.*      ← Limpieza, tipos, renombrado (dbt)
marts.*        ← Tablas agregadas para dashboards (dbt)
streaming.*    ← Datos que llegan por Kafka (opcional)
```

---

## Dashboards sugeridos en Streamlit.


---
---

## Setup rápido

```bash
# 1. Git clone repo or open codespace

# 2. Levantar el stack 
Make up

# 3. kestra + dbt + streamlit
Make pipeline 

```

---

**Recomendaciones:**
- Kafka queda comentado — activalo solo para el módulo de streaming
