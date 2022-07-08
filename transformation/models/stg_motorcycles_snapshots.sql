select
    dbt_scd_id as scd_id,
    id as motorcycle_id,
    creationDate::timestamp as creation_date,
    title,
    'www.motos.net' || url as url,
    coalesce(km, 0)::int as km,
    year::int as year,
    cubicCapacity as cubic_capacity,
    location_mainProvince as main_province,
    fuelType as fuel_type,
    isFinanced::boolean as is_financed,
    isCertified::boolean as is_certified,
    isProfessional as is_professional,
    publishedDate::timestamp as published_date,
    price_amount as price,
    warranty_literal as warranty,
    offerType_literal as offer_type,
    dbt_updated_at as updated_at,
    dbt_valid_to is null as is_current_version,
    row_number() over (partition by id order by dbt_valid_from) as version,
    dbt_valid_from as valid_from,
    coalesce(
        dbt_valid_to,
        '{{ var("the_distant_future") }}'::timestamp
    ) as valid_to

from {{ source('snapshots', 'motorcycles_snapshots') }}
