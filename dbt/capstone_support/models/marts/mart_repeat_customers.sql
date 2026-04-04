{{ config(materialized='table') }}

-- ============================================================
-- mart_repeat_customers
-- Pregunta central: ¿Hay clientes que abren múltiples tickets?
--                   ¿Son señal de churn inminente?
--
-- Responde:
--   Q1. ¿Cuántos clientes abrieron más de 1 ticket? (recurrencia)
--   Q2. ¿Los clientes recurrentes tienen peor satisfacción?
--   Q3. ¿Qué productos generan clientes recurrentes?
--   Q4. ¿El canal preferido cambia entre el 1er y 2do ticket?
--   Q5. Segmentación: clientes de alto riesgo de churn
-- ============================================================

with base as (
    select * from {{ ref('stg_tickets') }}
),

-- Número de tickets por cliente
customer_ticket_counts as (
    select
        customer_id,
        customer_name,
        customer_gender,
        customer_age,
        count(*)                                                    as ticket_count,
        count(distinct product_purchased)                           as products_with_issues,
        count(distinct ticket_type)                                 as issue_type_variety,

        -- Satisfacción promedio del cliente
        avg(satisfaction_rating)                                    as avg_satisfaction,
        min(satisfaction_rating)                                    as min_satisfaction,

        -- ¿Tiene tickets sin resolver?
        sum(case when is_unresolved then 1 else 0 end)              as unresolved_count,

        -- ¿Alguna vez fue Critical?
        max(case when ticket_priority = 'critical' then 1 else 0 end) as had_critical,

        -- Canal más usado
        mode() within group (order by ticket_channel)               as preferred_channel,

        -- Producto más problemático
        mode() within group (order by product_purchased)            as most_complained_product,

        -- Rango de fechas de actividad
        min(purchase_date)                                          as first_purchase,
        max(purchase_date)                                          as last_purchase

    from base
    group by 1,2,3,4
),

-- Segmentación de riesgo de churn
segmented as (
    select
        *,
        case
            when ticket_count >= 3 then 'Recurrente frecuente (3+)'
            when ticket_count = 2  then 'Recurrente (2 tickets)'
            else                        'Primera vez'
        end                                                         as recurrence_segment,

        case
            when ticket_count >= 2
             and (min_satisfaction <= 2 or unresolved_count >= 1
                  or had_critical = 1)
                then '🔴 Churn inminente'
            when ticket_count >= 2
             and avg_satisfaction < 3
                then '🟡 Riesgo de churn'
            when ticket_count >= 2
                then '🟠 Recurrente estable'
            else    '🟢 Sin señales'
        end                                                         as churn_risk
    from customer_ticket_counts
)

select
    customer_id,
    customer_name,
    customer_gender,
    customer_age,
    ticket_count,
    products_with_issues,
    issue_type_variety,
    round(avg_satisfaction, 2)  as avg_satisfaction,
    min_satisfaction,
    unresolved_count,
    had_critical,
    preferred_channel,
    most_complained_product,
    first_purchase,
    last_purchase,
    recurrence_segment,
    churn_risk
from segmented
order by ticket_count desc, avg_satisfaction asc
