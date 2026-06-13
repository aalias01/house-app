# 🏡 House & Browse — Housing Affordability Dashboard

An interactive data visualization dashboard exploring housing affordability across 30 major U.S. metropolitan areas from 2012–2023. Built with Streamlit, Plotly, and GeoPandas.

## 🌐 Live Demo

[https://houseapp-i2uqriykdh9d6ui38wvwev.streamlit.app](https://houseapp-i2uqriykdh9d6ui38wvwev.streamlit.app)

## 📋 Project Structure

```
house_app/
├── app.py                         # Main entry point and navigation
├── pages/
│   ├── intro.py                   # Home page
│   ├── map_explorer.py            # Interactive Map Explorer
│   ├── trend_comparison.py        # Time Series Comparison
│   ├── affordability_finder.py    # Price Affordability Finder
│   └── story.py                   # Narrative visualization
├── map_explorer/                  # Choropleth map module
│   ├── charts.py
│   ├── config_data.py
│   ├── geo_utils.py
│   ├── events.py
│   └── data/
│       ├── house_ts_agg.csv
│       ├── cbsa_shapes.zip
│       └── zcta_shapes.zip
├── trend_comparison/              # Time series module
│   └── House_reduced.csv
├── affordability_finder/          # Income-based affordability module
│   ├── dataprep.py
│   ├── ui_components.py
│   ├── zip_module.py
│   └── city_geojson/             # GeoJSON files per metro area
├── story/                         # Narrative module
│   ├── charts.py
│   ├── data_utils.py
│   └── data/
│       └── HouseTS_reduced.csv
├── utils/                         # Shared utilities
│   ├── path_utils.py
│   └── error_handling.py
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## 🎯 Features

### 🗺️ Interactive Map Explorer
- Choropleth map of 30 U.S. metro areas with drill-down to ZIP code level
- Metrics: Price-to-Income Ratio (PTI) and median sale price
- ZIP-level historical trend charts and year-over-year comparison
- Ranking system showing where each ZIP sits within its metro

### 📊 Time Series Comparison
- Compare PTI trends across multiple metro areas simultaneously
- Color-coded affordability bands (Affordable → Impossibly Unaffordable)
- Hover tooltips with median income and price data per year

### 💰 Price Affordability Finder
- Income-based affordability: set income via preset persona or custom input
- Metro-level bar chart filtered to your price range
- ZIP-code choropleth map — green for affordable, red for unaffordable
- Adjustable by year (2012–2023)

### 📖 Key Insights (Story)
- Narrative visualization across five chapters
- Covers macro price-vs-income divergence, metro divergence, affordability bands, rent vs. ownership burden, and a 2023 metro snapshot

## 📊 Data

| Source | Description |
|--------|-------------|
| [HouseTS Dataset](https://www.kaggle.com/datasets/shengkunwang/housets-dataset/data) | 30 U.S. metros, 2012–2023, ZIP-level sale prices and incomes |
| U.S. Census Bureau CBSA & ZCTA shapefiles | Metro and ZIP code boundaries for map layers |
| Pre-processed GeoJSON | Per-metro ZIP geometries for the affordability map |

**Price-to-Income Ratio (PTI):**
```
PTI = Median Sale Price / (Per Capita Income × 2.54)
```
The multiplier 2.54 is the median U.S. household size (2019–2023 ACS).

| PTI Range | Affordability Level |
|-----------|---------------------|
| 0.0–3.0 | 🟢 Affordable |
| 3.1–4.0 | 🟡 Moderately Unaffordable |
| 4.1–5.0 | 🟠 Seriously Unaffordable |
| 5.1–8.9 | 🔴 Severely Unaffordable |
| 9.0+ | ⚫ Impossibly Unaffordable |

*Thresholds from: Cox, Wendell (2025). Demographia International Housing Affordability, 2025 Edition.*

## 🛠️ Tech Stack

| Library | Use |
|---------|-----|
| Streamlit | Web app framework and multi-page navigation |
| Plotly | Interactive charts and choropleth maps |
| GeoPandas | Geospatial joins and shapefile processing |
| Pandas / NumPy | Data wrangling and aggregation |
| Shapely / PyArrow | Geometry operations and efficient I/O |

## 🔧 Troubleshooting

**Map Explorer won't load:**
- Confirm `map_explorer/data/house_ts_agg.csv`, `cbsa_shapes.zip`, and `zcta_shapes.zip` exist
- GeoPandas and Shapely must be installed

**Trend Comparison shows no data:**
- Confirm `trend_comparison/House_reduced.csv` exists and is not a Git LFS pointer

**Affordability Finder shows no data:**
- Confirm `trend_comparison/House_reduced.csv` is present (shared data source)
- Confirm GeoJSON files exist in `affordability_finder/city_geojson/`

**Slow initial load:**
- The map explorer processes large shapefiles on first run; subsequent loads use Streamlit's cache
