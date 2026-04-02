
  
  create view "support"."main_staging"."stg_users__dbt_tmp" as (
    

with source as (
    select * from "support"."raw"."customer_support_tickets"
)

select
    distinct
    md5(cast(coalesce(cast("Customer Name" as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast("Customer Email" as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as user_id,
    "Customer Name" as name,
    "Customer Email" as email
from "support"."raw"."customer_support_tickets"
  );
