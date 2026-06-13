# data_utils.py
import numpy as np
import pandas as pd
import streamlit as st

# Demographia categories
AFFORDABILITY_ORDER = [
    "Affordable",
    "Moderately Unaffordable",
    "Seriously Unaffordable",
    "Severely Unaffordable",
    "Impossibly Unaffordable",
]

AFFORDABILITY_COLORS = {
    "Affordable": "#4CAF50",                # green
    "Moderately Unaffordable": "#FFC107",   # amber
    "Seriously Unaffordable": "#FF9800",    # orange
    "Severely Unaffordable": "#E57373",     # light red
    "Impossibly Unaffordable": "#B71C1C",   # dark red
}


def classify_affordability(pti: float):
    """Demographia thresholds based on price-to-income."""
    if pd.isna(pti):
        return None
    if pti <= 3.0:
        return "Affordable"
    elif pti <= 4.0:
        return "Moderately Unaffordable"
    elif pti <= 5.0:
        return "Seriously Unaffordable"
    elif pti <= 8.9:
        return "Severely Unaffordable"
    else:
        return "Impossibly Unaffordable"


@st.cache_data(show_spinner="Loading HouseTS_reduced.csv …")
def load_raw_data(path: str = None) -> pd.DataFrame:
    """Read the raw HouseTS CSV."""
    import os
    from pathlib import Path
    
    # If no path provided, try to find the file relative to the story directory
    if path is None:
        # Try multiple possible locations
        current_file = Path(__file__).resolve()
        story_dir = current_file.parent
        
        # Try relative to story directory first
        data_file = story_dir / "data" / "HouseTS_reduced.csv"
        if data_file.exists():
            path = str(data_file)
        else:
            # Try relative to project root
            project_root = story_dir.parent
            data_file = project_root / "story" / "data" / "HouseTS_reduced.csv"
            if data_file.exists():
                path = str(data_file)
            else:
                # Fallback to original relative path (works when os.chdir is used)
                path = "data/HouseTS_reduced.csv"
    
    # Convert to Path object for better handling
    data_path = Path(path)
    if not data_path.is_absolute():
        # If relative path, resolve relative to story directory
        current_file = Path(__file__).resolve()
        story_dir = current_file.parent
        data_path = (story_dir / path).resolve()
    
    if not data_path.exists():
        raise FileNotFoundError(
            f"Cannot find data file: {data_path}\n"
            f"Please ensure HouseTS_reduced.csv exists in story/data/ directory"
        )
    
    return pd.read_csv(data_path)


def add_derived_columns(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare main working DataFrame.

    Uses original columns:
    - date
    - median_sale_price
    - Median Rent
    - Per Capita Income
    - city_full
    - year
    """
    df = df_raw.copy()

    # time
    df["date"] = pd.to_datetime(df["date"])
    # recompute year from date to be safe
    df["year"] = df["date"].dt.year

    # safe denominators
    income_pc = df["Per Capita Income"].replace(0, np.nan)
    rent = df["Median Rent"].replace(0, np.nan)
    
    AVERAGE_HOUSEHOLD_SIZE = 2.54
    df["median_household_income_est"] = income_pc * AVERAGE_HOUSEHOLD_SIZE

    # core ratios
    df["price_to_income"] = df["median_sale_price"] / df["median_household_income_est"]
    df["rent_to_income"] = (rent * 12.0) / df["median_household_income_est"]
    df["price_to_rent"] = df["median_sale_price"] / (rent * 12.0)

    # affordability category
    df["affordability_rating"] = df["price_to_income"].apply(classify_affordability)

    return df

def composite_series(df: pd.DataFrame) -> pd.DataFrame:
    """
    Composite (simple average across metros) over time.

    Returns columns:
      date, composite_price, composite_income,
      composite_pti, price_index, income_index, year
    """
    grouped = (
        df.groupby("date", as_index=False, observed=True)[
            ["median_sale_price", "median_household_income_est", "price_to_income"]
        ]
        .mean()
        .rename(
            columns={
                "median_sale_price": "composite_price",
                "median_household_income_est": "composite_income",
                "price_to_income": "composite_pti",
            }
        )
    )

    # normalize to first year's values
    first_year = grouped["date"].dt.year.min()
    base = grouped[grouped["date"].dt.year == first_year].iloc[0]
    grouped["price_index"] = (
        grouped["composite_price"] / base["composite_price"] * 100.0
    )
    grouped["income_index"] = (
        grouped["composite_income"] / base["composite_income"] * 100.0
    )

    grouped["year"] = grouped["date"].dt.year
    grouped["affordability_rating"] = grouped["composite_pti"].apply(
        classify_affordability
    )
    return grouped


def yearly_metro_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per (city_full, year) summarizing PTI, rent burden
    """
    summary = (
        df.groupby(["city_full", "year"], as_index=False, observed=True)
        .agg(
            price_to_income=("price_to_income", "mean"),
            rent_to_income=("rent_to_income", "mean"),
        )
    )

    summary["affordability_rating"] = summary["price_to_income"].apply(
        classify_affordability
    )
    return summary


def affordability_counts_by_year(summary: pd.DataFrame) -> pd.DataFrame:
    """Number of metros in each category per year."""
    counts = (
        summary.groupby(["year", "affordability_rating"])
        .size()
        .reset_index(name="n_metros")
    )
    counts["affordability_rating"] = pd.Categorical(
        counts["affordability_rating"],
        categories=AFFORDABILITY_ORDER,
        ordered=True,
    )
    counts = counts.sort_values(["year", "affordability_rating"])
    return counts


def latest_year(summary: pd.DataFrame) -> int:
    """Return the latest year present in the summary."""
    return int(summary["year"].max())
