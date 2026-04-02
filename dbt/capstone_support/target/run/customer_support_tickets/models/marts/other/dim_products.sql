
  
    
    

    create  table
      "support"."main_marts"."dim_products__dbt_tmp"
  
    as (
      

with source as (

    select * from "support"."main_staging"."stg_tickets"

),

dim_products as (

    select distinct
        product_id,
        product_name,
        purchase_date

    from source
    where product_id is not null

)

select * from dim_products
    );
  
  