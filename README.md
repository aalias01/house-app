# House & Browse — Housing Affordability Dashboard

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75)](https://plotly.com/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-0.14-139C5A)](https://geopandas.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)

> Housing affordability traced at ZIP-code resolution across 30 U.S. metros from 2012 to 2023. Filter by income and year to see exactly where your household falls on the affordability scale.

**[Live Demo](https://houseapp-i2uqriykdh9d6ui38wvwev.streamlit.app)**

---

## What This Answers

| Question | How the app answers it |
|----------|----------------------|
| Which metros became unaffordable over the last decade? | Choropleth map of 30 metros with Demographia five-tier PTI bands, selectable by year |
| Can my household afford to live here? | Income-based affordability finder: set salary, get a ZIP-level map colored by your personal threshold |
| How does my metro's trend compare to others? | Side-by-side PTI time series with color-coded affordability bands and hover detail |
| What drove the national price-income divergence? | Five-chapter narrative: macro trend, metro divergence, affordability bands, rent burden, 2023 snapshot |

**Price-to-Income Ratio (PTI):** `Median Sale Price / (Per Capita Income × 2.54)`. The 2.54 multiplier converts per-capita income to household purchasing power using the median U.S. household size (2019-2023 ACS).

| PTI Range | Affordability Level |
|-----------|---------------------|
| 0.0 – 3.0 | Affordable |
| 3.1 – 4.0 | Moderately Unaffordable |
| 4.1 – 5.0 | Seriously Unaffordable |
| 5.1 – 8.9 | Severely Unaffordable |
| 9.0+ | Impossibly Unaffordable |

*Thresholds from: Cox, Wendell (2025). Demographia International Housing Affordability, 2025 Edition.*

---

Metro-level averages hide what ZIP-level data reveals. A single metro can span PTI values from a low-2s outer suburb to a high-8s urban core, and the aggregate tells neither story accurately. The affordability finder addresses this directly: rather than showing where a metro ranks on average, it colors every ZIP green or red based on whether your specific income clears the affordability threshold for that year.

PTI normalizes for local income in a way that raw price data cannot. San Jose and Cleveland can both be described as "expensive" in absolute terms, but San Jose's higher median incomes make many ZIPs more accessible than their sticker price suggests, while Cleveland ZIPs can be unaffordable precisely because incomes are lower. Converting price to PTI puts every market on the same scale.

The five-chapter narrative module ties the ZIP-level data to a macro story. The gap between price growth and income growth is the structural backdrop for everything the map explorer shows at the ZIP level. Starting the app with the individual map and skipping that context is the most common mistake in housing data communication.

---

## Approach

| Step | Decision | Rationale |
|------|---------|-----------|
| Affordability metric | PTI using median sale price divided by (per-capita income × 2.54 household size) | Normalizes for local income; the multiplier converts per-capita to household purchasing power |
| Tier thresholds | Demographia 2025 five-tier scale | Standard research framing; avoids ad hoc cutoffs that change between analyses |
| Map granularity | CBSA shapes for metro view, ZCTA shapes for ZIP drill-down | ZCTA boundaries align with the ZIP codes in the source data; CBSA captures economic commuting zones |
| App architecture | Streamlit multi-page app with module-level data loading | Native page routing without a separate backend; module isolation prevents redundant data reloads across pages |
| Shapefile caching | `@st.cache_data` on geospatial joins | The ZCTA join takes 10-20 seconds on first load; caching makes subsequent page visits instant within a session |

---

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. Data files are bundled in the repo under `map_explorer/data/`, `trend_comparison/`, and `affordability_finder/city_geojson/` — no additional downloads needed.

---

## Project Structure

```
house_app/
├── app.py                         # Entry point and page navigation
├── pages/
│   ├── intro.py
│   ├── map_explorer.py            # Interactive choropleth map
│   ├── trend_comparison.py        # Time-series PTI comparison
│   ├── affordability_finder.py    # Income-based ZIP filter
│   └── story.py                   # Narrative visualization
├── map_explorer/                  # Choropleth module
│   ├── charts.py
│   ├── config_data.py
│   ├── geo_utils.py
│   ├── events.py
│   └── data/
│       ├── house_ts_agg.csv
│       ├── cbsa_shapes.zip
│       └── zcta_shapes.zip
├── trend_comparison/
│   └── House_reduced.csv
├── affordability_finder/
│   ├── dataprep.py
│   ├── ui_components.py
│   ├── zip_module.py
│   └── city_geojson/              # GeoJSON files per metro area
├── story/
│   ├── charts.py
│   ├── data_utils.py
│   └── data/HouseTS_reduced.csv
└── utils/
    ├── path_utils.py
    └── error_handling.py
```

---

## Limitations

- PTI uses per-capita income from the HouseTS dataset's aggregated metro figures rather than household-level microdata; within-ZIP income variation is smoothed.
- Shapefile processing on first render is slow on Streamlit's free tier; the ZCTA join takes 10-20 seconds before the cache warms.
- Data coverage ends at 2023; more recent affordability shifts are not reflected.
- The Affordability Finder uses the same income threshold across all ZIPs in a metro; local property tax and insurance variation is not accounted for.

---

*Data: [HouseTS Dataset](https://www.kaggle.com/datasets/shengkunwang/housets-dataset/data) (Kaggle) · U.S. Census Bureau CBSA and ZCTA shapefiles*
