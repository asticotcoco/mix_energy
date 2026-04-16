{{ config(
    alias='nat_tr_predi',
    materialized='table'
) }}

WITH source_rows AS (
    SELECT
        {{ safe_float64_from_raw('consommation') }} AS consommation,
        {{ safe_float64_from_raw('prevision_j1') }} AS prevision_j1,
        {{ safe_float64_from_raw('prevision_j') }} AS prevision_j,
        SAFE_CAST(date_heure AS TIMESTAMP) AS date_heure
    FROM {{ source('nat_source', 'eco2mix_national_tr') }}
)

SELECT
consommation,
prevision_j1,
prevision_j,
EXTRACT(YEAR FROM date_heure) AS year,
EXTRACT(MONTH FROM date_heure) AS month,
EXTRACT(DAY FROM date_heure) AS day,
EXTRACT(HOUR FROM date_heure) AS hour,
EXTRACT(MINUTE FROM date_heure) AS minute
FROM source_rows
WHERE date_heure IS NOT NULL
  AND EXTRACT(YEAR FROM date_heure) = EXTRACT(YEAR FROM CURRENT_DATE())
  AND consommation IS NOT NULL
order by date_heure asc
