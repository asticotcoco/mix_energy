{{ config(
    alias='air_quality_by_city',
    materialized='table'
) }}

WITH ranked_zone_snapshots AS (
    SELECT
        city_name,
        DATE(date_dif) AS date,
        EXTRACT(YEAR FROM DATE(date_dif)) AS annee,
        EXTRACT(MONTH FROM DATE(date_dif)) AS mois,
        EXTRACT(DAY FROM DATE(date_dif)) AS jour,
        date_maj,
        code_zone,
        lib_zone,
        type_zone,
        lib_qual,
        SAFE_CAST(code_qual AS INT64) AS code_qual,
        SAFE_CAST(code_no2 AS INT64) AS code_no2,
        SAFE_CAST(code_o3 AS INT64) AS code_o3,
        SAFE_CAST(code_pm10 AS INT64) AS code_pm10,
        SAFE_CAST(code_pm25 AS INT64) AS code_pm25,
        SAFE_CAST(code_so2 AS INT64) AS code_so2,
        SAFE_CAST(x_wgs84 AS FLOAT64) AS x_wgs84,
        SAFE_CAST(y_wgs84 AS FLOAT64) AS y_wgs84,
        ROW_NUMBER() OVER (
            PARTITION BY city_name, DATE(date_dif), code_zone
            ORDER BY date_maj DESC, lib_zone ASC
        ) AS snapshot_rank
    FROM {{ ref('air_quality_by_city') }}
    WHERE date_dif IS NOT NULL
),

latest_zone_snapshots AS (
    SELECT * EXCEPT(snapshot_rank)
    FROM ranked_zone_snapshots
    WHERE snapshot_rank = 1
)

SELECT
    city_name,
    date,
    annee,
    mois,
    jour,
    COUNT(*) AS zone_count,
    MAX(date_maj) AS last_update_at,
    AVG(code_qual) AS avg_quality_code,
    MAX(code_qual) AS max_quality_code,
    AVG(code_no2) AS avg_no2_code,
    MAX(code_no2) AS max_no2_code,
    AVG(code_o3) AS avg_o3_code,
    MAX(code_o3) AS max_o3_code,
    AVG(code_pm10) AS avg_pm10_code,
    MAX(code_pm10) AS max_pm10_code,
    AVG(code_pm25) AS avg_pm25_code,
    MAX(code_pm25) AS max_pm25_code,
    AVG(code_so2) AS avg_so2_code,
    MAX(code_so2) AS max_so2_code,
    ARRAY_AGG(lib_qual IGNORE NULLS ORDER BY code_qual DESC, lib_zone ASC LIMIT 1)[SAFE_OFFSET(0)] AS worst_quality_label,
    ARRAY_AGG(lib_zone IGNORE NULLS ORDER BY code_qual DESC, lib_zone ASC LIMIT 1)[SAFE_OFFSET(0)] AS worst_quality_zone,
    ARRAY_AGG(type_zone IGNORE NULLS ORDER BY code_qual DESC, lib_zone ASC LIMIT 1)[SAFE_OFFSET(0)] AS worst_quality_zone_type
FROM latest_zone_snapshots
GROUP BY city_name, date, annee, mois, jour
ORDER BY date ASC, city_name ASC