

WITH metrics AS (
    SELECT 
        *,
        -- KPI: Ticket Resolution Time (TRT)
        EXTRACT(EPOCH FROM (closed_at - created_at))/3600 as trt_hours,
        -- KPI: ROI (Rentabilidad)
        (revenue - cac) / NULLIF(cac, 0) as roi
    FROM "support"."main"."stg_tickets"
)
SELECT 
    category,
    AVG(trt_hours) as avg_resolution_time,
    AVG(cac) as avg_cac,
    AVG(roi) as avg_roi,
    AVG(nps_score) as nps_index,
    COUNT(ticket_id) as total_tickets
FROM metrics
GROUP BY 1