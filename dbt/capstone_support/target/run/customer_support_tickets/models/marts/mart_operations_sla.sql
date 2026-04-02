
  
    
    

    create  table
      "support"."main_marts"."mart_operations_sla__dbt_tmp"
  
    as (
      

-- Dashboard 1 & 2: Operations Overview + Channel Performance
-- Responde:
--   - Tiempo promedio de primera respuesta por canal
--   - % tickets resueltos en < 24 horas
--   - Backlog actual (open + pending)
--   - % tickets Critical sin resolver
--   - Carga por día de semana y mes

with base as (
    select * from "support"."main_staging"."stg_tickets"
),

per_channel as (
    select
        ticket_channel,
        ticket_priority,
        ticket_status,
        ticket_type,

        extract('dow'   from purchase_date) as day_of_week,
        strftime(purchase_date, '%A')       as day_name,
        extract('month' from purchase_date) as month_num,
        strftime(purchase_date, '%B')       as month_name,
        extract('year'  from purchase_date) as year,

        first_response_hrs,
        resolution_hrs,
        satisfaction_rating,

        -- SLA flags
        case when resolution_hrs <= 24 then 1 else 0 end          as resolved_under_24h,
        case when ticket_status in ('open','pending customer response')
             then 1 else 0 end                                     as is_backlog,
        case when ticket_priority = 'critical'
              and ticket_status != 'closed' then 1 else 0 end      as is_critical_unresolved

    from base
)

select
    ticket_channel,
    ticket_priority,
    ticket_status,
    ticket_type,
    day_of_week,
    day_name,
    month_num,
    month_name,
    year,

    count(*)                                  as total_tickets,
    avg(first_response_hrs)                   as avg_first_response_hrs,
    avg(resolution_hrs)                       as avg_resolution_hrs,
    avg(satisfaction_rating)                  as avg_satisfaction,

    sum(resolved_under_24h)                   as tickets_resolved_under_24h,
    round(
        100.0 * sum(resolved_under_24h) / count(*), 1
    )                                         as pct_resolved_under_24h,

    sum(is_backlog)                           as backlog_count,
    sum(is_critical_unresolved)               as critical_unresolved_count,

    round(
        100.0 * sum(is_critical_unresolved)
            / nullif(sum(case when ticket_priority='critical' then 1 end), 0)
    , 1)                                      as pct_critical_unresolved

from per_channel
group by 1,2,3,4,5,6,7,8,9
    );
  
  