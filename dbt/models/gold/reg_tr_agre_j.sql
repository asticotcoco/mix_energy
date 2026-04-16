{{ config (
    alias='reg_tr_agre_j',
    materialized='incremental',
    unique_key=['date', 'code_insee_region']
) }}

WITH source_rows AS (
    SELECT
        code_insee_region,
        libelle_region,
        nature,
        SAFE_CAST(date AS DATE) AS date,
        {{ safe_float64_from_raw('consommation') }} AS consommation,
        {{ safe_float64_from_raw('thermique') }} AS thermique,
        {{ safe_float64_from_raw('nucleaire') }} AS nucleaire,
        {{ safe_float64_from_raw('eolien') }} AS eolien,
        {{ safe_float64_from_raw('solaire') }} AS solaire,
        {{ safe_float64_from_raw('hydraulique') }} AS hydraulique,
        {{ safe_float64_from_raw('pompage') }} AS pompage,
        {{ safe_float64_from_raw('bioenergies') }} AS bioenergies,
        {{ safe_float64_from_raw('ech_physiques') }} AS ech_physiques,
        {{ safe_float64_from_raw('tco_thermique') }} AS tco_thermique,
        {{ safe_float64_from_raw('tch_thermique') }} AS tch_thermique,
        {{ safe_float64_from_raw('tco_nucleaire') }} AS tco_nucleaire,
        {{ safe_float64_from_raw('tch_nucleaire') }} AS tch_nucleaire,
        {{ safe_float64_from_raw('tco_eolien') }} AS tco_eolien,
        {{ safe_float64_from_raw('tch_eolien') }} AS tch_eolien,
        {{ safe_float64_from_raw('tco_solaire') }} AS tco_solaire,
        {{ safe_float64_from_raw('tch_solaire') }} AS tch_solaire,
        {{ safe_float64_from_raw('tco_hydraulique') }} AS tco_hydraulique,
        {{ safe_float64_from_raw('tch_hydraulique') }} AS tch_hydraulique,
        {{ safe_float64_from_raw('tco_bioenergies') }} AS tco_bioenergies,
        {{ safe_float64_from_raw('tch_bioenergies') }} AS tch_bioenergies
    FROM {{ source('reg_source', 'eco2mix_regional_tr') }}
    {% if is_incremental() %}
        WHERE SAFE_CAST(date AS DATE) >= (SELECT DATE_SUB(MAX(date), INTERVAL 2 DAY) FROM {{ this }})
    {% endif %}
),

valid_rows AS (
    SELECT *
    FROM source_rows
    WHERE date IS NOT NULL
)

SELECT
    code_insee_region,
    libelle_region,
    nature,
    DATE(date) AS date,
    EXTRACT(YEAR FROM date) AS annee,
    EXTRACT(MONTH FROM date) AS mois,
    EXTRACT(DAY FROM date) AS jour,
    (SUM(consommation) - SUM(pompage) - SUM(ech_physiques)) * 0.25 AS production,
    SUM(consommation) * 0.25 AS consommation,
    SUM(thermique) * 0.25 AS thermique,
    SUM(nucleaire) * 0.25 AS nucleaire,
    SUM(eolien) * 0.25 AS eolien,
    SUM(solaire) * 0.25 AS solaire,
    SUM(hydraulique) * 0.25 AS hydraulique,
    SUM(pompage) * 0.25 AS pompage,
    SUM(bioenergies) * 0.25 AS bioenergies,
    SUM(ech_physiques) * 0.25 AS ech_physiques,
    SUM(tco_thermique * thermique) / NULLIF(SUM(thermique), 0) AS tco_thermique,
    SUM(tch_thermique * consommation) / NULLIF(SUM(consommation), 0) AS tch_thermique,
    SUM(tco_nucleaire * nucleaire) / NULLIF(SUM(nucleaire), 0) AS tco_nucleaire,
    SUM(tch_nucleaire * consommation) / NULLIF(SUM(consommation), 0) AS tch_nucleaire,
    SUM(tco_eolien * eolien) / NULLIF(SUM(eolien), 0) AS tco_eolien,
    SUM(tch_eolien * consommation) / NULLIF(SUM(consommation), 0) AS tch_eolien,
    SUM(tco_solaire * solaire) / NULLIF(SUM(solaire), 0) AS tco_solaire,
    SUM(tch_solaire * consommation) / NULLIF(SUM(consommation), 0) AS tch_solaire,
    SUM(tco_hydraulique * hydraulique) / NULLIF(SUM(hydraulique), 0) AS tco_hydraulique,
    SUM(tch_hydraulique * consommation) / NULLIF(SUM(consommation), 0) AS tch_hydraulique,
    SUM(tco_bioenergies * bioenergies) / NULLIF(SUM(bioenergies), 0) AS tco_bioenergies,
    SUM(tch_bioenergies * consommation) / NULLIF(SUM(consommation), 0) AS tch_bioenergies
FROM valid_rows
GROUP BY code_insee_region, libelle_region, nature, date, annee, mois, jour
ORDER BY date, libelle_region ASC
