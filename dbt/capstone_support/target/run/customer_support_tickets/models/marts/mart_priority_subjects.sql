
  
    
    

    create  table
      "support"."main_marts"."mart_priority_subjects__dbt_tmp"
  
    as (
      

-- Dashboard 3 & 5: Priority Matrix + Product Complaints
-- Responde:
--   - Subjects más frecuentes como Critical
--   - Sistema de prioridades vs satisfacción real
--   - Tipo de ticket con mayor tasa de escalamiento
--   - Productos con más tickets críticos

with base as (
    select * from "support"."main_staging"."stg_tickets"
)

select
    ticket_subject,
    ticket_type,
    ticket_priority,
    product_purchased,

    count(*)                     as total_tickets,
    avg(satisfaction_rating)     as avg_satisfaction,
    avg(resolution_hrs)          as avg_resolution_hrs,

    -- % no resueltos (proxy de escalamiento)
    round(
        100.0 * sum(case when ticket_status != 'closed' then 1 else 0 end) / count(*)
    , 1) as pct_unresolved,

    sum(case when ticket_priority = 'critical' then 1 else 0 end) as critical_count,
    sum(case when ticket_priority = 'high'     then 1 else 0 end) as high_count,

    -- ¿La prioridad asignada coincide con la satisfacción?
    -- Si critical tiene alta satisfacción, el sistema de prioridades es inconsistente
    case
        when avg(satisfaction_rating) >= 4
         and ticket_priority in ('critical','high') then 'Prioridad sobreasignada'
        when avg(satisfaction_rating) <= 2
         and ticket_priority in ('low','medium')    then 'Prioridad subasignada'
        else 'Consistente'
    end as priority_alignment

from base
group by 1,2,3,4
order by critical_count desc
    );
  
  