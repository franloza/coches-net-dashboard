{% snapshot cars_snapshots %}
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
    hasUrge,
    environmentalLabel,
    price_amount,
    price_financedAmount,
    price_taxTypeId,
    price_hasTaxes,
    location_mainProvince,
    warranty_id,
    warranty_months,
    offerType_literal,
    hasStock
from {{ source('coches_net', 'cars') }}
{% endsnapshot %}
