"""
Page 5: Observatoire environnemental par ville.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from dashboard.dashboard_share import (
    BASE_LAYOUT,
    apply_global_style,
    apply_widget_text_style,
    clear_realtime_cache,
    configure_page,
    get_city_options,
    get_environment_context,
    render_sidebar,
    styled_axis,
)

WEATHER_METRICS = {
    "temperature_2m": "Temperature 2m (degC)",
    "relative_humidity_2m": "Humidite relative (%)",
    "precipitation": "Precipitations (mm)",
    "cloud_cover": "Couverture nuageuse (%)",
    "pressure_msl": "Pression MSL (hPa)",
    "wind_speed_10m": "Vent 10m (km/h)",
    "wind_gusts_10m": "Rafales 10m (km/h)",
    "soil_temperature_0cm": "Temp. sol 0cm (degC)",
}

AIR_QUALITY_METRICS = {
    "max_quality_code": "Indice global (max)",
    "avg_quality_code": "Indice global (moy)",
    "max_no2_code": "NO2 (max)",
    "avg_no2_code": "NO2 (moy)",
    "max_o3_code": "O3 (max)",
    "avg_o3_code": "O3 (moy)",
    "max_pm10_code": "PM10 (max)",
    "avg_pm10_code": "PM10 (moy)",
    "max_pm25_code": "PM2.5 (max)",
    "avg_pm25_code": "PM2.5 (moy)",
    "max_so2_code": "SO2 (max)",
    "avg_so2_code": "SO2 (moy)",
}

DEFAULT_WEATHER_METRICS = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
]
DEFAULT_AIR_QUALITY_METRICS = ["max_quality_code", "max_pm25_code", "max_o3_code"]
ALL_ZONES_LABEL = "Toutes les zones"


def _resolve_datetime_column(frame: pd.DataFrame, *candidates: str) -> str | None:
    for column in candidates:
        if column in frame.columns and frame[column].notna().any():
            return column
    return None


def _display_city_name(city_name: str) -> str:
    return city_name.replace("_", " ").title()


def _resolve_date_bounds(
    meteo_frame: pd.DataFrame,
    air_quality_daily_frame: pd.DataFrame,
    air_quality_detail_frame: pd.DataFrame,
) -> tuple[date, date]:
    lower_bounds: list[date] = []
    upper_bounds: list[date] = []

    meteo_column = _resolve_datetime_column(meteo_frame, "time", "last_observation_at", "date")
    if meteo_column:
        lower_bounds.append(meteo_frame[meteo_column].min().date())
        upper_bounds.append(meteo_frame[meteo_column].max().date())

    air_daily_column = _resolve_datetime_column(
        air_quality_daily_frame,
        "date",
        "last_update_at",
        "date_maj",
    )
    if air_daily_column:
        lower_bounds.append(air_quality_daily_frame[air_daily_column].min().date())
        upper_bounds.append(air_quality_daily_frame[air_daily_column].max().date())

    air_detail_column = _resolve_datetime_column(
        air_quality_detail_frame,
        "date_dif",
        "date_maj",
    )
    if air_detail_column:
        lower_bounds.append(air_quality_detail_frame[air_detail_column].min().date())
        upper_bounds.append(air_quality_detail_frame[air_detail_column].max().date())

    if not lower_bounds or not upper_bounds:
        today = date.today()
        return today, today

    return min(lower_bounds), max(upper_bounds)


def _filter_frame_by_window(
    frame: pd.DataFrame,
    *,
    datetime_column: str,
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    if frame.empty or datetime_column not in frame.columns:
        return frame.iloc[0:0].copy()

    filtered = frame.copy()
    filtered = filtered.dropna(subset=[datetime_column])
    if filtered.empty:
        return filtered

    mask = filtered[datetime_column].dt.date.between(start_date, end_date)
    return filtered.loc[mask].sort_values(datetime_column)


def _prepare_air_quality_daily(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame

    prepared = frame.copy()
    if "date" in prepared.columns:
        sort_columns = [
            column
            for column in ["date", "max_quality_code", "last_update_at"]
            if column in prepared.columns
        ]
        if not sort_columns:
            return prepared.reset_index(drop=True)

        return prepared.sort_values(sort_columns).reset_index(drop=True)

    if "date_dif" not in prepared.columns or prepared["date_dif"].isna().all():
        prepared["date_dif"] = prepared["date_maj"].dt.floor("D")

    sort_columns = [column for column in ["date_dif", "code_qual", "date_maj"] if column in prepared.columns]
    if not sort_columns:
        return prepared

    prepared = prepared.sort_values(sort_columns)
    return (
        prepared.groupby("date_dif", group_keys=False)
        .tail(1)
        .sort_values("date_dif")
        .reset_index(drop=True)
    )


def _format_metric_value(value: object, *, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.1f}{suffix}"
    return f"{value}{suffix}"


def _max_air_quality_level(frame: pd.DataFrame, metrics: list[str]) -> int:
    if frame.empty or not metrics:
        return 6

    numeric_max = pd.to_numeric(frame[metrics].stack(), errors="coerce").max()
    if pd.isna(numeric_max):
        return 6
    return max(6, int(numeric_max))


def _resolve_air_quality_label(latest_row: pd.Series | None) -> str:
    if latest_row is None:
        return "N/A"

    for label_column in ("worst_quality_label", "lib_qual"):
        label = latest_row.get(label_column)
        if label is not None and not pd.isna(label) and str(label).strip():
            return str(label)

    for code_column in ("max_quality_code", "code_qual", "avg_quality_code"):
        code_value = latest_row.get(code_column)
        if code_value is not None and not pd.isna(code_value):
            return _format_metric_value(code_value)

    return "N/A"


def _format_timestamp(value: object) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)


def _zone_label(row: pd.Series) -> str:
    zone_name = row.get("lib_zone")
    zone_code = row.get("code_zone")

    zone_name_text = "" if zone_name is None or pd.isna(zone_name) else str(zone_name).strip()
    zone_code_text = "" if zone_code is None or pd.isna(zone_code) else str(zone_code).strip()

    if zone_name_text and zone_code_text:
        return f"{zone_name_text} [{zone_code_text}]"
    if zone_name_text:
        return zone_name_text
    if zone_code_text:
        return zone_code_text
    return "Zone inconnue"


def _get_zone_options(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return [ALL_ZONES_LABEL]

    zone_columns = [column for column in ("lib_zone", "code_zone") if column in frame.columns]
    if not zone_columns:
        return [ALL_ZONES_LABEL]

    deduped = frame[zone_columns].drop_duplicates().copy()
    deduped["zone_option"] = deduped.apply(_zone_label, axis=1)
    options = sorted(option for option in deduped["zone_option"].tolist() if option)
    return [ALL_ZONES_LABEL, *options]


def _apply_zone_filter(frame: pd.DataFrame, zone_option: str) -> pd.DataFrame:
    if frame.empty or zone_option == ALL_ZONES_LABEL:
        return frame

    filtered = frame.copy()
    if "lib_zone" in filtered.columns:
        lib_zone = filtered["lib_zone"].fillna("").astype(str).str.strip()
    else:
        lib_zone = pd.Series("", index=filtered.index)

    if "code_zone" in filtered.columns:
        code_zone = filtered["code_zone"].fillna("").astype(str).str.strip()
    else:
        code_zone = pd.Series("", index=filtered.index)

    combined = pd.Series(
        [
            f"{name} [{code}]" if name and code else name or code or "Zone inconnue"
            for name, code in zip(lib_zone, code_zone, strict=False)
        ],
        index=filtered.index,
    )
    return filtered.loc[combined == zone_option].copy()


def _build_weather_figure(frame: pd.DataFrame, metrics: list[str]) -> go.Figure | None:
    available_metrics = [metric for metric in metrics if metric in frame.columns]
    if frame.empty or not available_metrics:
        return None

    fig = make_subplots(
        rows=len(available_metrics),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        subplot_titles=[WEATHER_METRICS.get(metric, metric) for metric in available_metrics],
    )

    palette = ["#00dcff", "#7ef29a", "#ffd166", "#ff8c69", "#c084fc", "#82b1ff"]

    for index, metric in enumerate(available_metrics, start=1):
        metric_frame = frame[["time", metric]].dropna().sort_values("time")
        if metric_frame.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=metric_frame["time"],
                y=metric_frame[metric],
                mode="lines",
                name=WEATHER_METRICS.get(metric, metric),
                line={"width": 2.4, "color": palette[(index - 1) % len(palette)]},
                hovertemplate=(
                    f"<b>{WEATHER_METRICS.get(metric, metric)}</b><br>"
                    "Date: %{x|%Y-%m-%d %H:%M}<br>"
                    "Valeur: %{y:.2f}<extra></extra>"
                ),
                showlegend=False,
            ),
            row=index,
            col=1,
        )
        fig.update_yaxes(
            **styled_axis(WEATHER_METRICS.get(metric, metric)),
            row=index,
            col=1,
        )

    fig.update_xaxes(
        **styled_axis("Temps"),
        tickformat="%d/%m %Hh",
        row=len(available_metrics),
        col=1,
    )
    fig.update_annotations(font={"size": 16, "color": "#ffffff"})
    fig.update_layout(
        paper_bgcolor=BASE_LAYOUT.get("paper_bgcolor"),
        plot_bgcolor=BASE_LAYOUT.get("plot_bgcolor"),
        font=BASE_LAYOUT.get("font"),
        margin={"l": 80, "r": 40, "t": 80, "b": 70},
        height=260 * len(available_metrics) + 110,
        hovermode="x unified",
        title={
            "text": "Evolution meteo horaire sur la fenetre selectionnee",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 26, "color": "#ffffff"},
        },
    )
    return fig


def _build_air_quality_heatmap(frame: pd.DataFrame, metrics: list[str]) -> go.Figure | None:
    available_metrics = [metric for metric in metrics if metric in frame.columns]
    if frame.empty or not available_metrics:
        return None

    date_column = _resolve_datetime_column(frame, "date", "date_dif", "date_maj")
    if date_column is None:
        return None

    x_values = frame[date_column]
    z_values = [frame[metric].fillna(0).tolist() for metric in available_metrics]

    fig = go.Figure(
        data=go.Heatmap(
            x=x_values,
            y=[AIR_QUALITY_METRICS.get(metric, metric) for metric in available_metrics],
            z=z_values,
            zmin=0,
            zmax=_max_air_quality_level(frame, available_metrics),
            colorscale=[
                [0.0, "#12304c"],
                [0.16, "#2dd4bf"],
                [0.33, "#84cc16"],
                [0.5, "#facc15"],
                [0.66, "#fb923c"],
                [0.83, "#ef4444"],
                [1.0, "#7f1d1d"],
            ],
            colorbar={"title": "Niveau"},
            hovertemplate="Jour: %{x|%Y-%m-%d}<br>Indicateur: %{y}<br>Niveau: %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        paper_bgcolor=BASE_LAYOUT.get("paper_bgcolor"),
        plot_bgcolor=BASE_LAYOUT.get("plot_bgcolor"),
        font=BASE_LAYOUT.get("font"),
        margin={"l": 80, "r": 40, "t": 80, "b": 70},
        height=460,
        title={
            "text": "Synthese quotidienne de la qualite de l'air",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 26, "color": "#ffffff"},
        },
    )
    fig.update_xaxes(**styled_axis("Jour"), tickformat="%d/%m")
    fig.update_yaxes(**styled_axis("Indicateurs"))
    return fig


def _build_air_quality_map(frame: pd.DataFrame) -> go.Figure | None:
    required_columns = {"x_wgs84", "y_wgs84"}
    if frame.empty or not required_columns.issubset(frame.columns):
        return None

    map_frame = frame.copy()
    map_frame["x_wgs84"] = pd.to_numeric(map_frame["x_wgs84"], errors="coerce")
    map_frame["y_wgs84"] = pd.to_numeric(map_frame["y_wgs84"], errors="coerce")
    map_frame = map_frame.dropna(subset=["x_wgs84", "y_wgs84"])
    if map_frame.empty:
        return None

    sort_columns = [column for column in ("lib_zone", "date_maj") if column in map_frame.columns]
    if sort_columns:
        map_frame = map_frame.sort_values(sort_columns)

    group_columns = [column for column in ("lib_zone", "code_zone") if column in map_frame.columns]
    if group_columns:
        map_frame = map_frame.groupby(group_columns, group_keys=False).tail(1).copy()

    map_frame["zone_display"] = map_frame.apply(_zone_label, axis=1)
    if "lib_qual" not in map_frame.columns:
        map_frame["lib_qual"] = "N/A"
    if "type_zone" not in map_frame.columns:
        map_frame["type_zone"] = "N/A"

    fig = px.scatter_mapbox(
        map_frame,
        lat="y_wgs84",
        lon="x_wgs84",
        color="code_qual" if "code_qual" in map_frame.columns else None,
        size="code_qual" if "code_qual" in map_frame.columns else None,
        size_max=20,
        hover_name="zone_display",
        hover_data={
            "lib_qual": True,
            "type_zone": True,
            "date_maj": True,
            "x_wgs84": False,
            "y_wgs84": False,
        },
        color_continuous_scale=[
            [0.0, "#2dd4bf"],
            [0.2, "#84cc16"],
            [0.4, "#facc15"],
            [0.6, "#fb923c"],
            [0.8, "#ef4444"],
            [1.0, "#7f1d1d"],
        ],
        zoom=9,
        center={
            "lat": map_frame["y_wgs84"].mean(),
            "lon": map_frame["x_wgs84"].mean(),
        },
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        paper_bgcolor=BASE_LAYOUT.get("paper_bgcolor"),
        plot_bgcolor=BASE_LAYOUT.get("plot_bgcolor"),
        font=BASE_LAYOUT.get("font"),
        margin={"l": 0, "r": 0, "t": 60, "b": 0},
        height=520,
        title={
            "text": "Carte des zones ATMO visibles sur la fenetre selectionnee",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 24, "color": "#ffffff"},
        },
        coloraxis_colorbar={"title": "Indice"},
    )
    return fig


configure_page()
apply_global_style()
render_sidebar()

city_options = get_city_options()
default_city = "paris" if "paris" in city_options else city_options[0]

with st.sidebar:
    st.markdown(
        '<div class="sidebar-section">🌤️ Filtres environnement</div>',
        unsafe_allow_html=True,
    )
    selected_city = st.selectbox(
        "Ville analysee:",
        options=city_options,
        index=city_options.index(default_city),
        format_func=_display_city_name,
        key="environment_city_choice",
    )

context = get_environment_context(selected_city)
df_meteo = context.get("df_meteo_by_city", pd.DataFrame())
df_air_quality_detail = context.get(
    "df_air_quality_by_city_detail",
    context.get("df_air_quality_by_city", pd.DataFrame()),
)
df_air_quality_daily_source = context.get("df_air_quality_by_city_daily", pd.DataFrame())

min_date, max_date = _resolve_date_bounds(
    df_meteo,
    df_air_quality_daily_source,
    df_air_quality_detail,
)
default_start_date = max(min_date, max_date - pd.Timedelta(days=13).to_pytimedelta())
apply_widget_text_style(color="#000000", font_size="0.95rem")

available_weather_metrics = [metric for metric in WEATHER_METRICS if metric in df_meteo.columns]
available_air_metrics = [
    metric for metric in AIR_QUALITY_METRICS if metric in df_air_quality_daily_source.columns
]
zone_options = _get_zone_options(df_air_quality_detail)

with st.sidebar:
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input(
            "Date debut",
            value=default_start_date,
            min_value=min_date,
            max_value=max_date,
            key="environment_start_date",
        )
    with date_col2:
        end_date = st.date_input(
            "Date fin",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="environment_end_date",
        )

    weather_metrics = st.multiselect(
        "Indicateurs meteo:",
        options=available_weather_metrics,
        default=[metric for metric in DEFAULT_WEATHER_METRICS if metric in available_weather_metrics],
        format_func=lambda metric: WEATHER_METRICS.get(metric, metric),
        key="environment_weather_metrics",
    )
    air_quality_metrics = st.multiselect(
        "Indicateurs qualite de l'air:",
        options=available_air_metrics,
        default=[metric for metric in DEFAULT_AIR_QUALITY_METRICS if metric in available_air_metrics],
        format_func=lambda metric: AIR_QUALITY_METRICS.get(metric, metric),
        key="environment_air_metrics",
    )
    selected_zone = st.selectbox(
        "Zone ATMO detaillee (carte):",
        options=zone_options,
        index=0,
        key="environment_zone_choice",
    )

    if st.button("Rafraichir les donnees", use_container_width=True):
        clear_realtime_cache()
        st.rerun()

if start_date > end_date:
    st.error("La date de debut doit etre anterieure ou egale a la date de fin.")
    st.stop()

st.title(
    f"Observatoire environnemental de {_display_city_name(selected_city)}",
    text_alignment="center",
    width="stretch",
)

st.markdown(
    """
