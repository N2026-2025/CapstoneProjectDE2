
  
  create view "support"."main"."stg_tickets__dbt_tmp" as (
    

with source as (
    select * from "support"."raw"."customer_support_tickets"
),

cleaned as (
    select
        -- La clave subrogada va ACÁ adentro del select
        md5(cast(coalesce(cast("Customer Name" as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast("Customer Email" as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as customer_id,
        cast("Ticket ID"           as varchar)  as ticket_id,
        lower(trim("Customer Name"))            as customer_name,
        cast("Customer Age"        as integer)  as customer_age,
        lower(trim("Customer Gender"))          as customer_gender,
        lower(trim("Product Purchased"))        as product_purchased,
        cast("Date of Purchase"    as date)     as purchase_date,
        lower(trim("Ticket Type"))              as ticket_type,
        lower(trim("Ticket Subject"))           as ticket_subject,
        lower(trim("Ticket Status"))            as ticket_status,
        lower(trim("Ticket Priority"))          as ticket_priority,
        lower(trim("Ticket Channel"))           as ticket_channel,
        epoch(cast("First Response Time" as timestamp)) / 3600.0  as first_response_hrs,
        epoch(cast("Time to Resolution"  as timestamp)) / 3600.0  as resolution_hrs,
        cast("Customer Satisfaction Rating" as double) as satisfaction_rating,
        _ingested_at
    from source
)

select * from cleaned
  );
