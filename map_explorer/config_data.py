"""Constants, theme CSS, and data loading for the map explorer module."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from utils.path_utils import get_geo_dir, get_metro_aggregates_path

MAP_EXPLORER_DIR = Path(__file__).parent.resolve()

CBSA_SHP_PATH = str(get_geo_dir() / "cb_2018_us_cbsa_500k.shp")
ZCTA_SHP_PATH = str(get_geo_dir() / "cb_2018_us_zcta510_500k.shp")
CBSA_ZIP_PATH = str(get_geo_dir() / "cbsa_shapes.zip")
ZCTA_ZIP_PATH = str(get_geo_dir() / "zcta_shapes.zip")

US_CENTER_LAT = 39.8283
US_CENTER_LON = -98.5795
US_ZOOM_LEVEL = 3.8

US_BOUNDS = {
    "west": -130,
    "east": -65,
    "south": 22,
    "north": 52,
}

MANUAL_CBSA_NAME_MAP = {
    "dc_metro": "Washington-Arlington-Alexandria, DC-VA-MD-WV",
}


def get_dynamic_css(is_dark_mode: bool) -> str:
    """Generate CSS based on current theme (light / dark)."""
    if is_dark_mode:
        return """
        <style>
        #MainMenu {visibility: hidden;}
        .modebar {display: none !important;}
        .metric-card {
            background: #111827;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            border: 1px solid #1f2937;
            margin-bottom: 0.75rem;
        }
        .stButton > button {
            transition: all 0.2s ease;
            border-radius: 8px;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }
        .stSelectbox > div > div {
            border-radius: 8px;
        }
        .js-plotly-plot .xtitle, .js-plotly-plot .ytitle {
            fill: #ffffff !important;
            color: #ffffff !important;
        }
        .js-plotly-plot .xtick text, .js-plotly-plot .ytick text {
            fill: #ffffff !important;
            color: #ffffff !important;
        }
        </style>
        """
    return """
        <style>
        #MainMenu {visibility: hidden;}
        .modebar {display: none !important;}
        .metric-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 2px rgba(15,23,42,0.06);
            margin-bottom: 0.75rem;
        }
        .stButton > button {
            transition: all 0.2s ease;
            border-radius: 8px;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(148,163,184,0.4);
        }
        .stSelectbox > div > div {
            border-radius: 8px;
        }
        </style>
        """


def get_colorscale(metric_type: str, is_dark_mode: bool = False):
    """Return a colorscale for PTI or median sale price."""
    if "PTI" in metric_type:
        return [
            [0.0, "#dcfce7"],
            [0.25, "#22c55e"],
            [0.5, "#f59e0b"],
            [0.75, "#f97316"],
            [1.0, "#991b1b"],
        ]
    return [
        [0.0, "#dcfce7"],
        [0.25, "#4ade80"],
        [0.5, "#fbbf24"],
        [0.75, "#f87171"],
        [1.0, "#dc2626"],
    ]


def _standardize_house_df(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type the metro map aggregate dataset."""
    df = df.copy()
    df["zip_code"] = df["zip_code"].astype("Int64")
    df["zip_code_str"] = (
        df["zip_code"].astype(str)
        .str.replace("<NA>", "", regex=False)
        .str.zfill(5)
    )
    df["city_clean"] = df["city"].astype(str).str.lower().str.strip()
    df["year"] = df["year"].astype(int)
    df["median_sale_price"] = pd.to_numeric(df["median_sale_price"], errors="coerce")
    df["per_capita_income"] = pd.to_numeric(df["per_capita_income"], errors="coerce")
    return df


def _load_all_data_local() -> pd.DataFrame:
    """Load the pre-aggregated metro map CSV."""
    house = pd.read_csv(get_metro_aggregates_path())
    return _standardize_house_df(house)


@st.cache_data(show_spinner="Loading housing data...", ttl=3600, max_entries=1)
def load_all_data() -> pd.DataFrame:
    """Load housing data for the map explorer."""
    return _load_all_data_local()


def compute_pti(df: pd.DataFrame) -> pd.DataFrame:
    """Compute price-to-income ratio for each row."""
    median_household_size = 2.54
    df = df[
        df["median_sale_price"].notna()
        & df["per_capita_income"].notna()
        & (df["median_sale_price"] > 0)
        & (df["per_capita_income"] >= 5000)
    ].copy()
    df["PTI"] = df["median_sale_price"] / (df["per_capita_income"] * median_household_size)
    df.loc[(df["PTI"] < 0.5) | (df["PTI"] > 50), "PTI"] = np.nan
    return df[df["PTI"].notna()].copy()


def compute_rankings(df: pd.DataFrame, value_col: str, id_col: str) -> pd.DataFrame:
    """Add rank and percentile columns."""
    df = df.copy()
    df["rank"] = df[value_col].rank(ascending=False, method="min").astype(int)
    df["rank_total"] = len(df)
    df["percentile"] = ((df["rank_total"] - df["rank"] + 1) / df["rank_total"] * 100).round(1)
    return df


def compute_yoy(
    df_all: pd.DataFrame, current_year: int, group_cols: list, value_col: str
) -> pd.DataFrame:
    """Compute year-over-year change for each group."""
    prev_year = current_year - 1
    df_current = df_all[df_all["year"] == current_year].copy()
    df_prev = df_all[df_all["year"] == prev_year].copy()

    if df_prev.empty:
        df_current["yoy_change"] = np.nan
        df_current["yoy_pct"] = np.nan
        return df_current

    agg_current = df_current.groupby(group_cols, as_index=False, observed=True).agg({value_col: "mean"})
    agg_prev = df_prev.groupby(group_cols, as_index=False, observed=True).agg({value_col: "mean"})

    merged = agg_current.merge(
        agg_prev,
        on=group_cols,
        suffixes=("", "_prev"),
        how="left",
    )
    merged["yoy_change"] = merged[value_col] - merged[f"{value_col}_prev"]
    merged["yoy_pct"] = (merged["yoy_change"] / merged[f"{value_col}_prev"] * 100).round(1)
    return merged


@st.cache_data(ttl=3600, max_entries=10)
def get_metro_yoy(df_all_input: pd.DataFrame, current_year: int, metric_type_input: str) -> pd.DataFrame:
    """Compute metro-level year-over-year changes."""
    df_all_local = df_all_input.copy()
    if metric_type_input == "Price-to-Income Ratio (PTI)":
        df_processed = compute_pti(df_all_local)
        value_col = "PTI"
    else:
        df_processed = df_all_local[df_all_local["median_sale_price"].notna()].copy()
        value_col = "median_sale_price"

    return compute_yoy(df_processed, current_year, ["city", "city_full"], value_col)
