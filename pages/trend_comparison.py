import sys
from pathlib import Path

# Add utils to path for shared utilities
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.path_utils import get_housets_csv_path

import streamlit as st
import pandas as pd
import warnings
import plotly.express as px
import plotly.graph_objects as go

# Suppress FutureWarning from plotly.express about observed parameter in groupby
warnings.filterwarnings("ignore", category=FutureWarning, module="plotly.express")

# Hide navigation bar on design pages
st.markdown("""
<style>
/* Hide navigation bar on design pages */
header[data-testid="stHeader"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Return home button at the top
col_back, col_spacer = st.columns([2, 20])
with col_back:
    if st.button("🏠 Return Home", use_container_width=True, help="Return to home page", type="secondary"):
        st.switch_page("pages/intro.py")

st.title("📊 Time Series Comparison")
st.markdown(
    """
    <p style="color: #6b7280; font-size: 0.875rem; margin-top: -1rem; margin-bottom: 1rem;">
        Compare <span class="pti-tooltip">Price-to-Income Ratio<span class="tooltiptext"><strong>PTI = Median Sale Price ÷ Median Household Income</strong></span></span> across multiple metropolitan areas over time
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    [data-testid="stVirtualDropdown"] > div {
        height: auto !important;
    }
    
    /* Left panel / multiselect sizing + align pills to top */
    div[data-testid="stMultiSelect"] {
        height: 471px !important;
        display: flex !important;
        flex-direction: column !important;
    }
    div[data-testid="stMultiSelect"] > div:nth-child(2) {
        flex: 1 1 auto !important;
        height: 100% !important;
    }
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
        height: 100% !important;
        min-height: 100% !important;
        display: flex !important;
        align-items: flex-start !important;
    }
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        height: 100% !important;
        min-height: 100% !important;
        display: flex !important;
        align-items: flex-start !important;
    }
    
    /* PTI Tooltip Styles */
    .pti-tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #4B0082;
        cursor: help;
        color: #4B0082;
        font-weight: 700;
    }
    .pti-tooltip .tooltiptext {
        visibility: hidden;
        width: 280px;
        background-color: #333;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 8px 12px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -140px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.85rem;
        font-weight: normal;
        line-height: 1.4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .pti-tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #333 transparent transparent transparent;
    }
    .pti-tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data(show_spinner="Loading required data...", ttl=3600, max_entries=1)
