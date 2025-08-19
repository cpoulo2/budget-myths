import pandas as pd
import streamlit as st
from ipyvizzu import Chart, Data, Config, Style, DisplayTarget
from streamlit.components.v1 import html
import ssl
import os

st.set_page_config(page_title="≠ growth", layout="centered")

# Load data
@st.cache_data
def load_data():
    """Load IL income inequality dataset."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "data_gdp.csv")
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please ensure the CSV files are in the correct location.")
        return None
    
def main():    
    # Load data
    df = load_data()
    
    if df is None:
        return

    tab1, tab2, tab3 = st.tabs(["Scarcity Myth", "Tax Burden Myth","Glossary"])

    with tab1:

        # Format BEA data

        df['year_type'] = df['year'].astype(str)
        df['gdp_pct_100'] = df['gdp_pct']*100
        df['gdp_pct_100'] = df['gdp_pct_100'].round(2)
        df['gdp_pct_str'] = df['gdp_pct_100'].astype(str)+"%"
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

        # create a data frame for state and local at 2005 gdp share 0.084394675

        state_and_local = df.copy()
        state_and_local = state_and_local[(state_and_local['type'] == 'State and Local Governments') & (state_and_local['quarter']=="Q1")]
        state_and_local = state_and_local[['year','year_type','gdp']]
        state_and_local['type'] = "GDP"
        state_and_local_2005 = df.copy()
        state_and_local_2005 = state_and_local_2005[(state_and_local_2005['type'] == 'Private Sector') & (state_and_local_2005['quarter']=="Q1")]
        state_and_local_2005 = state_and_local_2005[['year','year_type','total']]
        state_and_local_2005['gdp'] = state_and_local_2005['total'] * 0.084394675
        state_and_local_2005 = state_and_local_2005[['year','year_type','gdp']]
        state_and_local_2005['type'] = "GDP at 2005 level"

        # concatenate state_and_local and state_and_local_2005

        df2 = pd.concat([state_and_local,state_and_local_2005])

        df2['gdp_label'] = df2['gdp'].apply(lambda x: f"${x/1000000000000:.1f}T" if x >= 1000000000000 else f"${x/1000000000:.1f}B")
        df2['gdp_label'] = df2.apply(lambda row: 
                row['gdp_label'] if (row['year'] == 2005 or row['year'] == 2025)
                else "", axis=1)
        # Main app

        st.title("Illinois' economic resources and who captures them")
        st.markdown("""In this section we will:

- Introduce the scarcity myth;
- Illustrate why it's not true using government data;
- Explore the distribution of economic resources in Illinois; and
- Understand the implications of the scarcity myth""", unsafe_allow_html=True)

        st.subheader("""The Scarcity Myth""")
        st.markdown("""
A <b><mark style='background-color: yellow'>scarcity myth</mark></b> limits how the public imagines government budgets and how state and local leaders address deficits. <b><mark style='background-color: yellow'>This refers to the taken-for-granted belief that we simply don’t have the resources to fund public jobs, goods, and services. It operates by omitting the full picture of what our society produces and who owns it.</mark></b>

For example, when budgets are discussed publicly the media, policy makers, and government officials often cite “rising expenditures” or “cost pressures” without answering an essential question: in relation to what?

In March of 2025, Illinois' economy generated over a trillion dollars and it nearly doubled in size over the past twenty years. Moreover, Illinois is recognized as the economic powerhouse of the Midwest. But public debates almost never provide this context when discussing the budget and budget deficits. 

Raising the question of what we have opens the door to questions of social justice: who owns that value, and who gets to decide how it's used?

