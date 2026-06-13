import sys
from pathlib import Path

# Add utils to path for shared utilities
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.path_utils import setup_design_path, import_from_path, clear_module_cache
from utils.error_handling import show_directory_not_found_error, show_missing_files_error

# Global error handler - wrap everything to catch all errors silently
try:
    # Setup design1 path using shared utility
    design1_path, project_root = setup_design_path("map_explorer")
    
    # Check if design1 directory exists
    if not design1_path.exists():
        import streamlit as st
        show_directory_not_found_error(design1_path, ["config_data.py", "geo_utils.py", "charts.py", "events.py"])

        st.stop()
    
    # Check if required files exist
    required_files = [
        design1_path / "config_data.py",
        design1_path / "geo_utils.py",
        design1_path / "charts.py",
        design1_path / "events.py",
    ]
    
    missing_files = [f for f in required_files if not f.exists()]
    if missing_files:
        import streamlit as st
        show_missing_files_error(missing_files)
        st.stop()

    # Remove other design directories from sys.path to avoid conflicts
    story_path = project_root / "story"
    design2_path = project_root / "trend_comparison"
    design3_path = project_root / "affordability_finder"

    # Remove conflicting paths if they exist
    paths_to_remove = [story_path, design2_path, design3_path]
    from utils.path_utils import add_to_path
    add_to_path(design1_path, remove_others=paths_to_remove)

    import streamlit as st
    import pandas as pd
    import numpy as np
    import geopandas as gpd

    # Clear any cached modules to avoid conflicts with other pages that have modules with same names
    # Force clear all conflicting modules from cache before importing
    modules_to_clear = ['config_data', 'geo_utils', 'charts', 'events']
    clear_module_cache(modules_to_clear)
    
    # Import from design1 directory using file paths to avoid conflicts
    # Import in dependency order: config_data and geo_utils first, then charts and events
    config_data = import_from_path('config_data', design1_path / 'config_data.py')
    geo_utils = import_from_path('geo_utils', design1_path / 'geo_utils.py')
    # Now load charts and events (they depend on config_data and geo_utils)
    # Make sure config_data and geo_utils are in sys.modules so charts can import them
    sys.modules['config_data'] = config_data
    sys.modules['geo_utils'] = geo_utils
    charts_module = import_from_path('charts', design1_path / 'charts.py')
    events_module = import_from_path('events', design1_path / 'events.py')
    
    # Import what we need directly from the loaded modules
    get_dynamic_css = config_data.get_dynamic_css
    get_colorscale = config_data.get_colorscale
    load_all_data = config_data.load_all_data
    compute_pti = config_data.compute_pti
    compute_rankings = config_data.compute_rankings
    get_metro_yoy = config_data.get_metro_yoy
    US_BOUNDS = config_data.US_BOUNDS
    US_CENTER_LAT = config_data.US_CENTER_LAT
    US_CENTER_LON = config_data.US_CENTER_LON
    US_ZOOM_LEVEL = config_data.US_ZOOM_LEVEL
    
    load_cbsa_shapes = geo_utils.load_cbsa_shapes
    load_zcta_shapes = geo_utils.load_zcta_shapes
    get_zip_polygons_for_metro = geo_utils.get_zip_polygons_for_metro
    
    create_city_choropleth = charts_module.create_city_choropleth
    create_zip_choropleth = charts_module.create_zip_choropleth
    create_history_chart = charts_module.create_history_chart
    create_metro_timeseries_chart = charts_module.create_metro_timeseries_chart
    
    extract_city_from_event = events_module.extract_city_from_event
    extract_zip_from_event = events_module.extract_zip_from_event

    # =========================================================================
    # 1. Hide navigation bar and add return home button
    # =========================================================================
    st.markdown("""
    <style>
    /* Hide navigation bar on design pages */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Style return home button */
    .home-button-container {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Return home button at the top
    col_back, col_spacer = st.columns([2, 20])
    with col_back:
        if st.button("🏠 Return Home", use_container_width=True, help="Return to home page", type="secondary"):
            st.switch_page("pages/intro.py")
    
    # =========================================================================
    # 2. Page config (already set by parent app, but we can override if needed)
    # =========================================================================
    # Note: Page config is set in parent app.py, so we don't set it here

    # =========================================================================
    # 3. Session state init (with page-specific keys to avoid conflicts)
    # =========================================================================
    design1_prefix = "design1_"
    if f"{design1_prefix}view_mode" not in st.session_state:
        st.session_state[f"{design1_prefix}view_mode"] = "city"
    if f"{design1_prefix}selected_city" not in st.session_state:
        st.session_state[f"{design1_prefix}selected_city"] = None
    if f"{design1_prefix}selected_zip" not in st.session_state:
        st.session_state[f"{design1_prefix}selected_zip"] = None

    # =========================================================================
    # 4. Load data
    # =========================================================================
    try:
        df_all = load_all_data()
    except FileNotFoundError as e:
        st.error(f"""
            ❌ **Data File Not Found**
            
            Unable to find the data file. Please check:
            - Data file exists: `map_explorer/data/house_ts_agg.csv`
            - File path is correct
            - You have read permissions
            
            **Technical details:** {str(e)}
        """)
        if st.button("🔄 Retry Loading Data"):
            st.cache_data.clear()
            st.rerun()
        st.stop()
    except Exception as e:
        st.error(f"""
            ❌ **Data Loading Error**
            
            Unable to load data from the source. Please check:
            - Data file format is correct
            - File is not corrupted
            - You have read permissions
            
            **Technical details:** {str(e)}
        """)
        if st.button("🔄 Retry Loading Data"):
            st.cache_data.clear()
            st.rerun()
        st.stop()

    if df_all.empty:
        st.warning("""
            ⚠️ **No Data Available**
            
            The data file is empty or contains no valid records.
            Please check the data source and try again.
        """)
        st.stop()

    min_year = int(df_all["year"].min())
    max_year = int(df_all["year"].max())

    # Detect Streamlit theme (for UI elements, not just map style)
    try:
        theme_base = st.get_option("theme.base")
        streamlit_is_dark = theme_base == "dark"
    except:
        streamlit_is_dark = False

    is_dark_mode = streamlit_is_dark
    map_style = "carto-positron"

    # =========================================================================
    # 5. Header & intro (moved before control panel)
    # =========================================================================
    st.title("🏙️ Metro → ZIP Sale Price/PTI Explorer")

    with st.expander("ℹ️ How to use this app", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                """
                ### **Navigation**
                - **Select a year** using the year slider in the control panel
                - **Select a metric** (PTI or Median Sale Price) from the control panel
                - **Hover** over metros/ZIPs to preview statistics  
                - **Click** a metro to view its ZIP codes  
                - **Click** a ZIP code to see detailed metrics  
                - Use **Back to All Metros** to return to national view
                """
            )

        with col2:
            st.markdown(
                """
            **Metrics**
            - **Median Sale Price**: The median price of houses sold during a specific time period
            - **PTI (Price-to-Income Ratio)**: Median Sale Price ÷ Median Household Income
              - Lower PTI = more affordable
            """
            )

    st.markdown("---")

    # =========================================================================
    # 6. Top Control Panel (moved after title and intro)
    # =========================================================================
    st.markdown("### 🧭 Control Panel")
    control_col1, control_col2, control_col3 = st.columns([2, 2, 3])

    with control_col1:
        selected_year = st.slider("Year", min_year, max_year, max_year, help=f"Data range: {min_year} – {max_year}")

    with control_col2:
        metric_type = st.radio(
            "Metric",
            ["Price-to-Income Ratio (PTI)", "Median Sale Price"],
            index=0,
            horizontal=True,
            help="PTI Formula: Median Sale Price / Median Household Income\n\nMedian Sale Price: The median price of houses sold during a specific time period",
        )
    
    # Update caption after control panel values are set
    st.caption(f"Year: **{selected_year}** · Metric: **{metric_type}**")

    with control_col3:
        if st.session_state[f"{design1_prefix}view_mode"] == "city":
            st.markdown("**🔍 Quick Metro Search**")
            df_filtered_sidebar = df_all[df_all["year"] == selected_year].copy()
            if not df_filtered_sidebar.empty:
                df_city_sidebar = (
                    df_filtered_sidebar.groupby(["city", "city_full"], as_index=False, observed=True)
                    .agg(avg_median_sale_price=("median_sale_price", "mean"))
                )
                metro_list = (
                    df_city_sidebar.drop_duplicates(subset=["city_full"])
                    .sort_values("city_full")["city_full"]
                    .tolist()
                )

                selected_metro = st.selectbox(
                    "Select metro",
                    metro_list,
                    index=None,
                    placeholder="Type to search...",
                    format_func=lambda x: f"📍 {x}",
                    label_visibility="collapsed",
                )

                if selected_metro:
                    city_match = (
                        df_city_sidebar[df_city_sidebar["city_full"] == selected_metro]["city"].iloc[0]
                    )
                    if st.session_state.get(f"{design1_prefix}selected_city") != city_match:
                        st.session_state[f"{design1_prefix}selected_city"] = city_match
                        st.session_state[f"{design1_prefix}view_mode"] = "zip"
                        st.session_state[f"{design1_prefix}selected_zip"] = None
                        st.rerun()

    st.markdown("---")

    # =========================================================================
    # 7. Apply CSS
    # =========================================================================
    st.markdown(get_dynamic_css(is_dark_mode), unsafe_allow_html=True)

    # =========================================================================
    # 8. Build metric data for selected_year
    # =========================================================================
    df_year = df_all[df_all["year"] == selected_year].copy()
    if df_year.empty:
        st.warning(f"### ⚠️ No Data Available for {selected_year}")
        st.info("Please try selecting a different year from the control panel above.")
        st.stop()

    if metric_type == "Price-to-Income Ratio (PTI)":
        df_year = compute_pti(df_year)
        value_source_col = "PTI"
        if df_year.empty:
            st.warning(f"⚠️ PTI values out of range for {selected_year}.")
            st.stop()

        df_zip_metric = (
            df_year.groupby(
                ["city", "city_full", "city_clean", "zip_code_str", "year"], as_index=False, observed=True
            ).agg(
                metric_value=("PTI", "mean"),
                lat=("lat", "mean"),
                lon=("lon", "mean"),
            )
        )

        df_city = (
            df_zip_metric.groupby(["city", "city_full", "city_clean"], as_index=False, observed=True).agg(
                n=("zip_code_str", "count"),
                avg_metric_value=("metric_value", "mean"),
                lat=("lat", "mean"),
                lon=("lon", "mean"),
            )
        )
    else:
        df_year = df_year[df_year["median_sale_price"].notna()].copy()
        value_source_col = "median_sale_price"
        if df_year.empty:
            st.warning(f"⚠️ No valid price data for {selected_year}.")
            st.stop()

        df_zip_metric = (
            df_year.groupby(
                ["city", "city_full", "city_clean", "zip_code_str", "year"], as_index=False, observed=True
            ).agg(
                metric_value=("median_sale_price", "mean"),
                lat=("lat", "mean"),
                lon=("lon", "mean"),
            )
        )

        df_city = (
            df_zip_metric.groupby(["city", "city_full", "city_clean"], as_index=False, observed=True).agg(
                n=("zip_code_str", "count"),
                avg_metric_value=("metric_value", "mean"),
                lat=("lat", "mean"),
                lon=("lon", "mean"),
            )
        )

    df_city_map = df_city.copy().reset_index(drop=True)
    df_city_map = compute_rankings(df_city_map, "avg_metric_value", "city")

    metro_yoy = get_metro_yoy(df_all, selected_year, metric_type)

    current_metro_name = None
    if st.session_state[f"{design1_prefix}selected_city"]:
        row_sel = df_city_map[df_city_map["city"] == st.session_state[f"{design1_prefix}selected_city"]]
        if not row_sel.empty:
            current_metro_name = row_sel["city_full"].iloc[0]

    # =========================================================================
    # 9. Main view (metro / zip)
    # =========================================================================
    if st.session_state[f"{design1_prefix}view_mode"] == "city":
        # --------------------- METRO VIEW ---------------------
        st.info(
            f"📍 **Metro View ({selected_year}) · {metric_type}**  · "
            f"Hover for details · Click to drill down · Scroll to zoom"
        )

        st.markdown("#### 📊 National Summary")
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)

        with col_s1:
            st.metric(
                "Total Metros", 
                len(df_city_map),
                help="Total number of metropolitan areas included in the dataset (30 metro areas across all years)"
            )

        with col_s2:
            avg_val = df_city_map["avg_metric_value"].mean()
            if metric_type == "Price-to-Income Ratio (PTI)":
                st.metric(
                    "Avg PTI", 
                    f"{avg_val:.2f}x",
                    help="Average Price-to-Income Ratio across all metro areas. Formula: Median Sale Price / Median Household Income. Lower values indicate better affordability."
                )
            else:
                st.metric(
                    "Avg Price", 
                    f"${avg_val:,.0f}",
                    help="Average median sale price across all metro areas. The median price of houses sold during the selected time period."
                )

        with col_s3:
            top_metro = df_city_map.loc[df_city_map["avg_metric_value"].idxmax()]
            metro_label_high = top_metro["city_full"]
            if metric_type == "Price-to-Income Ratio (PTI)":
                st.metric(
                    "Highest PTI", 
                    f"{top_metro['avg_metric_value']:.2f}x",
                    help=f"Highest Price-to-Income Ratio among all metro areas. {metro_label_high} has the least affordable housing based on PTI."
                )
            else:
                st.metric(
                    "Highest Price", 
                    f"${top_metro['avg_metric_value']:,.0f}",
                    help=f"Highest median sale price among all metro areas. {metro_label_high} has the most expensive housing."
                )
            st.caption(f"Metro: **{metro_label_high}**")

        with col_s4:
            bottom_metro = df_city_map.loc[df_city_map["avg_metric_value"].idxmin()]
            metro_label_low = bottom_metro["city_full"]
            if metric_type == "Price-to-Income Ratio (PTI)":
                st.metric(
                    "Lowest PTI", 
                    f"{bottom_metro['avg_metric_value']:.2f}x",
                    help=f"Lowest Price-to-Income Ratio among all metro areas. {metro_label_low} has the most affordable housing based on PTI."
                )
            else:
                st.metric(
                    "Lowest Price", 
                    f"${bottom_metro['avg_metric_value']:,.0f}",
                    help=f"Lowest median sale price among all metro areas. {metro_label_low} has the most affordable housing."
                )
            st.caption(f"Metro: **{metro_label_low}**")

        with col_s5:
            if not metro_yoy.empty and "yoy_pct" in metro_yoy.columns:
                avg_yoy = metro_yoy["yoy_pct"].mean()
                if not pd.isna(avg_yoy):
                    st.metric(
                        "Avg YoY Change",
                        f"{avg_yoy:+.1f}%",
                        delta="vs last year",
                        delta_color="off",
                        help="Year-over-Year (YoY): The average percentage change across all metro areas compared to the previous year. Positive values indicate an increase, negative values indicate a decrease."
                    )
                else:
                    st.metric("Avg YoY Change", "N/A", delta="No prior year", delta_color="off", help="Year-over-Year (YoY): The percentage change compared to the previous year.")
            else:
                st.metric("Avg YoY Change", "N/A", delta="No prior year", delta_color="off", help="Year-over-Year (YoY): The percentage change compared to the previous year.")

        st.markdown("---")

        fig_city = None
        gdf_metro = None
        try:
            with st.spinner("🗺️ Loading metro boundaries..."):
                cbsa_shapes = load_cbsa_shapes()
            with st.spinner("📊 Generating metro map..."):
                fig_city, gdf_metro = create_city_choropleth(
                    df_city_map, cbsa_shapes, map_style, metric_type, is_dark_mode
                )
        except Exception as e:
            st.error(f"""
                ❌ **Map Generation Error**
                
                Unable to generate the metro map. This could be due to:
                - Missing shapefile data
                - Corrupted shapefile files
                - Insufficient memory
                
                **Technical details:** {str(e)}
            """)

        if fig_city is not None and gdf_metro is not None:
            event = st.plotly_chart(
                fig_city,
                width="stretch",
                on_select="rerun",
                selection_mode="points",
                key=f"metro_map_{selected_year}_{metric_type}_{map_style}",
                config={"scrollZoom": True},
            )
            clicked_city = extract_city_from_event(event)
            
            # Fallback: try to extract from Choroplethmapbox location if Scattermapbox customdata fails
            if not clicked_city and event and event.selection and event.selection.points:
                for clicked_point in event.selection.points:
                    # Try customdata first (from Scattermapbox or Choroplethmapbox)
                    cd = clicked_point.get("customdata", None)
                    if isinstance(cd, (list, tuple)) and len(cd) > 0:
                        clicked_city = cd[0]
                        break
                    
                    # Try location (from Choroplethmapbox)
                    location = clicked_point.get("location", None)
                    if location is not None:
                        match = gdf_metro[gdf_metro["id"] == str(location)]
                        if not match.empty:
                            clicked_city = match.iloc[0]["city"]
                            break
                    
                    # Try point_index as last resort
                    point_idx = clicked_point.get("point_index", None)
                    if point_idx is not None and point_idx < len(gdf_metro):
                        clicked_city = gdf_metro.iloc[point_idx]["city"]
                        break
            
            if clicked_city:
                # Only update if different from current selection to avoid unnecessary reruns
                current_city = st.session_state.get(f"{design1_prefix}selected_city")
                if current_city != clicked_city:
                    st.session_state[f"{design1_prefix}selected_city"] = clicked_city
                    st.session_state[f"{design1_prefix}selected_zip"] = None
                    st.session_state[f"{design1_prefix}view_mode"] = "zip"
                    st.rerun()

    else:
        # --------------------- ZIP VIEW ---------------------
        selected_city = st.session_state[f"{design1_prefix}selected_city"]
        if not selected_city:
            st.warning("⚠️ **No Metro Selected**")
            st.info("Please use the 'Quick Metro Search' in the control panel above to select a metro area, or click on a metro on the map.")
            st.stop()

        st.markdown(f"### 🗺️ `USA` → `{current_metro_name or selected_city}` → `ZIP Codes`")
        
        if st.button("⬅️ Back to All Metros", use_container_width=False):
            st.session_state[f"{design1_prefix}view_mode"] = "city"
            st.session_state[f"{design1_prefix}selected_city"] = None
            st.session_state[f"{design1_prefix}selected_zip"] = None
            st.rerun()
        
        st.markdown("---")

        label = current_metro_name or selected_city
        st.info(
            f"📍 **{label}** ({selected_year}) · {metric_type}  · "
            f"Click ZIPs to see details · Scroll to zoom · Double-click to reset"
        )

        try:
            with st.spinner("🗺️ Loading ZIP code boundaries..."):
                zcta_shapes = load_zcta_shapes()
            with st.spinner("📊 Processing ZIP code data..."):
                zip_df_city, gdf_merge = get_zip_polygons_for_metro(
                    selected_city, zcta_shapes, df_zip_metric
                )
        except Exception as e:
            st.error(f"""
                ❌ **ZIP Code Data Error**
                
                Unable to load ZIP code boundaries. This could be due to:
                - Missing shapefile data
                - Corrupted shapefile files
                - Data processing error
                
                **Technical details:** {str(e)}
            """)
            zip_df_city, gdf_merge = pd.DataFrame(), gpd.GeoDataFrame()

        if gdf_merge.empty or zip_df_city.empty:
            st.warning(f"""
                ⚠️ **No ZIP Code Data Available**
                
                No ZIP code data found for **{selected_city}** in **{selected_year}**.
                
                **Suggestions:**
                - Try selecting a different year
                - Try selecting a different metro area
                - Check if data exists for this metro in other years
            """)
        else:
            zip_df_city = zip_df_city[zip_df_city["metric_value"].notna()].copy()

            valid_zips = gdf_merge["zip_code_str"].unique()
            zip_df_city = zip_df_city[zip_df_city["zip_code_str"].isin(valid_zips)].copy()

            if zip_df_city.empty:
                st.warning(f"""
                    ⚠️ **No Valid Data Available**
                    
                    No valid {metric_type} data for **{selected_city}** in **{selected_year}**.
                    
                    **Possible reasons:**
                    - Data not available for this metro/year combination
                    - All values are missing or invalid
                    - Data filtering removed all records
                """)
            else:
                zip_df_city = compute_rankings(zip_df_city, "metric_value", "zip_code_str")

                # Get currently selected ZIP
                current_selected_zip = st.session_state.get(f"{design1_prefix}selected_zip")
                
                # Validate and update selected ZIP
                # If no ZIP is selected, or the selected ZIP doesn't exist in current year's data,
                # select the first available ZIP
                if current_selected_zip is None:
                    if not zip_df_city.empty:
                        st.session_state[f"{design1_prefix}selected_zip"] = zip_df_city["zip_code_str"].iloc[0]
                elif current_selected_zip not in zip_df_city["zip_code_str"].values:
                    # Selected ZIP doesn't exist in current year, select first available
                    if not zip_df_city.empty:
                        st.session_state[f"{design1_prefix}selected_zip"] = zip_df_city["zip_code_str"].iloc[0]
                # Otherwise, keep the previously selected ZIP (it exists in current year's data)

                col_map, col_detail = st.columns([2, 1.2])

                with col_map:
                    city_coords = None
                    
                    city_coords = None
                    with st.spinner("📊 Generating ZIP code map..."):
                        fig_zip, gdf_zip = create_zip_choropleth(
                            gdf_merge, map_style, city_coords, zip_df_city, metric_type, is_dark_mode
                        )
                    
                    if fig_zip is not None and gdf_zip is not None:
                        event = st.plotly_chart(
                            fig_zip,
                            width="stretch",
                            on_select="rerun",
                            selection_mode="points",
                            key=f"zip_map_{selected_city}_{selected_year}_{metric_type}_{map_style}",
                            config={"scrollZoom": True},
                        )
                        
                        # Process click event
                        clicked_zip = extract_zip_from_event(event, gdf_zip)
                        
                        # If a new ZIP was clicked, update session state immediately
                        if clicked_zip:
                            current_zip = st.session_state.get(f"{design1_prefix}selected_zip")
                            if clicked_zip != current_zip and clicked_zip in zip_df_city["zip_code_str"].values:
                                # Update session state immediately
                                # The rerun from on_select will use this updated value
                                st.session_state[f"{design1_prefix}selected_zip"] = clicked_zip

                with col_detail:
                    st.subheader("📋 ZIP Details")
                    active_zip = st.session_state.get(f"{design1_prefix}selected_zip")
                    if not active_zip:
                        st.info("👈 Click any ZIP on the map")
                    else:
                        row_now = zip_df_city[zip_df_city["zip_code_str"] == active_zip]
                        if row_now.empty:
                            st.warning(f"⚠️ No data for ZIP {active_zip}")
                        else:
                            metric_val = float(row_now["metric_value"].iloc[0])
                            metro_avg_now = float(zip_df_city["metric_value"].mean())
                            diff = metric_val - metro_avg_now
                            pct_diff = (diff / metro_avg_now * 100) if metro_avg_now != 0 else 0.0
                            rank = int(row_now["rank"].iloc[0])
                            rank_total = int(row_now["rank_total"].iloc[0])
                            percentile = float(row_now["percentile"].iloc[0])
                            metro_name = row_now["city_full"].iloc[0]

                            title_color = "#e5e7eb" if is_dark_mode else "#111827"
                            caption_color = "#9ca3af" if is_dark_mode else "#6b7280"
                            
                            st.markdown(
                                f'<h3 style="color: {title_color};">ZIP <code style="background: {"rgba(255,255,255,0.1)" if is_dark_mode else "rgba(0,0,0,0.05)"}; padding: 2px 6px; border-radius: 4px;">{active_zip}</code></h3>',
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f'<p style="color: {caption_color}; font-size: 0.875rem; margin-top: -0.5rem;">{metro_name}</p>',
                                unsafe_allow_html=True
                            )

                            if metric_type == "Price-to-Income Ratio (PTI)":
                                zip_prev_raw = df_all[
                                    (df_all["city"] == selected_city)
                                    & (df_all["zip_code_str"] == active_zip)
                                    & (df_all["year"] == selected_year - 1)
                                ].copy()
                                zip_prev_raw = compute_pti(zip_prev_raw) if not zip_prev_raw.empty else pd.DataFrame()
                                if not zip_prev_raw.empty:
                                    prev_val = zip_prev_raw["PTI"].mean()
                                    yoy_change = ((metric_val - prev_val) / prev_val * 100)
                                    main_value = f"{metric_val:.2f}x"
                                    delta_text = f"{yoy_change:+.1f}% YoY"
                                    # Note: Tooltip for YoY is shown via help parameter in st.metric
                                else:
                                    main_value = f"{metric_val:.2f}x"
                                    delta_text = "No prior year"
                            else:
                                zip_prev = df_all[
                                    (df_all["city"] == selected_city)
                                    & (df_all["zip_code_str"] == active_zip)
                                    & (df_all["year"] == selected_year - 1)
                                    & df_all["median_sale_price"].notna()
                                ]
                                if not zip_prev.empty:
                                    prev_val = zip_prev["median_sale_price"].mean()
                                    yoy_change = ((metric_val - prev_val) / prev_val * 100)
                                    main_value = f"${metric_val:,.0f}"
                                    delta_text = f"{yoy_change:+.1f}% YoY"
                                    # Note: Tooltip for YoY is shown via help parameter in st.metric
                                else:
                                    main_value = f"${metric_val:,.0f}"
                                    delta_text = "No prior year"

                            rank_percentile = 100 - percentile
                            if pct_diff > 5:
                                diff_label = f"{pct_diff:+.1f}% above metro avg"
                            elif pct_diff < -5:
                                diff_label = f"{pct_diff:+.1f}% below metro avg"
                            else:
                                diff_label = f"{pct_diff:+.1f}% vs metro avg"

                            label_color = "#9ca3af" if is_dark_mode else "#6b7280"
                            text_color = "#e5e7eb" if is_dark_mode else "#111827"
                            secondary_text_color = "#d1d5db" if is_dark_mode else "#4b5563"
                            
                            # Tooltip texts
                            pti_tooltip = "PTI Formula: Median Sale Price / Median Household Income. Lower values indicate better affordability."
                            price_tooltip = "The median price of houses sold during a specific time period."
                            yoy_tooltip = "Year-over-Year (YoY): The percentage change compared to the previous year. Positive values indicate an increase, negative values indicate a decrease."
                            
                            if metric_type == "Price-to-Income Ratio (PTI)":
                                rank_tooltip = f"Rank #{rank} out of {rank_total} ZIP codes in this metro area, sorted in descending order (highest to lowest). Top {rank_percentile:.0f}% means this ZIP is more affordable than {rank_percentile:.0f}% of ZIP codes in this metro."
                                relative_tooltip = f"This ZIP is {abs(pct_diff):.1f}% {'above' if pct_diff > 0 else 'below'} the metro average. {'Less affordable' if pct_diff > 0 else 'More affordable'} than the typical ZIP in this metro area."
                            else:
                                rank_tooltip = f"Rank #{rank} out of {rank_total} ZIP codes in this metro area, sorted in descending order (highest to lowest). Top {rank_percentile:.0f}% means this ZIP has a lower median sale price than {rank_percentile:.0f}% of ZIP codes in this metro."
                                relative_tooltip = f"This ZIP is {abs(pct_diff):.1f}% {'above' if pct_diff > 0 else 'below'} the metro average. {'More expensive' if pct_diff > 0 else 'Less expensive'} than the typical ZIP in this metro area."
                            
                            st.markdown(
                                f"""
                                <div class="metric-card">
                                    <div style="font-size: 0.8rem; text-transform: uppercase; color: {label_color}; margin-bottom: 0.25rem;" title="{'PTI Formula: Median Sale Price / Median Household Income. Lower values indicate better affordability.' if 'PTI' in metric_type else 'The median price of houses sold during a specific time period.'}">
                                        {'PTI Ratio' if 'PTI' in metric_type else 'Median Sale Price'}
                                    </div>
                                    <div style="font-size: 1.6rem; font-weight: 600; margin-bottom: 0.1rem; color: {text_color};" title="{'PTI Formula: Median Sale Price / Median Household Income. Lower values indicate better affordability.' if 'PTI' in metric_type else 'The median price of houses sold during a specific time period.'}">
                                        {main_value}
                                    </div>
                                    <div style="font-size: 0.85rem; color: {secondary_text_color}; margin-bottom: 0.6rem; cursor: help;" title="Year-over-Year (YoY): The percentage change compared to the previous year. Positive values indicate an increase, negative values indicate a decrease.">
                                        {delta_text}
                                    </div>
                                    <div style="font-size: 0.9rem; color: {text_color}; line-height: 1.5;">
                                        <b>Rank:</b> <span title="{rank_tooltip}" style="cursor: help; text-decoration: underline; text-decoration-style: dotted;">#{rank} of {rank_total} (descending) · Top {rank_percentile:.0f}% in this metro</span><br>
                                        <b>Relative to metro:</b> <span title="{relative_tooltip}" style="cursor: help; text-decoration: underline; text-decoration-style: dotted;">{diff_label}</span>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            st.markdown("#### 📈 Historical Trend Over Time")
                            if metric_type == "Price-to-Income Ratio (PTI)":
                                zip_hist_raw = df_all[
                                    (df_all["city"] == selected_city)
                                    & (df_all["zip_code_str"] == active_zip)
                                ].copy()
                                zip_hist_raw = compute_pti(zip_hist_raw)
                                if not zip_hist_raw.empty:
                                    zip_hist = (
                                        zip_hist_raw.groupby("year", as_index=False, observed=True)
                                        .agg(PTI=("PTI", "mean"))
                                        .sort_values("year")
                                    )
                                    if not zip_hist.empty:
                                        fig_hist = create_history_chart(
                                            zip_hist, metro_avg_now, metric_type, is_dark_mode
                                        )
                                        if fig_hist:
                                            st.plotly_chart(
                                                fig_hist,
                                                width='stretch',
                                                config={"displayModeBar": False},
                                            )
                                    else:
                                        st.caption("No historical data for this ZIP.")
                                else:
                                    st.caption("No historical data for this ZIP.")
                            else:
                                zip_hist = (
                                    df_all[
                                        (df_all["city"] == selected_city)
                                        & (df_all["zip_code_str"] == active_zip)
                                        & df_all["median_sale_price"].notna()
                                    ]
                                    .groupby("year", as_index=False, observed=True)
                                    .agg(price=("median_sale_price", "mean"))
                                    .sort_values("year")
                                )
                                if not zip_hist.empty:
                                    fig_hist = create_history_chart(
                                        zip_hist, metro_avg_now, metric_type, is_dark_mode
                                    )
                                    if fig_hist:
                                        st.plotly_chart(
                                            fig_hist,
                                            use_container_width=True,
                                            config={"displayModeBar": False},
                                        )
                                else:
                                    st.caption("No historical data for this ZIP.")

                            st.markdown("---")
                            csv = zip_df_city[
                                ["zip_code_str", "year", "metric_value", "city_full", "rank"]
                            ].to_csv(index=False)
                            st.download_button(
                                label="📥 Download ZIP-level data (CSV)",
                                data=csv,
                                file_name=f"{selected_city.replace(',', '_')}_{selected_year}_zipdata.csv",
                                mime="text/csv",
                                use_container_width=True,
                            )

                st.markdown("---")
                st.markdown("#### 📊 Metro Summary")
                col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

                values = zip_df_city["metric_value"]
                nonzero_values = values[values > 0]

                with col_m1:
                    st.metric(
                        "ZIP Codes (on map)", 
                        len(zip_df_city),
                        help="Total number of ZIP codes displayed on the map for this metro area in the selected year"
                    )

                with col_m2:
                    if metric_type == "Price-to-Income Ratio (PTI)":
                        st.metric(
                            "Metro Avg", 
                            f"{values.mean():.2f}x",
                            help="Average Price-to-Income Ratio across all ZIP codes in this metro area. Formula: Median Sale Price / Median Household Income."
                        )
                    else:
                        st.metric(
                            "Metro Avg", 
                            f"${values.mean():,.0f}",
                            help="Average median sale price across all ZIP codes in this metro area. The median price of houses sold during the selected time period."
                        )

                with col_m3:
                    if metric_type == "Price-to-Income Ratio (PTI)":
                        st.metric(
                            "Max PTI",
                            f"{nonzero_values.max():.2f}x"
                            if not nonzero_values.empty
                            else "N/A",
                            help="Highest Price-to-Income Ratio among all ZIP codes in this metro area. Indicates the least affordable ZIP code."
                        )
                    else:
                        st.metric(
                            "Max Price",
                            f"${nonzero_values.max():,.0f}"
                            if not nonzero_values.empty
                            else "N/A",
                            help="Highest median sale price among all ZIP codes in this metro area. Indicates the most expensive ZIP code."
                        )

                with col_m4:
                    if metric_type == "Price-to-Income Ratio (PTI)":
                        st.metric(
                            "Min PTI",
                            f"{nonzero_values.min():.2f}x"
                            if not nonzero_values.empty
                            else "N/A",
                            help="Lowest Price-to-Income Ratio among all ZIP codes in this metro area. Indicates the most affordable ZIP code."
                        )
                    else:
                        st.metric(
                            "Min Price",
                            f"${nonzero_values.min():,.0f}"
                            if not nonzero_values.empty
                            else "N/A",
                            help="Lowest median sale price among all ZIP codes in this metro area. Indicates the most affordable ZIP code."
                        )

                with col_m5:
                    metro_row = (
                        metro_yoy[metro_yoy["city"] == selected_city]
                        if not metro_yoy.empty
                        else pd.DataFrame()
                    )
                    if not metro_row.empty and "yoy_pct" in metro_row.columns:
                        yoy_val = metro_row["yoy_pct"].iloc[0]
                        if not pd.isna(yoy_val):
                            st.metric(
                                "YoY Change", 
                                f"{yoy_val:+.1f}%",
                                help="Year-over-Year (YoY): The percentage change compared to the previous year. Positive values indicate an increase, negative values indicate a decrease."
                            )
                        else:
                            st.metric("YoY Change", "N/A", help="Year-over-Year (YoY): The percentage change compared to the previous year.")
                    else:
                        st.metric("YoY Change", "N/A", help="Year-over-Year (YoY): The percentage change compared to the previous year.")
                
                st.markdown("#### 📈 Metro-Level Trend Over Time")
                valid_zips_for_chart = zip_df_city["zip_code_str"].unique()
                
                if metric_type == "Price-to-Income Ratio (PTI)":
                    metro_hist_raw = df_all[df_all["city"] == selected_city].copy()
                    metro_hist_raw = compute_pti(metro_hist_raw)
                    if not metro_hist_raw.empty:
                        metro_zip_year = (
                            metro_hist_raw.groupby(
                                ["city", "city_full", "city_clean", "zip_code_str", "year"], as_index=False, observed=True
                            ).agg(PTI=("PTI", "mean"))
                        )
                        metro_zip_year = metro_zip_year[metro_zip_year["zip_code_str"].isin(valid_zips_for_chart)].copy()
                        metro_hist = (
                            metro_zip_year.groupby("year", as_index=False, observed=True)
                            .agg(PTI=("PTI", "mean"))
                            .sort_values("year")
                        )
                        if not metro_hist.empty:
                            fig_metro_ts = create_metro_timeseries_chart(
                                metro_hist, metric_type, is_dark_mode
                            )
                            if fig_metro_ts:
                                st.plotly_chart(
                                    fig_metro_ts,
                                    width='stretch',
                                    config={
                                        "displayModeBar": False,
                                        "staticPlot": False,
                                    },
                                )
                                st.caption("Affordability levels based on Price-to-Income Ratio thresholds from: Cox, Wendell (2025). *Demographia International Housing Affordability, 2025 Edition*. Center for Demographics and Policy.")
                        else:
                            st.caption("No historical data available for this metro.")
                    else:
                        st.caption("No historical data available for this metro.")
                else:
                    metro_hist_raw = df_all[
                        (df_all["city"] == selected_city)
                        & df_all["median_sale_price"].notna()
                    ].copy()
                    if not metro_hist_raw.empty:
                        metro_zip_year = (
                            metro_hist_raw.groupby(
                                ["city", "city_full", "city_clean", "zip_code_str", "year"], as_index=False, observed=True
                            ).agg(metric_value=("median_sale_price", "mean"))
                        )
                        metro_zip_year = metro_zip_year[metro_zip_year["zip_code_str"].isin(valid_zips_for_chart)].copy()
                        metro_hist = (
                            metro_zip_year.groupby("year", as_index=False, observed=True)
                            .agg(metric_value=("metric_value", "mean"))
                            .sort_values("year")
                        )
                        if not metro_hist.empty:
                            fig_metro_ts = create_metro_timeseries_chart(
                                metro_hist, metric_type, is_dark_mode
                            )
                            if fig_metro_ts:
                                st.plotly_chart(
                                    fig_metro_ts,
                                    width='stretch',
                                    config={
                                        "displayModeBar": False,
                                        "staticPlot": False,
                                    },
                                )
                                if metric_type == "Price-to-Income Ratio (PTI)":
                                    st.caption("Affordability levels based on Price-to-Income Ratio thresholds from: Cox, Wendell (2025). *Demographia International Housing Affordability, 2025 Edition*. Center for Demographics and Policy.")
                        else:
                            st.caption("No historical data available for this metro.")
                    else:
                        st.caption("No historical data available for this metro.")

except FileNotFoundError as e:
    import streamlit as st
    from utils.error_handling import show_file_not_found_error
    error_msg = str(e)
    # Ignore errors about app.py files (they are intentionally removed from design directories)
    if "app.py" not in error_msg.lower():
        # Extract file path from error message if possible
        try:
            file_path = Path(error_msg.split("'")[1]) if "'" in error_msg else Path(str(e))
            show_file_not_found_error(file_path, "required file")
        except:
            st.error(f"❌ **File Not Found Error**: {error_msg}\n\nPlease ensure all required files are present.")
        st.stop()
except Exception as e:
    import streamlit as st
    import traceback
    st.error(f"❌ **Error Loading Map Explorer**: {str(e)}")
    with st.expander("Error Details"):
        st.code(traceback.format_exc())
    st.stop()
finally:
    # Restore original working directory
    try:
        # original_cwd should be available from the outer scope
        if 'original_cwd' in locals() and original_cwd:
            os.chdir(original_cwd)
    except (NameError, OSError):
        # If original_cwd is not defined or chdir fails, just pass
        pass