def load_data():
    csv_path = get_housets_csv_path()

    if not csv_path.exists():
        st.error(f"Data file not found: {csv_path}")
        st.info("Ensure data/housets_zip_level.csv is present in the repository.")
        return pd.DataFrame(), []

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), []
    
    # Normalize column names - handle both formats
    # Check for different possible column name formats
    price_col = None
    income_col = None
    
    # Try to find median_sale_price column (case-insensitive)
    for col in df.columns:
        col_lower = col.lower().replace(" ", "_").replace("-", "_")
        if "median" in col_lower and "sale" in col_lower and "price" in col_lower:
            price_col = col
        elif ("per_capita" in col_lower or "capita" in col_lower) and "income" in col_lower:
            income_col = col
    
    # If not found, try exact matches
    if price_col is None:
        if "median_sale_price" in df.columns:
            price_col = "median_sale_price"
        elif "Median Sale Price" in df.columns:
            price_col = "Median Sale Price"
    
    if income_col is None:
        if "Per Capita Income" in df.columns:
            income_col = "Per Capita Income"
        elif "per_capita_income" in df.columns:
            income_col = "per_capita_income"
    
    if price_col is None or income_col is None:
        st.error(f"Could not find required columns. Available columns: {list(df.columns)}")
        st.info("Expected columns: 'median_sale_price' (or 'Median Sale Price') and 'Per Capita Income' (or 'per_capita_income')")
        return pd.DataFrame(), []
    
    # Check for city_full column
    city_col = None
    if "city_full" in df.columns:
        city_col = "city_full"
    elif "city" in df.columns:
        # If only city column exists, we might need to use it
        city_col = "city"
        st.warning("Using 'city' column instead of 'city_full'. Some city names might be abbreviated.")
    
    if city_col is None:
        st.error(f"Could not find city column. Available columns: {list(df.columns)}")
        return pd.DataFrame(), []
    
    # Filter out rows with invalid data
    df = df[(df[price_col] > 0) & (df[income_col] > 0)].copy()
    df = df.fillna(0)

    # Price to Income Data Preparation
    df["Price_Income_Ratio"] = df[price_col] / (2.54 * df[income_col])
    
    # Group by city and year, then aggregate
    ratio_agg = (
        df.groupby([city_col, "year"], as_index=False, observed=True)
        .agg({
            "Price_Income_Ratio": "median",
            price_col: "median",
            income_col: "median"
        })
    )
    
    # Rename columns for consistency
    ratio_agg = ratio_agg.rename(columns={
        city_col: "city_full",
        price_col: "median_sale_price",
        income_col: "Per Capita Income"
    })

    ratio_agg["Affordability"] = ""

    ratio_agg.loc[ratio_agg["Price_Income_Ratio"] <= 3.0,
                "Affordability"] = "Affordable"

    ratio_agg.loc[(ratio_agg["Price_Income_Ratio"] > 3.0) &
                (ratio_agg["Price_Income_Ratio"] <= 4.0),
                "Affordability"] = "Moderately Unaffordable"

    ratio_agg.loc[(ratio_agg["Price_Income_Ratio"] > 4.0) &
                (ratio_agg["Price_Income_Ratio"] <= 5.0),
                "Affordability"] = "Seriously Unaffordable"

    ratio_agg.loc[(ratio_agg["Price_Income_Ratio"] > 5.0) &
                (ratio_agg["Price_Income_Ratio"] < 9.0),
                "Affordability"] = "Severely Unaffordable"

    ratio_agg.loc[ratio_agg["Price_Income_Ratio"] >= 9.0,
                "Affordability"] = "Impossibly Unaffordable"

    city_order = sorted(df["city_full"].unique())
    
    return ratio_agg, city_order

data = load_data()
ratio_agg = data[0]
city_order = data[1]

# Check if data loaded successfully
if ratio_agg.empty or len(city_order) == 0:
    st.error("⚠️ **No Data Available**")
    st.info("""
    Please check that:
    - The data file `housets_zip_level.csv` exists in the `trend_comparison` directory
    - The file is properly formatted and not corrupted
    - The file contains valid data for the selected time period
    """)
    st.stop()

with st.expander("How to Use This Tool", expanded=True, icon="💡"):
    st.markdown("""
                - 🎯 Pick any metropolitan area from the list above — the chart updates instantly.
                - 📊 Compare how affordable house prices are across metropolitan area and over time.
                - 🔍 Hover over any point to see detailed numbers for that year.

                Enjoy exploring! 🚀
                """)

default_cities = [
    "Los Angeles-Long Beach-Anaheim",
    "San Diego-Chula Vista-Carlsbad",
    "San Francisco-Oakland-Berkeley",
    "Seattle-Tacoma-Bellevue",
    "Austin-Round Rock-Georgetown",
    "Pittsburgh"
]

if "selected_cities" not in st.session_state:
    st.session_state.selected_cities = [c for c in default_cities if c in city_order]

def reset_cities():
    st.session_state.selected_cities = [c for c in default_cities if c in city_order]

col1, col2 = st.columns([1.3, 5], vertical_alignment="top")
with col1:
    with st.container(border=True):
        st.markdown(
            "<h2 style='font-size: 24px; margin-bottom: 0.75rem;'>Select Metropolitan Area</h2>",
            unsafe_allow_html=True,
        )
        st.button("Reset to Default", on_click=reset_cities)
        selected_cities = st.multiselect(
            "Metro Areas",
            options=city_order,
            key="selected_cities",
        )

    

if len(selected_cities) == 0:
        with col2:
            st.warning("⚠️ **No Metro Areas Selected**")
            st.info("Please select at least one metropolitan area from the list on the left to view the comparison chart.")
