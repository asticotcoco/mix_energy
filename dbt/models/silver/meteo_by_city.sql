{{ config(
    alias='meteo_by_city',
    materialized='table'
) }}

WITH unioned AS (
    {{ union_city_sources('meteo_source', 'meteo_') }}
)

SELECT
    city_name,
    SAFE_CAST(time AS TIMESTAMP) AS time,
    * EXCEPT(city_name, time)
FROM unioned
WHERE SAFE_CAST(time AS TIMESTAMP) IS NOT NULL