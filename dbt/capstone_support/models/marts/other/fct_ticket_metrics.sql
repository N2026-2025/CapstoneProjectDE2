{{ config(materialized='incremental', unique_key='ticket_id') }}

SELECT
    ticket_id,
    customer_id,
    status,
    -- KPI: Eficiencia (Segundos para cerrar)
    DATEDIFF('second', created_at, closed_at) as resolution_time_sec,
    -- KPI: Calidad (¿Requirió más de 3 interacciones?)
    CASE WHEN total_interactions > 3 THEN 1 ELSE 0 END as is_complex_issue,
    -- KPI: Ingresos (Valor del cliente afectado)
    c.customer_lifetime_value
FROM {{ ref('stg_tickets') }} t
JOIN {{ ref('dim_customers') }} c ON t.customer_id = c.id