<div class="chart-card">
  <div class="chart-title">🌍 Vue hybride météo silver + synthèse air gold</div>
  <div class="chart-desc">
    Cette page combine la météo horaire détaillée issue de meteo_by_city en silver,
    une synthèse quotidienne de la qualité de l'air issue de air_quality_by_city en gold,
    et une carte ATMO détaillée qui reste alimentée par la couche silver.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

air_quality_detail_date_column = _resolve_datetime_column(
    df_air_quality_detail,
    "date_dif",
    "date_maj",
)
air_quality_daily_date_column = _resolve_datetime_column(
    df_air_quality_daily_source,
    "date",
    "last_update_at",
)

filtered_meteo = _filter_frame_by_window(
    df_meteo,
    datetime_column="time",
    start_date=start_date,
    end_date=end_date,
)
filtered_air_quality_detail = _filter_frame_by_window(
    df_air_quality_detail,
    datetime_column=air_quality_detail_date_column,
    start_date=start_date,
    end_date=end_date,
)
filtered_air_quality_detail = _apply_zone_filter(filtered_air_quality_detail, selected_zone)
filtered_air_quality_daily = _filter_frame_by_window(
    df_air_quality_daily_source,
    datetime_column=air_quality_daily_date_column,
    start_date=start_date,
    end_date=end_date,
)
daily_air_quality = _prepare_air_quality_daily(filtered_air_quality_daily)

