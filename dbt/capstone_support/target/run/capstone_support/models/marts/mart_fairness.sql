
  
    
    

    create  table
      "support"."main"."mart_fairness__dbt_tmp"
  
    as (
      

-- Dashboard 6: Fairness / Bias
-- Responde:
--   - Diferencias sistemáticas en resolución por género
--   - Tickets de grupos demográficos con prioridad diferente
--   - Sesgo en asignación de prioridades por canal

with base as (
    select * from "support"."main"."stg_tickets"
),

enriched as (
    select
        *,
        case
            when customer_age < 25               then 'Gen Z (<25)'
            when customer_age between 25 and 34  then 'Millennial (25-34)'
            when customer_age between 35 and 44  then 'Gen X (35-44)'
            when customer_age between 45 and 59  then 'Boomer (45-59)'
            else                                      'Senior (60+)'
        end as age_segment
    from base
),

-- Baseline global para calcular desvíos
global_avg as (
    select
        avg(resolution_hrs)      as global_avg_resolution,
        avg(first_response_hrs)  as global_avg_frt,
        avg(satisfaction_rating) as global_avg_sat
    from base
)

select
    e.customer_gender,
    e.age_segment,
    e.ticket_channel,
    e.ticket_priority,

    count(*)                     as ticket_count,
    avg(e.resolution_hrs)        as avg_resolution_hrs,
    avg(e.first_response_hrs)    as avg_first_response_hrs,
    avg(e.satisfaction_rating)   as avg_satisfaction,

    -- Desvío respecto al promedio global (+ = peor servicio, - = mejor)
    avg(e.resolution_hrs)    - max(g.global_avg_resolution) as resolution_bias,
    avg(e.first_response_hrs)- max(g.global_avg_frt)        as frt_bias,
    avg(e.satisfaction_rating)-max(g.global_avg_sat)        as satisfaction_bias,

    -- % de tickets asignados a prioridad Critical por grupo
    round(
        100.0 * sum(case when e.ticket_priority='critical' then 1 else 0 end) / count(*)
    , 1) as pct_critical,

    round(
        100.0 * sum(case when e.ticket_status='closed' then 1 else 0 end) / count(*)
    , 1) as pct_resolved

from enriched e
cross join global_avg g
group by 1,2,3,4
    );
  
  