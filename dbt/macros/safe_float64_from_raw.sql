{% macro safe_float64_from_raw(column_name) -%}
case
    when {{ column_name }} is null then null
    when upper(trim(cast({{ column_name }} as string))) in ('', 'NA', 'N/A', 'NULL', '-', 'ND') then null
    else safe_cast(
        replace(
            regexp_replace(trim(cast({{ column_name }} as string)), r'\s+', ''),
            ',',
            '.'
        ) as float64
    )
end
{%- endmacro %}