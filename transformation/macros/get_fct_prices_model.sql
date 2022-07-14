{% macro get_fct_prices_model(vehicle_type) %}

{% set primary_key = vehicle_type + '_id' %}
{% set vehicle_type_plural = vehicle_type + 's' %}

with {{ vehicle_type_plural }} as (

    select *,
        valid_to::date as valid_to_date,
        valid_from::date as valid_from_date
    from {{ ref('stg_' + vehicle_type_plural + '_snapshots') }}

),

dates as (

    select * from {{ ref('dim_date') }}

),

deduplicated as (

    select
        *
    from {{ vehicle_type_plural }}
    qualify row_number() over (partition by {{ primary_key }}, valid_from_date order by version desc) = 1

),

spined as (

    select
        deduplicated.{{ primary_key }},
        deduplicated.scd_id,
        deduplicated.price,
        dates.date_key
    from deduplicated
    left join dates
        on dates.date_key >= deduplicated.valid_from_date
            and dates.date_key < deduplicated.valid_to_date
    where dates.date_key <= (select max(creation_date)::date from deduplicated)
        and dates.date_key >= (select min(creation_date)::date from deduplicated)

)

select
    date_key,
    {{ primary_key }},
    scd_id,
    price
from spined

{% endmacro %}
