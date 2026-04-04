

-- ============================================================
-- mart_operations_sla_partitioned
-- 
-- PARTICIONADO LÓGICO EN DUCKDB
-- ─────────────────────────────────────────────────────────────
-- DuckDB no tiene particionado físico tipo BigQuery/Hive, pero
-- se puede simular con columnas de partición + índices implícitos
-- que el optimizador usa para pruning automático.
--
-- Criterio elegido:
--   PARTITION KEY → year (filtro más común en series temporales)
--   CLUSTER KEY   → ticket_channel (filtro más frecuente en dashboards)
--
-- Por qué tiene sentido:
--   • 99% de las queries filtran por canal (sidebar de Streamlit)
--   • Las queries de SLA siempre filtran por período (month/year)
--   • DuckDB hace zone-map pruning: lee solo row groups relevantes
--     cuando los datos están ordenados por estas columnas
--
-- Equivalente en BigQuery: PARTITION BY year CLUSTER BY ticket_channel
-- ============================================================

with base as (
    select * from "support"."main_staging"."stg_tickets"
),

enriched as (
    select
        *,
        extract('year'  from purchase_date)::integer  as part_year,
        extract('month' from purchase_date)::integer  as part_month,

        -- SLA flags (iguales al mart original)
        case when ticket_status in ('open','pending customer response')
             then 1 else 0 end                         as is_backlog,
        case when ticket_priority = 'critical'
              and ticket_status != 'closed' then 1 else 0 end as is_critical_unresolved

    from base
)

select
    -- ── Columnas de partición primero (DuckDB las usa para zone-map pruning)
    part_year,
    part_month,
    ticket_channel,          -- cluster key

    -- ── Resto de dimensiones
    ticket_priority,
    ticket_status,
    ticket_type,
    ticket_subject,

    -- ── Métricas
    count(*)                                 as total_tickets,
    avg(first_response_hour_of_day)          as avg_first_response_hrs,
    avg(resolution_hour_of_day)              as avg_resolution_hrs,
    avg(satisfaction_rating)                 as avg_satisfaction,
    sum(is_backlog)                          as backlog_count,
    sum(is_critical_unresolved)              as critical_unresolved_count,

    round(
        100.0 * sum(is_critical_unresolved)
            / nullif(sum(case when ticket_priority='critical' then 1 end), 0)
    , 1)                                     as pct_critical_unresolved

from enriched

-- ── ORDER BY = cluster key explícito
-- DuckDB escribe los row groups en este orden → pruning eficiente
-- para queries tipo: WHERE ticket_channel = 'email' AND part_year = 2021
group by 1,2,3,4,5,6,7
order by part_year, part_month, ticket_channel