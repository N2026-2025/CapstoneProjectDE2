
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        ticket_priority as value_field,
        count(*) as n_records

    from "support"."main_staging"."stg_tickets"
    group by ticket_priority

)

select *
from all_values
where value_field not in (
    'low','medium','high','critical'
)



  
  
      
    ) dbt_internal_test