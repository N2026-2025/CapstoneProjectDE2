
  
    
    

    create  table
      "support"."main"."fact_tickets__dbt_tmp"
  
    as (
      

with source as (

    select * from "support"."main"."stg_tickets"

),

fact as (

    select
        ticket_id,

        customer_id,
        agent as agent_id,
        product_id,

        created_at,
        resolved_at,

        first_response_time,
        time_to_resolution,
        customer_satisfaction_rating,
        status,
        priority

    from source

)

select * from fact
    );
  
  