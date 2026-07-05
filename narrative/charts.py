# charts.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


from data_utils import AFFORDABILITY_COLORS, AFFORDABILITY_ORDER, classify_affordability


# ---------- CHAPTER 1: MACRO TREND ----------

def composite_price_income_index_chart(comp: pd.DataFrame) -> go.Figure:
    """Composite price vs income, indexed to 2012 = 100."""
    long = comp.melt(
        id_vars="date",
        value_vars=["price_index", "income_index"],
        var_name="Series",
        value_name="Index (2012=100)",
    )
    fig = px.line(
        long,
        x="date",
        y="Index (2012=100)",
        color="Series",
        title="Composite Price vs Income (Indexed to 2012 = 100)",
    )
    fig.update_layout(legend_title_text="")
    fig.update_xaxes(title_text="")
    return fig

# ---------- CHAPTER 2: METRO DIVERGENCE ----------

def metro_pti_lines(df: pd.DataFrame, focus_year: int) -> go.Figure:
    """
    Plot metro-level PTI trends over time, with the top/bottom 7 metros
    (by PTI in the focus_year) highlighted.

    df can be ZIP-level; we aggregate to metro-by-date first.
    """

    # 1) Aggregate ZIPs → metro-level series
    df_metro = (
        df.groupby(["city_full", "year", "date"], as_index=False, observed=True)["price_to_income"]
        .mean()
        .dropna(subset=["price_to_income"])
    )

    # 2) Compute snapshot for the focus year (metro-level PTI)
    snapshot = (
        df_metro[df_metro["year"] == focus_year]
        .groupby("city_full", as_index=False, observed=True)["price_to_income"]
        .mean()
        .dropna(subset=["price_to_income"])
    )

    top = snapshot.sort_values("price_to_income", ascending=False).head(7)["city_full"]
    bottom = snapshot.sort_values("price_to_income", ascending=True).head(7)["city_full"]

    def label_group(city: str) -> str:
        if city in top.values:
            return "Top 7 (Least Affordable)"
        if city in bottom.values:
            return "Bottom 7 (Most Affordable)"
        return "Other"

    df_plot = df_metro.copy()
    df_plot["group"] = df_plot["city_full"].apply(label_group)

    color_map = {
        "Top 7 (Least Affordable)": "#B71C1C",
        "Bottom 7 (Most Affordable)": "#1E88E5",
        "Other": "#B0BEC5",
    }

    fig = px.line(
        df_plot,
        x="date",
        y="price_to_income",
        line_group="city_full",
        color="group",
        color_discrete_map=color_map,
        labels={"price_to_income": "PTI", "date": "Date"},
        title=f"Metro Price-to-Income Trends (Top/Bottom 7 Highlighted for {focus_year})",
        hover_name="city_full",
    )
    fig.update_layout(legend_title_text="")
    fig.update_xaxes(title_text="")

    return fig



