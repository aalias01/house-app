import streamlit as st

st.markdown("""
    ### ℹ️ About House & Browse
    House & Browse visualizes housing prices across 30 major U.S. metropolitan areas from 2012 to 2023. Using metrics such as median sale price and price-to-income ratio, the dashboard explores how affordability has changed across regions and time.

    ### 🧮 How Price-to-Income Ratio Works
    - Price-to-Income Ratio = **Median Sale Price ÷ Median Household Income**
    - Median Household Income = 2.54 * Median Income (2019 to 2023 Median U.S. household size = 2.54)
    - Price-to-Income Ratio is divided into 5 levels of affordability:
        - **0.0-3.0:** Affordable
        - **3.1-4.0:** Moderately Unaffordable
        - **4.1-5.0:** Seriously Unaffordable
        - **5.1-8.9:** Severely Unaffordable
        - **9.0+:** Impossibly Unaffordable
            
    *Affordability levels were provided by the Center for Demographics and Policy (See References section)*

            
    ### 📚 References
    #### Dataset
    shengkunwang. (2025). *HouseTS Dataset*. Kaggle. https://www.kaggle.com/datasets/shengkunwang/housets-dataset/data
    
    #### Price-to-Income Ratio Levels
    Cox, Wendell (2025). *Demographia International Housing Affordability, 2025 Edition*. Center for Demographics and Policy. https://www.chapman.edu/communication/_files/Demographia-International-Housing-Affordability-2025-Edition.pdf

    #### 2019 to 2023 Median U.S. Household Size
    U.S. Census Bureau. (2023). 2019—2023 ACS 5-Year Narrative Profile. Retrieved December 4, 2025, from https://www.census.gov/acs/www/data/data-tables-and-tools/narrative-profiles/2023/report.php?geotype=nation&usVal=us&utm
    """)
