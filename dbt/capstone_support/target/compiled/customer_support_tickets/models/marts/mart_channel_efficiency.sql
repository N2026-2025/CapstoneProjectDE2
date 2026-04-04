

-- ============================================================
-- mart_channel_efficiency
-- Pregunta central: ¿Qué canal de atención es más eficiente?
--
-- Responde:
--   Q1. ¿Chat vs Email vs Phone vs Social: cuál resuelve más rápido?
--   Q2. ¿Cada canal atiende bien todos los tipos de ticket o hay especialización?
--   Q3. ¿El canal cambia el nivel de satisfacción del cliente?
--   Q4. ¿Hay canales donde los tickets críticos se atascan más?
--   Q5. ¿Qué canal tiene mayor volumen pero peor performance? (cuello de botella)
-- ============================================================

with base as (
    select * from "support"."main_staging"."stg_tickets"
),

-- Global benchmarks para comparar
global_bench as (
    select
        count(*)                                                as g_total,
        avg(satisfaction_rating)                               as g_avg_sat,
        round(100.0 * sum(case when ticket_status='closed' then 1 else 0 end)
              / count(*), 1)                                   as g_pct_closed,
        round(100.0 * sum(case when is_open_no_response then 1 else 0 end)
              / count(*), 1)                                   as g_pct_no_response
    from base
),

channel_metrics as (
    select
        b.ticket_channel,
        b.ticket_type,
        b.ticket_priority,

        count(*)                                                as total_tickets,

        -- Volumen relativo
        round(100.0 * count(*) / max(g.g_total), 1)            as pct_of_all_tickets,

        -- Resolución
        sum(case when b.ticket_status='closed' then 1 else 0 end)  as resolved_count,
        round(100.0 * sum(case when b.ticket_status='closed' then 1 else 0 end)
              / count(*), 1)                                   as pct_resolved,

        -- Tickets sin ninguna respuesta aún
        sum(case when b.is_open_no_response then 1 else 0 end) as no_response_count,
        round(100.0 * sum(case when b.is_open_no_response then 1 else 0 end)
              / count(*), 1)                                   as pct_no_response,

        -- Satisfacción
        avg(b.satisfaction_rating)                             as avg_satisfaction,

        -- Críticos sin resolver
        sum(case when b.ticket_priority='critical'
                  and b.ticket_status != 'closed' then 1 else 0 end) as critical_open,

        -- Comparación vs benchmark global
        round(
            (100.0 * sum(case when b.ticket_status='closed' then 1 else 0 end) / count(*))
            - max(g.g_pct_closed)
        , 1)                                                   as resolution_vs_global,

        round(
            coalesce(avg(b.satisfaction_rating), 3) - max(g.g_avg_sat)
        , 2)                                                   as satisfaction_vs_global,

        -- Eficiencia compuesta: ¿canal bueno o malo?
        case
            when round(100.0 * sum(case when b.ticket_status='closed' then 1 else 0 end)
                       / count(*), 1) > max(g.g_pct_closed)
             and coalesce(avg(b.satisfaction_rating),3) > max(g.g_avg_sat)
                then '⭐ Mejor que promedio'
            when round(100.0 * sum(case when b.ticket_status='closed' then 1 else 0 end)
                       / count(*), 1) < max(g.g_pct_closed)
             and coalesce(avg(b.satisfaction_rating),3) < max(g.g_avg_sat)
                then '⚠️ Peor que promedio'
            else '➡️ Promedio'
        end                                                    as channel_rating

    from base b
    cross join global_bench g
    group by 1,2,3
)

select * from channel_metrics
order by ticket_channel, pct_resolved asc