
  
    
    

    create  table
      "support"."main_marts"."dim_agents__dbt_tmp"
  
    as (
      

with source as (

    select * from "support"."main_staging"."stg_tickets"

),

dim_agents as (

    select distinct
        agent as agent_id,
        agent_team,
        agent_role

    from source
    where agent is not null

)

select * from dim_agents
    );
  
  