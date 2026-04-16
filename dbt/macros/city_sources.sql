{% macro get_supported_city_names() %}
  {{ return([
    'paris',
    'lyon',
    'lille',
    'dijon',
    'rennes',
    'orleans',
    'strasbourg',
    'caen',
    'bordeaux',
    'toulouse',
    'marseille',
    'nantes'
  ]) }}
{% endmacro %}

{% macro union_city_sources(source_name, table_prefix) %}
  {% set cities = get_supported_city_names() %}

  {% for city in cities %}
    SELECT
      '{{ city }}' AS city_name,
      *
    FROM {{ source(source_name, table_prefix ~ city) }}
    {% if not loop.last %}
      UNION ALL
    {% endif %}
  {% endfor %}
{% endmacro %}