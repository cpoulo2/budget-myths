import pandas as pd
import streamlit as st
from ipyvizzu import Chart, Data, Config, Style, DisplayTarget
from streamlit.components.v1 import html
import ssl
import os

# Load data
@st.cache_data
def load_data():
    """Load IL income inequality dataset."""
    try:
        df = pd.read_csv(r"data_gdp.csv")
        return df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please ensure the CSV files are in the correct location.")
        return None
    
def main():    
    # Load data
    df = load_data()
    
    if df is None:
        return

    df['year_type'] = df['year'].astype(str)
    df['gdp_pct'] = df['gdp_pct']*100
    df['gdp_pct'] = df['gdp_pct'].round(2)
    df['gdp_pct_str'] = df['gdp_pct'].astype(str)+"%"
    df['gdp_label'] = df['gdp'].apply(lambda x: f"${x/1000000:.1f}T" if x >= 1000000 else f"${x/1000:.1f}B")
    df['gdp_label_total'] = df['total'].apply(lambda x: f"${x/1000000:.1f}T" if x >= 1000000 else f"${x/1000:.1f}B")
    df['gdp'] = df['gdp']*1000000
    df['total'] = df['total']*1000000
    
    df['gdp_label'] = df.apply(lambda row: 
        row['gdp_label'] if (row['year'] == 2005 or row['year'] == 2025)
        else "", axis=1)
    
    df['combined_label'] = df.apply(lambda row: 
        row['gdp_label'] + " (" + row['gdp_pct_str'] + ")" if (row['year'] == 2005 or row['year'] == 2025)
        else row['gdp_label'] if (row['year'] == 2005 or row['year'] == 2025)
        else "", axis=1)

    # Main app
    
    st.set_page_config(page_title="≠ growth", layout="centered")

    st.title("Illinois' economic capacity and who captures it?")
    st.markdown("""
A scarcity myth limits how the public imagines government budgets and how state and local leaders address deficits. This myth—the taken-for-granted belief that we simply don’t have enough to fund public jobs, goods, and services—obscures the true shape of our economy. It operates by omitting the full picture of what our society actually produces and who owns it.
When statistics and statements about “rising expenditures” or “cost pressures” are invoked, for instance, they’re rarely followed with the answer to the pivotal question: in relation to what?

Illinois' economy generates over a trillion dollars a year. It's the 6th largest state economy in the US and the economic powerhouse of the midwest (over $200 million larger than the next largest economy), but public debates almost never contextualize spending within this broader social capacity.
Raising the question of what we have opens the door to deeper questions of social justice: who owns that value, and who gets to decide how it's used?

""", unsafe_allow_html=True)

    st.subheader("""The Private Sector Captures Most of Illinois' Economic Growth""")
    st.markdown("""
    One way to understand Illinois' economic capacity is to look at gross domestic product (GDP). GDP measures the total value of all goods and services produced in Illinois and it allows us to compare across sectors of the economy.

    The chart below shows that Illinois' economy generated $1.2 trillion 2025. The private sector captured about 91% of that.
    """, unsafe_allow_html=True)

    # First chart section
    data1 = Data()
    data1.add_df(df, units={"gdp_pct_str": "%"})
    
    chart1 = Chart(display=DisplayTarget.MANUAL)
    chart1.animate(data1)

    # Show total GDP
    chart1.animate(
        Data.filter("record['year'] == 2025 && record['quarter'] == 'Q1'"),
        Config({
            "y": "gdp",
            "label": "gdp_label_total",
            "title": "GDP (2025 Q1)",
            "legend": None
        }),
        Style({
            "plot": {
                "yAxis": {"label": {"numberScale": "K, M, B, T"}}            
            }
        }),
        delay=1,
    )

    chart1.animate(
        Data.filter("record['type'] != 'Federal' && record['year'] == 2025 && record['quarter'] == 'Q1'"),
        Config({
            "y": ["gdp","type"],
            "label": "combined_label",
            "color":"type",
            "title": "Illinois' GDP (March 2025)",
            "legend": None
        }),
        Style({
            "plot": {
                "yAxis": {"label": {"numberScale": "K, M, B, T"}}
            }
        }),
        delay=1,
    )

    chart1.animate(
        Data.filter("record['type'] != 'Federal' && record['year'] == 2025 && record['quarter'] == 'Q1'"),
        Config({
            "y": "gdp",
            "x":"type",
            "label": "combined_label",
            "legend": None,
            "color":"type",
            "title": "Private vs State and Local Share of GDP (March 2025)",
        }),
        Style({
            "plot": {
                "yAxis": {"label": {"numberScale": "K, M, B, T"}}
            }
        }),
        delay=2,
    )
    
    # Render first chart
    html_content1 = chart1._repr_html_()
    # Use column layout to control container width explicitly
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        st.components.v1.html(html_content1, height=100%,width=100%, scrolling=False)

    # Add restart button at the end
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Restart Animation", key="restart_btn_1", type="primary"):
            st.rerun()

    st.subheader("""State and Local Governmental Expenditures are Making up a Decreasing Share of GDP""")
    st.markdown("""
    TEXT
    """, unsafe_allow_html=True)

    # Second chart section
    data2 = Data()
    data2.add_df(df, units={"gdp_pct_str": "%"})
    
    chart2 = Chart(display=DisplayTarget.MANUAL)
    chart2.animate(data2)

    for i,y in enumerate(range(2005, 2026,5)):  # Changed to 2026 to include 2025
       chart2.animate(
           Data.filter(f"(record['year'] >= 2005 && record['year'] <= {y}) && record['type'] != 'Federal' && record['quarter'] == 'Q1'"),
           Config({
               "x": ["year_type","type"],  # This creates side-by-side bars grouped by year and type
               "y": "gdp",
               "color": "type",
               "label": "gdp_label",
               "title": f"Private vs State and Local Share of GDP (2005-{y})",
               "legend": None
           }),
           x={"easing": "linear", "delay": 0},
           y={"delay": 0},
           show={"delay": 0},
           hide={"delay": 0},
           title={"duration": 0, "delay": 0},
           duration=1,
           delay=0.3,  # Faster animation for smoother progression
       )

    chart2.animate(
           Data.filter(f"(record['year'] == 2005 || record['year'] == 2025) && record['type'] != 'Federal' && record['quarter'] == 'Q1'"),
           Config({
               "x": ["year_type", "type"],  # This creates side-by-side bars grouped by year and type
               "y": "gdp_pct",
               "color": "type",
               "label": "combined_label",
               "title": f"Private vs State and Local Share of GDP (2005 and 2025)",
               "legend": None
           }),
           delay=.1,  # Faster animation for smoother progression
       )

    # Render second chart
    html_content2 = chart2._repr_html_()
    # Use column layout to control container width explicitly
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        st.components.v1.html(html_content2, height=500, scrolling=False)
    
        # Add restart button at the end
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Restart Animation", key="restart_btn_2", type="primary"):
            st.rerun()

if __name__ == "__main__":
    main()

