"""Data loading and aggregation for the affordability finder."""

import logging

import numpy as np
import pandas as pd
import streamlit as st

from utils.path_utils import get_housets_csv_path

RATIO_COL = "price_to_income_ratio"
AFFORDABILITY_THRESHOLD = 3.0
AFFORDABILITY_CATEGORIES = {
    "Affordable": (None, 3.0),
    "Moderately Unaffordable": (3.0, 4.0),
    "Seriously Unaffordable": (4.0, 5.0),
    "Severely Unaffordable": (5.0, 8.9),
    "Impossibly Unaffordable": (8.9, None),
}
AFFORDABILITY_COLORS = {
    "Affordable": "#4CAF50",
    "Moderately Unaffordable": "#FFC107",
    "Seriously Unaffordable": "#FF9800",
    "Severely Unaffordable": "#E57373",
    "Impossibly Unaffordable": "#B71C1C",
}


def classify_affordability(ratio: float) -> str:
    """Classify a price-to-income ratio using Demographia tiers."""
    if pd.isna(ratio):
        return "N/A"

    sorted_categories = sorted(
        AFFORDABILITY_CATEGORIES.items(),
        key=lambda item: item[1][1] if item[1][1] is not None else float("inf"),
    )

    for category, (lower, upper) in sorted_categories:
        if category == "Affordable":
            if ratio <= upper:
                return category
        elif lower is not None and upper is None:
            if ratio > lower:
                return category
        elif lower is not None and upper is not None:
            if lower < ratio <= upper:
                return category

    return "Uncategorized"


@st.cache_data(ttl=3600 * 24)
def load_data() -> pd.DataFrame:
    """Load and standardize the canonical housing dataset."""
    logger = logging.getLogger(__name__)
    data_path = get_housets_csv_path()

    if not data_path.exists():
        logger.error("Missing canonical data file: %s", data_path)
        return pd.DataFrame()

    try:
        df = pd.read_csv(data_path, low_memory=False)
    except Exception as exc:
        logger.error("Error loading %s: %s", data_path, exc)
        return pd.DataFrame()

    if df.empty:
        logger.error("Data file is empty: %s", data_path)
        return pd.DataFrame()

    df.rename(
        columns={
            "Median Sale Price": "median_sale_price",
            "Per Capita Income": "per_capita_income",
            "city": "city_geojson_code",
        },
        inplace=True,
    )

    if "city_full" not in df.columns:
        df["city_full"] = df["city_geojson_code"] + " Metro Area"

    df["city_clean"] = df["city_geojson_code"]
    df["monthly_income_pc"] = df["per_capita_income"] / 12.0
    return df


def apply_income_filter(df: pd.DataFrame, annual_income: float) -> pd.DataFrame:
    """Return the full dataframe for map context."""
    return df.copy()


@st.cache_data(ttl=3600 * 24)
def make_city_view_data(df_full: pd.DataFrame, annual_income: float, year: int, budget_pct: float = 30):
    """Aggregate metro-level affordability for the bar chart."""
    df_year = df_full[df_full["year"] == year].copy()

    city_agg = df_year.groupby("city_geojson_code", observed=True).agg(
        median_sale_price=("median_sale_price", "median"),
        per_capita_income=("per_capita_income", "median"),
        city_full=("city_full", "first"),
    ).reset_index()

    city_agg[RATIO_COL] = city_agg["median_sale_price"] / (city_agg["per_capita_income"] * 2.54)
    city_agg["affordability_rating"] = city_agg[RATIO_COL].apply(classify_affordability)
    city_agg["affordable"] = city_agg[RATIO_COL] <= AFFORDABILITY_THRESHOLD

    city_agg.rename(
        columns={
            "median_sale_price": "Median Sale Price",
            "per_capita_income": "Per Capita Income",
            "city_geojson_code": "city",
        },
        inplace=True,
    )
    return city_agg