else:
        # ===================================
        # Price to Income Ratio Visualization
        # ===================================

        price_income = ratio_agg[ratio_agg["city_full"].isin(selected_cities)].copy()

        customdata = price_income[
            ["Per Capita Income", "median_sale_price", "Affordability"]
        ].values

        # 1) Build metro line traces with Plotly Express
        colors = px.colors.qualitative.Plotly
        color_map = {
            city: colors[i % len(colors)] for i, city in enumerate(selected_cities)
        }

        px_fig = px.line(
            price_income,
            x="year",
            y="Price_Income_Ratio",
            color="city_full",
            color_discrete_map=color_map,
            markers=True,
        )

        # attach customdata to metro traces
        for i, trace in enumerate(px_fig.data):
            city_name = trace.name
            mask = price_income["city_full"] == city_name
            trace.customdata = customdata[mask.values]

        # 2) New Figure with affordability legend + bands + metro lines
        price_income_fig = go.Figure()

        # 2a) Affordability legend entries (dummy traces – legend only)
        affordability_legend = [
            ("0.0–3.0: Affordable", "rgba(76, 175, 80, 0.30)"),
            ("3.1–4.0: Moderately Unaffordable", "rgba(255, 193, 7, 0.30)"),
            ("4.1–5.0: Seriously Unaffordable", "rgba(255, 152, 0, 0.30)"),
            ("5.1–8.9: Severely Unaffordable", "rgba(229, 115, 115, 0.30)"),
            ("9.0+: Impossibly Unaffordable", "rgba(183, 28, 28, 0.30)"),
        ]

        for i, (label, color) in enumerate(affordability_legend):
            price_income_fig.add_scatter(
                x=[None],
                y=[None],  # nothing drawn
                mode="lines",
                line=dict(width=10, color=color),
                name=label,
                showlegend=True,
                legendgroup="bands",
                legendgrouptitle=dict(text="Affordability Scale (PTI Ranges)")
                if i == 0
                else None,
            )

        # 2b) Background color bands (no text overlays)
        bands = [
            (0.0, 3.0, "rgba(76, 175, 80, 0.30)"),
            (3.0, 4.0, "rgba(255, 193, 7, 0.30)"),
            (4.0, 5.0, "rgba(255, 152, 0, 0.30)"),
            (5.0, 9.0, "rgba(229, 115, 115, 0.30)"),
        ]
        ymax = max(price_income["Price_Income_Ratio"].max() + 1, 9.0)
        bands.append((9.0, ymax, "rgba(183, 28, 28, 0.30)"))

        for y0, y1, fill in bands:
            price_income_fig.add_hrect(
                y0=y0,
                y1=y1,
                line_width=0,
                fillcolor=fill,
                layer="below",
            )
            price_income_fig.add_hline(
                y=y1,
                line_width=1,
                line_dash="dash",
                line_color="silver",
            )

        # 2c) Add the metro lines as a separate legend group
        for i, trace in enumerate(px_fig.data):
            trace.legendgroup = "metros"
            if i == 0:
                trace.legendgrouptitle = dict(text="Metro Areas")
            price_income_fig.add_trace(trace)

        # 3) Hover + layout
        price_income_fig.update_traces(
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "%{customdata[2]}<br>"
                "Year: %{x}<br>"
                "Ratio: %{y:.2f}<br>"
                "Median Income: $%{customdata[0]:,.0f}<br>"
                "Median Sale Price: $%{customdata[1]:,.0f}<extra></extra>"
            ),
            selector=dict(mode="lines+markers"),  # only metro lines
        )

        price_income_fig.update_layout(
            title={
                "text": "Price-to-Income (PTI):<br>U.S. Metropolitan Areas from 2012 to 2023",
                "font": {"size": 28},
            },
            yaxis_title="Price-to-Income(PTI) Ratio",
            xaxis_title="Year",
            hovermode="closest",
            template="plotly_white",
            legend=dict(
                title="",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                traceorder="grouped",  # Affordability Scale group first, then Metro Areas
            ),
            height=600,
            margin=dict(l=20, r=260, t=120, b=40),
            font=dict(size=14),
        )

        # ====================================
        # Dashboard Display
        # ====================================

        with col2:
            with st.container(border=True):
                st.plotly_chart(price_income_fig, width='stretch')
                st.caption("Affordability levels based on Price-to-Income Ratio thresholds from: Cox, Wendell (2025). *Demographia International Housing Affordability, 2025 Edition*. Center for Demographics and Policy.")

