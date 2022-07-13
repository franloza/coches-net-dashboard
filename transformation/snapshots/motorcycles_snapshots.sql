{% snapshot motorcycles_snapshots %}
{{
    config(
      target_schema='snapshots',
      strategy='check',
      check_cols = 'all',
      unique_key='id',
      invalidate_hard_deletes=True,
    )
}}

select distinct
    id,
    creationDate,
    title,
    url,
    km,
    year,
    cubicCapacity,
    mainProvince,
    fuelType,
    isFinanced,
    isCertified,
    isProfessional,
    publishedDate,
    price_amount,
    location_mainProvince,
    warranty_literal,
    offerType_literal
from {{ source('coches_net', 'motorcycles') }}
-- The API produces duplicates due to pagination
qualify row_number() over (partition by id order by publishedDate desc) = 1
{% endsnapshot %}