# ---------- CHAPTER 4: Affordability Bands ----------
def affordability_bands_with_us_ratio(counts: pd.DataFrame,
                                      comp: pd.DataFrame) -> go.Figure:
    """
    Stacked bars: # of metros in each Demographia band by year
    + Line: composite US PTI (right axis), similar to the Moody's chart.
    """
    # Ensure sorted by year and band
    counts_sorted = counts.sort_values(["year", "affordability_rating"])

    # Composite US PTI by year
    us_pti = (
        comp.groupby("year", as_index=False, observed=True)["composite_pti"]
        .mean()
        .rename(columns={"composite_pti": "us_pti"})
    )
    
    us_pti["band"] = us_pti["us_pti"].apply(classify_affordability)

    # Figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Compute total metros per year
    totals = counts.groupby("year")["n_metros"].sum()


    # Stacked bars for each affordability band
    for band in AFFORDABILITY_ORDER:
        sub = counts_sorted[counts_sorted["affordability_rating"] == band]
        if sub.empty:
            continue

        fig.add_bar(
            x=sub["year"],
            y=sub["n_metros"],
            name=band,
            marker_color=AFFORDABILITY_COLORS[band],
            opacity=0.95,
            secondary_y=False,
            customdata=np.column_stack([
                    sub["year"],
                    sub["n_metros"],
                    sub["year"].map(totals) 
                ]),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"              # year
                "Band: <b>" + band + "</b><br>"           # category
                "Metros in band: <b>%{customdata[1]}</b><br>"   # n_metros
                "Total metros: <b>%{customdata[2]}</b><extra></extra>" # stacked total
            )
        )

    # Line for US composite PTI
    fig.add_trace(
        go.Scatter(
            x=us_pti["year"],
            y=us_pti["us_pti"],
            mode="lines+markers",
            name="30-Metro Composite PTI (right scale)",
            line=dict(color="#0066FF", width=2),
            legendrank=100,
            # hover info for PTI line
            customdata=np.column_stack([us_pti["year"], us_pti["us_pti"], us_pti["band"]]),
            hovertemplate=(
                "<b>Year:</b> %{customdata[0]}<br>"
                "<b>Composite PTI:</b> %{customdata[1]:.2f}x<br>"
                "<b>Affordability:</b> %{customdata[2]}"
                "<extra></extra>"
            ),
        ),
        secondary_y=True,
    )

    
    # Demographia PTI thresholds on the US PTI (right) axis
    threshold_lines = [3.0, 4.0, 5.0]

    for t in threshold_lines:
        fig.add_hline(
            y=t,
            line_dash="dot",
            line_color="rgba(0,0,0,0.35)",
            line_width=1,
            row=1,
            col=1,
            secondary_y=True,  
        )

    # One legend entry representing all dotted PTI threshold lines
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="rgba(0,0,0,0.35)", width=1, dash="dot"),
            name="Affordability Threshold (PTI)",
            showlegend=True,
            hoverinfo="skip",   # no hover since it's symbolic
            legendrank=50
        )
    )


    # Layout & axes
    fig.update_layout(
        barmode="stack",
        title="Number of Metros by Affordability Band and 30-Metro Composite PTI",
        legend_title_text="Affordability Rating",
        
    )

    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(
        title_text="Number of Metros",
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="Composite Price-to-Income Ratio (PTI)",
        secondary_y=True,
        showgrid=False,
        range = [0,6]
    )
    fig.update_xaxes(title_text="", dtick=1)

    return fig

# def composite_pti_bands_chart(comp: pd.DataFrame) -> go.Figure:
#     """
#     Composite PTI with Demographia-colored bands in the background.
#     Light-theme only: labels/lines in black.
#     """
#     fig = go.Figure()

#     text_color = "black"
#     line_color = "black"

#     # 1. COLORED ZONES (background)
#     zones = [
#         (0.0, 3.0,  "Affordable",                "≤3.0: Affordable"),
#         (3.0, 4.0,  "Moderately Unaffordable",   "3.1–4.0: Moderately Unaffordable"),
#         (4.0, 5.0,  "Seriously Unaffordable",    "4.1–5.0: Seriously Unaffordable"),
#         (5.0, 8.9,  "Severely Unaffordable",     "5.1–8.9: Severely Unaffordable"),
#         (8.9, 20.0, "Impossibly Unaffordable",   "≥9.0: Impossibly Unaffordable"),
#     ]

#     for (y0, y1, category, _label_text) in zones:
#         fig.add_shape(
#             type="rect",
#             xref="paper", x0=0, x1=1,
#             yref="y", y0=y0, y1=y1,
#             fillcolor=AFFORDABILITY_COLORS[category],
#             opacity=0.50,
#             layer="below",
#             line_width=0,
#         )

#     # 2. THRESHOLD LINES
#     for t in [3.0, 4.0, 5.0, 8.9, 9.0]:
#         fig.add_hline(
#             y=t,
#             line_dash="dash",
#             line_color=line_color,
#             opacity=0.8,
#             layer="above",
#         )

#     # 3. LABELS ON RIGHT
#     label_positions = [
#         (2.7,  "≤3.0: Affordable"),
#         (3.5,  "3.1–4.0: Moderately Unaffordable"),
#         (4.5,  "4.1–5.0: Seriously Unaffordable"),
#         (6.8,  "5.1–8.9: Severely Unaffordable"),
#         (9.3,  "≥9.0: Impossibly Unaffordable"),
#     ]

#     for y, text in label_positions:
#         fig.add_annotation(
#             xref="paper", x=1.005,
#             y=y,
#             text=text,
#             showarrow=False,
#             font=dict(size=12, color=text_color),
#             xanchor="left",
#             yanchor="middle",
#         )

#     # 4. PTI LINE
#     fig.add_trace(go.Scatter(
#         x=comp["date"],
#         y=comp["composite_pti"],
#         mode="lines",
#         line=dict(color="#1976D2", width=3),
#         name="Composite PTI",
#     ))

