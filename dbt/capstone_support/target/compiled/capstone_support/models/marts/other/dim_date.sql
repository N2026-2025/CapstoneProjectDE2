

with dates as (

    select
        created_at as full_date
    from "support"."main"."stg_tickets"

    union

    select
        resolved_at
    from "support"."main"."stg_tickets"

),

dim_date as (

    select distinct
        full_date,

        extract(year from full_date) as year,
        extract(month from full_date) as month,
        extract(day from full_date) as day,
        extract(dow from full_date) as day_of_week,
        extract(quarter from full_date) as quarter

    from dates
    where full_date is not null

)

select * from dim_date