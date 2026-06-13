import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown(
    """
    <style>
    [data-testid="stVirtualDropdown"] > div {
        height: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner="Loading required data...") 
def load_data():
    df = pd.read_csv("HouseTS.csv")
    df = df.fillna(0)

    # Price to Income Data Preparation
    df["Household Income"] = 2.54 * df["Per Capita Income"]
    df["Price_Income_Ratio"] = df["median_sale_price"] / df["Household Income"]

    
    
    ratio_agg = (
        df.groupby(["city_full", "year"], as_index=False, observed=True)
        .agg({
            "Price_Income_Ratio": "median",
            "median_sale_price": "median",
            "Household Income": "median"
        })
    )

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
city_order = data[1]
ratio_agg = data[0]

with st.expander("How to Use This Tool", expanded=True, icon="💡"):
    st.markdown("""
                - 🎯 Pick any metropolitan area from the list above — the chart updates instantly.
                - 📊 Compare how affordable house prices are across metropolitan area and over time.
                - 🔍 Hover over any point to see detailed numbers for that year.

                Enjoy exploring! 🚀
                """)

if "selected_cities" not in st.session_state:
    st.session_state.selected_cities = city_order[:5]

def reset_cities():
    st.session_state.selected_cities = city_order[:5]

col1, col2 = st.columns([1.5,5], vertical_alignment="top")
with col1:
    with st.container(border=True, height="content"):
        st.markdown("<h2 style='font-size: 24px;'>Select Metropolitan Area</h2>", unsafe_allow_html=True)
        
        st.button("Reset to Default", on_click=reset_cities)
        selected_cities = st.multiselect(
            "Metro Areas",
            options=city_order,
            key="selected_cities"
        )

    

if len(selected_cities) == 0:
    with col2:
        st.warning("Please select at least one metropolitan area.")
else:
    # ===================================
    # Price to Income Ratio Visualization
    # ===================================

    price_income = ratio_agg[ratio_agg["city_full"].isin(selected_cities)].copy()

    customdata = price_income[["Household Income", "median_sale_price", "Affordability"]].values

    colors = px.colors.qualitative.Plotly  
    color_map = {city: colors[i % len(colors)] for i, city in enumerate(selected_cities)}

    price_income_fig = px.line(
        price_income,
        x="year",
        y="Price_Income_Ratio",
        color="city_full",
        color_discrete_map=color_map,
        markers=True
    )

    for i, trace in enumerate(price_income_fig.data):
        city_name = trace.name
        mask = price_income["city_full"] == city_name
        price_income_fig.data[i].customdata = customdata[mask.values]

    price_income_fig.add_hline(
        y=3,
        line_width=2,
        line_dash="dash",
        line_color="silver",
        annotation_text="0.0-3.0: Affordable",
        annotation_position="bottom right",
        annotation_bgcolor="rgba(255,255,255,0.7)"
    )

    price_income_fig.add_hrect(
        y0=0.0, 
        y1=3.0, 
        line_width=0, 
        fillcolor="Green", 
        layer="below", 
        opacity=0.2
    )

    price_income_fig.add_hline(
        y=4,
        line_width=2,
        line_dash="dash",
        line_color="silver",
        annotation_text="3.1-4.0: Moderately Unaffordable",
        annotation_position="bottom right",
        annotation_bgcolor="rgba(255,255,255,0.7)"
    )

    price_income_fig.add_hrect(
        y0=3.0, 
        y1=4.0, 
        line_width=0, 
        fillcolor="Yellow", 
        layer="below", 
        opacity=0.2
    )

    price_income_fig.add_hline(
        y=5,
        line_width=2,
        line_dash="dash",
        line_color="silver",
        annotation_text="4.1-5.0: Seriously Unaffordable",
        annotation_position="bottom right",
        annotation_bgcolor="rgba(255,255,255,0.7)"
    )

    price_income_fig.add_hrect(
        y0=4.0, 
        y1=5.0, 
        line_width=0, 
        fillcolor="Orange", 
        layer="below", 
        opacity=0.2
    )

    price_income_fig.add_hline(
        y=9,
        line_width=2,
        line_dash="dash",
        line_color="silver",
        annotation_text="5.1-8.9: Severely Unaffordable",
        annotation_position="bottom right",
        annotation_bgcolor="rgba(255,255,255,0.7)"
    )

    price_income_fig.add_hrect(
        y0=5.0, 
        y1=9.0, 
        line_width=0, 
        fillcolor="Red", 
        layer="below", 
        opacity=0.2
    )

    ymax = price_income["Price_Income_Ratio"].max() + 1
    if ymax < 9.0:
        ymax = 10
    
    price_income_fig.add_hline(
        y=ymax,
        line_width=2,
        line_dash="dash",
        line_color="silver",
        annotation_text="9.0+: Impossibly Unaffordable",
        annotation_position="bottom right",
        annotation_bgcolor="rgba(255,255,255,0.7)"
    )

    price_income_fig.add_hrect(
        y0=9.0, 
        y1=ymax,
        line_width=0, 
        fillcolor="DarkRed", 
        layer="below", 
        opacity=0.2
    )

    price_income_fig.update_traces(
        hovertemplate=
            "<b>%{fullData.name}</b><br>" +
            "%{customdata[2]}<br>" +
            "Year: %{x}<br>" +
            "Ratio: x%{y:.2f}<br>" +
            "Median Household Income: $%{customdata[0]:,.0f}<br>" +
            "Median Sale Price: $%{customdata[1]:,.0f}<extra></extra>"
    )

    price_income_fig.update_layout(
        title={"text": "Price-to-Income (PTI):<br>U.S. Metropolitan Areas from 2012 to 2023", "font": {"size": 28}},
        yaxis_title="Price-to-Income Ratio",
        yaxis2=dict(
        title='Right Y-Axis Label',
        overlaying='y',
        side='right'
        ),
        xaxis_title="Year",
        hovermode="closest",
        template="plotly_white",
        legend=dict(title="Metro Area"),
        height=600,
        margin=dict(l=20, r=20, t=120),
        font=dict(size=14)
    )

    # ====================================
    # Dashboard Display
    # ====================================

    with col2:
        with st.container(border=True):
            st.plotly_chart(price_income_fig)



    