latest_weather = (
    filtered_meteo.sort_values("time").iloc[-1] if not filtered_meteo.empty else None
)
latest_air_quality = (
    daily_air_quality.sort_values(
        _resolve_datetime_column(daily_air_quality, "date", "last_update_at", "date_maj") or "date"
    ).iloc[-1]
    if not daily_air_quality.empty
    else None
)

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric(
        "Derniere temperature",
        _format_metric_value(
            latest_weather.get("temperature_2m") if latest_weather is not None else None,
            suffix=" °C",
        ),
    )
with kpi_col2:
    st.metric(
        "Humidite actuelle",
        _format_metric_value(
            latest_weather.get("relative_humidity_2m") if latest_weather is not None else None,
            suffix=" %",
        ),
    )
with kpi_col3:
    st.metric(
        "Vent 10m",
        _format_metric_value(
            latest_weather.get("wind_speed_10m") if latest_weather is not None else None,
            suffix=" km/h",
        ),
    )
with kpi_col4:
    st.metric("Qualite de l'air", _resolve_air_quality_label(latest_air_quality))

tab_weather, tab_air, tab_map, tab_data = st.tabs(
    ["Meteo", "Qualite de l'air", "Carte ATMO", "Donnees"]
)

with tab_weather:
    st.markdown(
        """
<div class="chart-card">
  <div class="chart-title">🌦️ Tendances météo</div>
  <div class="chart-desc">
    Les indicateurs sélectionnés sont tracés sur des panneaux séparés pour conserver leurs unités et éviter les axes trompeurs.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    weather_figure = _build_weather_figure(filtered_meteo, weather_metrics)
    if weather_figure is None:
        st.info("Aucune donnée météo disponible sur cette fenêtre pour les indicateurs sélectionnés.")
    else:
        st.plotly_chart(
            weather_figure,
            use_container_width=True,
            config={"displayModeBar": False},
        )

with tab_air:
    st.markdown(
        """
<div class="chart-card">
  <div class="chart-title">🌫️ Synthèse qualité de l'air</div>
  <div class="chart-desc">
      La heatmap affiche la synthèse quotidienne à l'échelle de la ville issue de la couche gold.
      Le sélecteur de zone ATMO reste réservé à la carte détaillée plus bas.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    air_quality_figure = _build_air_quality_heatmap(daily_air_quality, air_quality_metrics)
    if air_quality_figure is None:
        st.info("Aucune donnée qualité de l'air disponible sur cette fenêtre pour les indicateurs sélectionnés.")
    else:
        st.plotly_chart(
            air_quality_figure,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    if latest_air_quality is not None:
        st.markdown(
            f"""
<div class="chart-card">
  <div class="chart-title">Dernière synthèse disponible</div>
  <div class="chart-desc">
                Date: {_format_timestamp(latest_air_quality.get('date'))}<br>
                Dernière mise à jour: {_format_timestamp(latest_air_quality.get('last_update_at'))}<br>
                Zone la plus dégradée: {latest_air_quality.get('worst_quality_zone', 'N/A')}<br>
                Type de zone: {latest_air_quality.get('worst_quality_zone_type', 'N/A')}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

with tab_map:
    st.markdown(
        """
<div class="chart-card">
    <div class="chart-title">🗺️ Localisation des zones ATMO</div>
    <div class="chart-desc">
        La carte montre la dernière mesure disponible par zone sur la fenêtre sélectionnée, avec une couleur plus chaude quand l'indice est plus élevé.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    air_quality_map = _build_air_quality_map(filtered_air_quality_detail)
    if air_quality_map is None:
        st.info("Aucune coordonnée exploitable n'est disponible pour afficher la carte ATMO sur cette sélection.")
    else:
        st.plotly_chart(
            air_quality_map,
            use_container_width=True,
            config={"displayModeBar": False},
        )

with tab_data:
    st.markdown(
        """
<div class="chart-card">
  <div class="chart-title">📋 Données filtrées</div>
  <div class="chart-desc">
                Extrait des enregistrements chargés pour la ville et la période sélectionnées,
                avec la météo détaillée en silver et la synthèse quotidienne air en gold.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    data_col1, data_col2 = st.columns(2)
    with data_col1:
        st.caption("meteo_by_city (silver horaire)")
        st.dataframe(filtered_meteo.tail(48), use_container_width=True, hide_index=True)
    with data_col2:
        st.caption("air_quality_by_city (gold quotidien)")
        st.dataframe(daily_air_quality.tail(15), use_container_width=True, hide_index=True)