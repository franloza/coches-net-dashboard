

with cars as (

    select *,
        valid_to::date as valid_to_date,
        valid_from::date as valid_from_date
    from {{ ref('stg_cars_snapshots') }}

),

dates as (

    select * from {{ ref('dim_date') }}

),

spined as (

    select
        cars.car_id,
        cars.price,
        dates.date_key
    from cars
    left join dates
        on dates.date_key >= cars.valid_from_date
            and dates.date_key < cars.valid_to_date
    where dates.date_key <= (select max(creation_date)::date from cars)
        and dates.date_key >= (select min(creation_date)::date from cars)

)

select
    date_key,
    car_id,
    price
from spined
