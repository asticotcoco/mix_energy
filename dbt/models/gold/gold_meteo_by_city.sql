{{ config(
    alias='meteo_by_city',
    materialized='table'
) }}

WITH source_rows AS (
    SELECT
        city_name,
        DATE(time) AS date,
        EXTRACT(YEAR FROM time) AS annee,
        EXTRACT(MONTH FROM time) AS mois,
        EXTRACT(DAY FROM time) AS jour,
        time,
        SAFE_CAST(temperature_2m AS FLOAT64) AS temperature_2m,
        SAFE_CAST(relative_humidity_2m AS FLOAT64) AS relative_humidity_2m,
        SAFE_CAST(precipitation_probability AS FLOAT64) AS precipitation_probability,
        SAFE_CAST(precipitation AS FLOAT64) AS precipitation,
        SAFE_CAST(rain AS FLOAT64) AS rain,
        SAFE_CAST(snowfall AS FLOAT64) AS snowfall,
        SAFE_CAST(pressure_msl AS FLOAT64) AS pressure_msl,
        SAFE_CAST(cloud_cover AS FLOAT64) AS cloud_cover,
        SAFE_CAST(wind_speed_10m AS FLOAT64) AS wind_speed_10m,
        SAFE_CAST(wind_gusts_10m AS FLOAT64) AS wind_gusts_10m,
        SAFE_CAST(weather_code AS INT64) AS weather_code
    FROM {{ ref('meteo_by_city') }}
    WHERE time IS NOT NULL
)

SELECT
    city_name,
    date,
    annee,
    mois,
    jour,
    COUNT(*) AS hourly_observation_count,
    MAX(time) AS last_observation_at,
    AVG(temperature_2m) AS avg_temperature_2m,
    MIN(temperature_2m) AS min_temperature_2m,
    MAX(temperature_2m) AS max_temperature_2m,
    AVG(relative_humidity_2m) AS avg_relative_humidity_2m,
    AVG(precipitation_probability) AS avg_precipitation_probability,
    SUM(precipitation) AS total_precipitation,
    SUM(rain) AS total_rain,
    SUM(snowfall) AS total_snowfall,
    AVG(pressure_msl) AS avg_pressure_msl,
    AVG(cloud_cover) AS avg_cloud_cover,
    AVG(wind_speed_10m) AS avg_wind_speed_10m,
    MAX(wind_gusts_10m) AS max_wind_gusts_10m,
    ARRAY_AGG(weather_code IGNORE NULLS ORDER BY time DESC LIMIT 1)[SAFE_OFFSET(0)] AS latest_weather_code
FROM source_rows
GROUP BY city_name, date, annee, mois, jour
ORDER BY date ASC, city_name ASC