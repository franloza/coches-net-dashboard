select
    id,
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
    resources
from {{ source('coches_net', 'motorcycles') }}
-- The API produces duplicates due to pagination
qualify row_number() over (partition by id order by published_date desc) = 1
