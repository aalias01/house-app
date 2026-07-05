# Housing Affordability Dashboard

> ZIP-level price-to-income ratios across 30 U.S. metros, 2012 to 2023. Set your income and year to see where you can afford to live.

**[Live demo](https://houseapp-i2uqriykdh9d6ui38wvwev.streamlit.app)**

I built this in a DATA 511 group project, then refactored the repo for my portfolio: one data layer, clearer module names, and no leftover course scaffolding.

## What you can try

- **Map explorer:** choropleth of 30 metros with Demographia affordability bands; drill down to ZIP codes
- **Time series comparison:** PTI trends across metros with color-coded bands
- **Affordability finder:** set an annual income, get a ZIP-level map for your threshold
- **Key insights:** five-chapter narrative on price vs. income divergence, 2012 to 2023

The live app runs on Streamlit's free tier. The first map load after idle can take 10-20 seconds while shapefiles are joined and cached.

## Price-to-income ratio

`PTI = median sale price / (per capita income x 2.54)`

The 2.54 multiplier converts per-capita income to household purchasing power (median U.S. household size, 2019-2023 ACS). Tiers follow Demographia International Housing Affordability (2025):

| PTI | Level |
|-----|-------|
| 0.0 - 3.0 | Affordable |
| 3.1 - 4.0 | Moderately Unaffordable |
| 4.1 - 5.0 | Seriously Unaffordable |
| 5.1 - 8.9 | Severely Unaffordable |
| 9.0+ | Impossibly Unaffordable |

Metro averages hide ZIP-level spread. A single metro can run from low-2s in outer suburbs to high-8s in the urban core. The affordability finder colors each ZIP against your income instead of showing a metro-wide average.

## Limitations

- PTI uses metro-aggregated per-capita income, not household microdata. Within-ZIP income variation is smoothed.
- Shapefile joins are slow on first render before the cache warms.
- Data ends at 2023.
- The affordability finder applies one income threshold across all ZIPs in a metro. Local tax and insurance variation is not modeled.

## Stack

Streamlit, Plotly, GeoPandas, Pandas

## Project structure

```
house_app/
├── app.py
├── pages/                  # Streamlit multi-page entry points
├── data/
│   ├── housets_zip_level.csv
│   ├── metro_map_aggregates.csv
│   └── geo/
├── map_explorer/           # choropleth module
├── affordability_finder/   # income-based ZIP filter
├── narrative/              # key insights charts
└── utils/
```

Data: [HouseTS Dataset](https://www.kaggle.com/datasets/shengkunwang/housets-dataset/data) (Kaggle). Built by [Alvin Alias](https://github.com/aalias01).
