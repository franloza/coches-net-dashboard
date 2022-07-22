select
    id,
    creationDate::timestamp as creation_date,
    title,
    'www.coches.net' || url as url,
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
    price_financedAmount as financed_price,
    price_hasTaxes::boolean as price_has_taxes,
    warranty_months::int as warranty_months,
    offerType_literal as offer_type,
    hasStock::boolean as has_stock,
    environmentalLabel as environmental_label,
    resources
from {{ source('coches_net', 'cars') }}
-- The API produces duplicates due to pagination
qualify row_number() over (partition by id order by published_date desc) = 1