#     # 5. Layout
#     fig.update_layout(
#         title="Composite Price-to-Income Ratio with Demographia Zones",
#         xaxis_title="Date",
#         yaxis_title="Price-to-Income (PTI)",
#         font=dict(color=text_color),
#         margin=dict(r=200)
#     )

#     ymax = max(12, float(comp["composite_pti"].max()) + 1.0, 10.0)
#     fig.update_yaxes(range=[0, ymax])

#     return fig



# ---------- CHAPTER 4: RENT BURDEN ----------

def composite_rent_to_income(summary: pd.DataFrame) -> go.Figure:
    comp = (
        summary.groupby("year", as_index=False, observed=True)["rent_to_income"]
        .mean()
        .rename(columns={"rent_to_income": "composite_rti"})
    )

    fig = px.line(
        comp,
        x="year",
        y="composite_rti",
        markers=True,
        labels={"composite_rti": "Rent-to-Income"},
        title="Composite Rent-to-Income Ratio (Average Across Metros)",
    )

    max_rti = float(comp["composite_rti"].max())
    fig.update_yaxes(range=[0, max_rti * 1.1])  # little headroom above max
    fig.update_xaxes(title_text="")
    return fig



# def metro_rent_to_income(df: pd.DataFrame, metro: str) -> go.Figure:
#     sub = df[df["city_full"] == metro].copy()
#     fig = px.line(
#         sub,
#         x="date",
#         y="rent_to_income",
#         markers=True,
#         labels={"rent_to_income": "Rent-to-Income", "date": "Date"},
#         title=f"Rent-to-Income Over Time – {metro}",
#     )
#     return fig


# def top_rent_burden(summary: pd.DataFrame, year_focus: int, n: int = 10) -> go.Figure:
#     sub = summary[summary["year"] == year_focus].dropna(subset=["rent_to_income"])
#     sub = sub.sort_values("rent_to_income", ascending=False).head(n)

#     fig = px.bar(
#         sub,
#         x="rent_to_income",
#         y="city_full",
#         orientation="h",
#         labels={"rent_to_income": "Rent-to-Income", "city_full": "Metro"},
#         title=f"Highest Rental Burden Metros in {year_focus}",
#     )
#     fig.update_layout(yaxis=dict(autorange="reversed"))
#     return fig


# ---------- CHAPTER 5: SNAPSHOT ----------

def metro_snapshot_bar(summary):
    """
    Build the horizontal bar chart for the latest year,
    colored by affordability rating.
    """
    year_latest = summary["year"].max()

    summary_latest = (
        summary[summary["year"] == year_latest]
        .dropna(subset=["price_to_income"])
        .copy()
    )

    summary_latest = summary_latest.sort_values("price_to_income", ascending=True)

    bottom1 = summary_latest.head(1)
    top1 = summary_latest.tail(1)

    import plotly.express as px
    import plotly.graph_objects as go

    fig = px.bar(
        summary_latest,
        x="price_to_income",
        y="city_full",
        orientation="h",
        color="affordability_rating",
        color_discrete_map= AFFORDABILITY_COLORS,
        labels={
            "price_to_income": "Price-to-Income Ratio (PTI)",
            "city_full": "Metro",
            "affordability_rating": "Affordability Rating",
        },
        title=f"Metro PTI Levels in {year_latest} (Colored by Affordability Rating)",
        custom_data=["affordability_rating"]
    )

    fig.update_layout(
        yaxis=dict(title=""),
        xaxis=dict(title="Price-to-Income Ratio (PTI)"),
        legend_title_text="Affordability Rating",
        bargap=0.25,
        height=max(700, 20 * len(summary_latest)),
    )

    fig.update_traces(
        hovertemplate=
            "<b>%{y}</b><br>"
            "PTI: %{x:.1f}x<br>"
            "Rating: %{customdata[0]}<extra></extra>"
    )

    for _, row in bottom1.iterrows():
        fig.add_annotation(
            x=row["price_to_income"],
            y=row["city_full"],
            xanchor="left",
            yanchor="middle",
            text=" Most Affordable",
            showarrow=False,
            font=dict(size=10),
        )

    for _, row in top1.iterrows():
        fig.add_annotation(
            x=row["price_to_income"],
            y=row["city_full"],
            xanchor="right",
            yanchor="middle",
            text=" Least Affordable",
            showarrow=False,
            font=dict(size=10, color="white"),
        )
        
    return fig