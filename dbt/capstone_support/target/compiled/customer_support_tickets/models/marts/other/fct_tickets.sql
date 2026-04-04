SELECT
    ticket_id,
    user_id,
    created_at,
    closed_at,
    status,
    -- KPI: TTR (Time to Resolution)
    timestamp_diff(closed_at, created_at, MINUTE) as ttr_minutes,
    -- KPI: FIRST RESPONSE TIME
    timestamp_diff(first_interaction_at, created_at, MINUTE) as frt_minutes
FROM "support"."main_staging"."stg_tickets"
-- EFECTIVIZA KPI: Eficiencia operativa. 
-- Si el TTR sube, necesitás más personal o mejor automatización.