""", unsafe_allow_html=True)

        st.subheader("""The Private Sector Captures \\$9 out of every \\$10 of Illinois' economic output""")
        st.markdown("""
One way to understand our resources (what we have) is by using a statistic called the <b><mark style='background-color: yellow'>gross domestic product</mark></b> (GDP). <b><mark style='background-color: yellow'>It measures the total value of all goods and services produced in any given boundary</mark></b>—in this case the state of Illinois.

In March of 2025, Illinois’ economy generated $1.2 trillion.

We can break this down to understand which industries are capturing this value. **The private sector captured 91% of Illinois’ economic resources. State and local governments expenditures accounted for less than 8%.**

        """, unsafe_allow_html=True)

        # centering all buttons
        st.markdown(
    """
    <style>
    div.stButton > button {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
        )

            # Add restart button at the end
        st.button("Show animation", key="restart_btn_1", type="primary")

        # First chart section
        data1 = Data()
        data1.add_df(df, units={"gdp_pct_str": "%"})

        # Create chart with responsive settings
        chart1 = Chart(width="100%", height="400px", display=DisplayTarget.MANUAL)
        chart1.animate(data1)

        # Show total GDP
        chart1.animate(
            Data.filter("record['year'] == 2025 && record['quarter'] == 'Q1'"),
            Config({
                "y": "gdp",
                "label": "gdp_label_total",
                "title": "Illinois' GDP (March 2025)",
                "legend": None
            }),
            Style({
                "backgroundColor": "#ffffff00",
                "plot": {
                    "yAxis": {
                        "color": "#CCCCCCFF",
                        "label": {"numberScale": "K, M, B, T"},
                        "title": {"color": "#ffffff00"},
                        "interlacing": {"color": "#E6E6FA"}
                    }
                }
            }),
            delay=1,
        )

        chart1.animate(
            Data.filter("record['type'] != 'Federal Government' && record['year'] == 2025 && record['quarter'] == 'Q1'"),
            Config({
                "y": ["gdp","type"],
                "label": "type",
                "color":"type",
                "title": "Illinois' GDP (March 2025)",
                "legend": None
            }),
            Style({
                "backgroundColor": "#ffffff00",
                "plot": {
                    "yAxis": {
                        "color": "#CCCCCCFF",
                        "label": {"numberScale": "K, M, B, T"},
                        "title": {"color": "#ffffff00"},
                        "interlacing": {"color": "#E6E6FA"}
                    }
                }
            }),
            delay=1,
        )

        chart1.animate(
            Data.filter("record['type'] != 'Federal Government' && record['year'] == 2025 && record['quarter'] == 'Q1'"),
            Config({
                "y": "gdp",
                "x":"type",
                "label": "combined_label",
                "legend": None,
                "color":"type",
                "title": "Illinois GDP (March 2025)",
            }),
            Style({
                "backgroundColor": "#ffffff00",
                "plot": {
                    "yAxis": {
                        "color": "#CCCCCCFF",
                        "label": {"numberScale": "K, M, B, T"},
                        "title": {"color": "#ffffff00"},
                        "interlacing": {"color": "#E6E6FA"}
                    }
                }
            }),
            delay=2,
        )

        # Render first chart
        html_content1 = chart1._repr_html_()
        st.components.v1.html(html_content1, width=700, height=450, scrolling=False)

        st.subheader("""Illinois' economy is growing, but the state and local government share is shrinking""")
        st.markdown("""
        Illinois' economy doubled in size over the past 20 years. Large increases occurred post-Great Recession and again during and after the COVID pandic. 

        The scarcity myth often implies that public sector expenditures are 'out of control'. However, the data suggests that this is not the case. **State and local governmental expenditures have accounted for a decreasing share of GDP over the last two decades.** 
        """, unsafe_allow_html=True)

        # Second chart section
        data2 = Data()
        data2.add_df(df, units={"gdp_pct_str": "%"})

        # start animation button
        st.button("Show Animation", key="restart_btn_2", type="primary")

        # Create chart with responsive settings
        chart2 = Chart(width="100%", height="400px", display=DisplayTarget.MANUAL)
        chart2.animate(data2)

        for i,y in enumerate(range(2005, 2026,5)):  # Changed to 2026 to include 2025
           chart2.animate(
               Data.filter(f"(record['year'] >= 2005 && record['year'] <= {y}) && record['type'] != 'Federal Government' && record['quarter'] == 'Q1'"),
               Config({
                   "x": ["year_type","type"],  # This creates side-by-side bars grouped by year and type
                   "y": "gdp",
                   "color": "type",
                   "label": "gdp_label",
                   "title": f"Illinois' GDP (2005-{y})",
                   "subtitle": f"Private Industry vs State and Local Government",
                   "legend": None
               }),
               Style({
                "backgroundColor": "#ffffff00",
                "plot": {
                    "yAxis": {
                        "color": "#CCCCCCFF",
                        "label": {"numberScale": "K, M, B, T"},
                        "title": {"color": "#ffffff00"},
                        "interlacing": {"color": "#E6E6FA"}
                    }
                }
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
               Data.filter(f"(record['year'] == 2005 || record['year'] == 2025) && record['type'] != 'Federal Government' && record['type'] != 'Private Industry' && record['quarter'] == 'Q1'"),
               Config({
                   "x": ["year_type", "type"],  # This creates side-by-side bars grouped by year and type
                   "y": "gdp_pct_100",
                   "color": "type",
                   "label": ["gdp_pct_str","type"],
                   "title": f"Illinois' GDP (2005 and 2025)",
                   "subtitle": f"State and Local Governmental Share",
                   "legend": None
               }),
               Style({
                "backgroundColor": "#ffffff00",
                "plot": {
                    "yAxis": {
                        "color": "#CCCCCCFF",
                        "label": {"numberScale": "K, M, B, T"},
                        "title": {"color": "#ffffff00"},
                        "interlacing": {"color": "#E6E6FA"}
                    }
                }
            }),
               delay=.1,  # Faster animation for smoother progression
           )

        # Render second chart
        html_content2 = chart2._repr_html_()
        st.components.v1.html(html_content2, width=700, height=450, scrolling=False)

        # Show what would happen if state and local share stayed at 2005 levels

        st.subheader("""If the 2005 share of the GDP held, the state and local governments would have $12.2B more to spend.""")
        st.markdown("""

        A 1 percent different when dealing with a trillion dollar economy amounts to a large sum of money. Had the 2005 share of GDP held, **state and local governments' would have had over \\$12 billion more to spend in March of 2025.** That's enough to cover Trump's cuts to medicaid and the transit cliff while still having over $2 billion to spend.

        This hypothetical points to an important consideration: the resources to fund public jobs and programs exist, its a matter how these resources are distributed or more importantly **how  that value is taxed and used by the public sector**. In the absence of tax revenue, budget cuts and borrowing from those with money *appears* to be the only feasible solution to our budget deficits. We will cover the topic of taxation in the following section. 

        """, unsafe_allow_html=True)

        data3 = Data()
        data3.add_df(df2)

        # start animation button
        st.button("Show Animation", key="restart_btn_3", type="primary")

        # Create chart with responsive settings
        chart3 = Chart(width="100%", height="400px", display=DisplayTarget.MANUAL)
        chart3.animate(data3)

        for i,y in enumerate(range(2005, 2026,5)):  # Changed to 2026 to include 2025
           chart3.animate(
               Data.filter(f"(record['year'] >= 2005 && record['year'] <= {y})"),
               Config({
                   "x": ["year_type","type"],  # This creates side-by-side bars grouped by year and type
                   "y": "gdp",
                   "color": "type",
                   "label": "gdp_label",
                   "title": f"State and Local GDP (2005-{y})",
                   "subtitle": f"Actual vs 2005 Share",
                   "legend": None
               }),
               Style({
                "backgroundColor": "#ffffff00",
                "plot": {
                    "yAxis": {
                        "color": "#CCCCCCFF",
                        "label": {"numberScale": "K, M, B, T"},
                        "title": {"color": "#ffffff00"},
                        "interlacing": {"color": "#E6E6FA"}
                    }
                }
            }),
               x={"easing": "linear", "delay": 0},
               y={"delay": 0},
               show={"delay": 0},
               hide={"delay": 0},
               title={"duration": 0, "delay": 0},
               duration=1,
               delay=0.3,  # Faster animation for smoother progression
           )

        chart3.animate(
               Data.filter(f"(record['year'] == 2025)"),
               Config({
                   "x": ["year_type", "type"],  # This creates side-by-side bars grouped by year and type
                   "y": "gdp",
                   "color": "type",
                   "label": ["gdp_label",'type'],
                   "title": f"State and Local GDP (2025)",
                   "subtitle": f"Actual vs 2005 Share",
                   "legend": None
               }),
               Style({
                "backgroundColor": "#ffffff00",
                "plot": {
                    "yAxis": {
                        "color": "#CCCCCCFF",
                        "label": {"numberScale": "K, M, B, T"},
                        "title": {"color": "#ffffff00"},
                        "interlacing": {"color": "#E6E6FA"}
                    }
                }
            }),
               delay=.1,  # Faster animation for smoother progression
           )

        # Render second chart
        html_content3 = chart3._repr_html_()
        st.components.v1.html(html_content3, width=700, height=450, scrolling=False)

        st.subheader("""Take Aways""")
        st.markdown("""

        - Scaricty is a myth used to justify cuts to the public sector or borrowing from the private sector to resolve budget deficits, which divert more tax dollars to interest and other forms of finance capital.
        - There are enough economic resources to pay for and expand public sector jobs and programs.
        - The private sector captures 91% of Illinois' economic resources. These resources have been increasingly privately owned over the past two decades while the state and local governments are losing their share.
        - Had the 2005 share of GDP held, state and local governments' would have had over \\$12 billion more to spend in March of 2025.

        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

