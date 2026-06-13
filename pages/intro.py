import streamlit as st

# Logo and Hero section
st.markdown("""
<style>
.hero-section {
    margin-bottom: 1rem;
}
.logo-header {
    display: flex;
    align-items: center;
    margin-bottom: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
}
.logo-left {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.logo-icon-wrapper {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}
.logo-icon {
    font-size: 2rem;
}
.logo-text {
    display: flex;
    flex-direction: column;
}
.logo-main {
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}
.logo-tagline {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 0.2rem;
}
.main-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.5rem;
    line-height: 1.4;
}
.main-subtitle {
    font-size: 0.95rem;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

# Header with Logo
st.markdown("""
<div class="hero-section">
    <div class="logo-header">
        <div class="logo-left">
            <div class="logo-icon-wrapper">
                <div class="logo-icon">🏠</div>
            </div>
            <div class="logo-text">
                <div class="logo-main">House & Browse</div>
                <div class="logo-tagline">Housing Affordability Dashboard</div>
            </div>
        </div>
    </div>
    <div>
        <div class="main-title">Explore U.S. Housing Affordability Across 30 Major Metro Areas</div>
        <div class="main-subtitle">Interactive visualizations from 2012-2023</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Main navigation cards - primary entry points
st.markdown("### 🚀 Get Started")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="padding: 1.5rem; border: 2px solid #e5e7eb; border-radius: 12px; text-align: center; height: 100%; cursor: pointer; transition: all 0.3s ease;" 
         onmouseover="this.style.borderColor='#3b82f6'; this.style.boxShadow='0 4px 12px rgba(59, 130, 246, 0.2)';" 
         onmouseout="this.style.borderColor='#e5e7eb'; this.style.boxShadow='none';">
        <h2 style="margin: 0 0 0.5rem 0; font-size: 2.5rem;">🗺️</h2>
        <h4 style="margin: 0 0 0.5rem 0;">Interactive Map Explorer</h4>
        <p style="color: #6b7280; margin: 0 0 1rem 0;">Explore metro areas and drill down to ZIP codes</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Explore Map →", key="map_btn", use_container_width=True, type="primary"):
        st.switch_page("pages/map_explorer.py")

with col2:
    st.markdown("""
    <div style="padding: 1.5rem; border: 2px solid #e5e7eb; border-radius: 12px; text-align: center; height: 100%; cursor: pointer; transition: all 0.3s ease;" 
         onmouseover="this.style.borderColor='#3b82f6'; this.style.boxShadow='0 4px 12px rgba(59, 130, 246, 0.2)';" 
         onmouseout="this.style.borderColor='#e5e7eb'; this.style.boxShadow='none';">
        <h2 style="margin: 0 0 0.5rem 0; font-size: 2.5rem;">📊</h2>
        <h4 style="margin: 0 0 0.5rem 0;">Time Series Comparison</h4>
        <p style="color: #6b7280; margin: 0 0 1rem 0;">Compare affordability trends over time</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Trends →", key="trends_btn", use_container_width=True, type="primary"):
        st.switch_page("pages/trend_comparison.py")

with col3:
    st.markdown("""
    <div style="padding: 1.5rem; border: 2px solid #e5e7eb; border-radius: 12px; text-align: center; height: 100%; cursor: pointer; transition: all 0.3s ease;" 
         onmouseover="this.style.borderColor='#3b82f6'; this.style.boxShadow='0 4px 12px rgba(59, 130, 246, 0.2)';" 
         onmouseout="this.style.borderColor='#e5e7eb'; this.style.boxShadow='none';">
        <h2 style="margin: 0 0 0.5rem 0; font-size: 2.5rem;">💰</h2>
        <h4 style="margin: 0 0 0.5rem 0;">Price Affordability Finder</h4>
        <p style="color: #6b7280; margin: 0 0 1rem 0;">Find affordable areas based on your income</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Find Areas →", key="finder_btn", use_container_width=True, type="primary"):
        st.switch_page("pages/affordability_finder.py")

st.markdown("---")

# Optional information section - all optional content in one place
st.markdown("### 📖 Learn More (Additional)")
st.caption("All additional content is organized here for easy access")

# Use tabs to organize optional content
tab1, tab2, tab3 = st.tabs(["🔑 Key Insights", "ℹ️ About This Dashboard", "📚 References"])

with tab1:
    st.markdown("""
    Explore the housing affordability story through our narrative visualization.
    """)
    if st.button("🔑 View Key Insights", use_container_width=True, type="secondary"):
        st.switch_page("pages/story.py")

with tab2:
    st.markdown("""
    **House & Browse** visualizes housing prices across 30 major U.S. metropolitan areas from 2012 to 2023. 
    Using metrics such as median sale price and price-to-income ratio, this app provides interactive tools 
    to explore affordability trends and identify which areas are attainable based on your income.
    
    ### 🧮 Price-to-Income Ratio (PTI)
    - **Formula**: Median Sale Price ÷ Median Household Income
    - **Household Income**: 2.54 × Per Capita Income (based on 2019-2023 U.S. median household size)
    - **Affordability Levels**:
        - **0.0-3.0:** 🟢 Affordable
        - **3.1-4.0:** 🟡 Moderately Unaffordable
        - **4.1-5.0:** 🟠 Seriously Unaffordable
        - **5.1-8.9:** 🔴 Severely Unaffordable
        - **9.0+:** ⚫ Impossibly Unaffordable
    
    ### 💰 Median Sale Price
    - **Definition**: The median price of houses sold during a specific time period
    
    *Affordability levels from the Center for Demographics and Policy*
    """)

with tab3:
    st.markdown("""
    **Dataset**: shengkunwang. (2025). *HouseTS Dataset*. Kaggle. 
    https://www.kaggle.com/datasets/shengkunwang/housets-dataset/data
    
    **Price-to-Income Ratio Levels**: Cox, Wendell (2025). *Demographia International Housing Affordability, 2025 Edition*. 
    Center for Demographics and Policy. 
    https://www.chapman.edu/communication/_files/Demographia-International-Housing-Affordability-2025-Edition.pdf
    
    **Household Size**: U.S. Census Bureau. (2023). 2019—2023 ACS 5-Year Narrative Profile.
    
    **Part Time College Student Annual Salary**: Part Time College Student Annual Salary ($36,824 Avg | Sep 2020). (n.d.). ZipRecruiter. 
    https://www.ziprecruiter.com/Salaries/Part-Time-College-Student-Salary
    
    **Young Professionals Salary**: Young Professionals. (2025). ZipRecruiter. 
    https://www.ziprecruiter.com/Salaries/Young-Professionals-Salary
    
    **Median Income Table**: Office, U. E. (2025). U.S. Trustee Program/Dept. of Justice. Justice.gov. 
    https://www.justice.gov/ust/eo/bapcpa/20250401/bci_data/median_income_table.htm
    
    **Cartographic Boundary Files**: Cartographic Boundary Files - Shapefile. (2021). The United States Census Bureau. 
    https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
    """)

