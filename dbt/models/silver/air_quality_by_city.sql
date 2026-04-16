{{ config(
    alias='air_quality_by_city',
    materialized='table'
) }}

WITH unioned AS (
    {{ union_city_sources('air_quality_source', 'air_quality_') }}
)

SELECT
    city_name,
    SAFE_CAST(date_maj AS TIMESTAMP) AS date_maj,
    SAFE_CAST(date_dif AS DATE) AS date_dif,
    SAFE_CAST(date_ech AS DATE) AS date_ech,
    SAFE_CAST(x_reg AS FLOAT64) AS x_reg,
    SAFE_CAST(x_wgs84 AS FLOAT64) AS x_wgs84,
    SAFE_CAST(y_reg AS FLOAT64) AS y_reg,
    SAFE_CAST(y_wgs84 AS FLOAT64) AS y_wgs84,
    * EXCEPT(city_name, date_maj, date_dif, date_ech, x_reg, x_wgs84, y_reg, y_wgs84)
FROM unioned
WHERE SAFE_CAST(date_maj AS TIMESTAMP) IS NOT NULL