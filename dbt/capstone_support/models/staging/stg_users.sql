{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'customer_support_tickets') }}
)

select
    distinct
    {{ dbt_utils.generate_surrogate_key(['"Customer Name"', '"Customer Email"']) }} as user_id,
    "Customer Name" as name,
    "Customer Email" as email
from {{ source('raw', 'customer_support_tickets') }}
