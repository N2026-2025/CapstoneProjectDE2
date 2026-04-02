

with source as (

    select * from "support"."main"."stg_tickets"

),

dim_customers as (

    select distinct
        customer_id,
        customer_name,
        customer_email,
        customer_age,
        gender as customer_gender

    from source
    where customer_id is not null

)

select * from dim_customers