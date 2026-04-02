{{ config(materialized='table') }}

WITH base_metrics AS (
    SELECT 
        ticket_id,
        customer_id,
        status,
        created_at,
        closed_at,
        cost_of_acquisition, -- CAC
        revenue_generated,    -- Para ROI
        nps_score,           -- NPS
        -- KPI: Ticket Resolution Time (TRT)
        DATEDIFF('hour', created_at, closed_at) as resolution_time_hr
    FROM {{ ref('stg_tickets') }}
)

SELECT 
    customer_id,
    -- KPI: ROI (Rentabilidad por ticket/cliente)
    SUM(revenue_generated) / NULLIF(SUM(cost_of_acquisition), 0) as roi_ratio,
    -- KPI: CAC Promedio
    AVG(cost_of_acquisition) as avg_cac,
    -- KPI: NPS Promedio (Satisfacción)
    AVG(nps_score) as avg_nps,
    -- KPI: Eficiencia Operativa
    AVG(resolution_time_hr) as avg_trt
FROM base_metrics
GROUP BY 1
