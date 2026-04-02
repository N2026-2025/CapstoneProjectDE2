
  
    
    

    create  table
      "support"."main_marts"."mart_cx_satisfaction__dbt_tmp"
  
    as (
      

-- Dashboard 3: Priority Matrix + CX
-- Responde:
--   - Correlación edad-satisfacción
--   - Canal con mayor satisfacción
--   - Producto con más quejas críticas
--   - Diferencia de satisfacción por género
--   - Tickets con mayor resolution_hrs → peor rating

with base as (
    select * from "support"."main_staging"."stg_tickets"
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
        end as age_segment,

        -- Bucket de resolución para scatter en Superset
        case
            when resolution_hrs < 6   then '0-6h'
            when resolution_hrs < 24  then '6-24h'
            when resolution_hrs < 72  then '1-3 days'
            else                           '3+ days'
        end as resolution_bucket

    from base
)

select
    ticket_channel,
    ticket_priority,
    ticket_type,
    ticket_status,
    product_purchased,
    customer_gender,
    age_segment,
    resolution_bucket,

    count(*)                as total_tickets,
    avg(satisfaction_rating) as avg_satisfaction,
    avg(resolution_hrs)      as avg_resolution_hrs,
    avg(first_response_hrs)  as avg_first_response_hrs,

    -- Para Priority Matrix heatmap
    sum(case when ticket_priority = 'critical' then 1 else 0 end) as critical_count,
    sum(case when ticket_status   = 'closed'   then 1 else 0 end) as closed_count,

    round(
        100.0 * sum(case when ticket_status='closed' then 1 else 0 end) / count(*)
    , 1) as pct_closed

from enriched
group by 1,2,3,4,5,6,7,8
    );
  
  