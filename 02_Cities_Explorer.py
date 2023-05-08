import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt

TEXT1 = "The following interactive representation of cities' population, the PyDeck map enables users to analyze " \
        "population distribution, identify densely populated areas, compare cities based on population sizes, " \
        "and explore geographical trends in urbanization. It is a valuable tool for researchers, policymakers, " \
        "and anyone interested in understanding and visualizing population data at the city level."


def get_filters(df):
    # in this function we get filters that later reflects in the bar chart
    states_list = list(df['state_name'].unique())
    states_list.sort()
    state = st.sidebar.selectbox('Select a state', states_list)
    min_population = st.sidebar.slider(
        "Select minimum population size",
        0, 200000, step=5000
    )
    if st.sidebar.checkbox("Establish upper bound? (max: 500,000)"):
        max_population = st.sidebar.slider(
            "Select maximum population size",
            5000, 500000, value=500000, step=5000
        )
    else:
        max_population = None
    return state, min_population, max_population


def display_map(df):
    # used PyDeck documentation
    # Would like to bring attention to this function, for I put substantial efforts to create this pydeck map
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=df['lat'].mean(),
            longitude=df['lng'].mean(),
            zoom=7,
            pitch=50
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=df,
                get_position='[lng, lat]',
                opacity=0.3,
                auto_highlight=True,
                radius=3200,
                get_elevation_weight='population',
                elevations_scale=1,
                elevation_range=[0, 500000],
                pickable=True,
                extruded=True,
                coverage=1
            )
        ],
        tooltip={
            "html": "<b>Population:<b> {elevationValue}"
        }
    ))


def display_bar_chart(df, min_population, max_population):
    df = df[['city', 'population', 'density']]
    df = df.reset_index(drop=True)
    df = df[(df['population'] >= min_population)]
    if max_population is not None:
        df = df[(df['population'] >= min_population) & (df['population'] <= max_population)]
    df = df[:35]

    # used Altair documentation
    # also would like to bring attention here, I believe this chart looks incredibly good and informative
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('city', sort='-y'),
        y=alt.Y('population'),
        color=alt.Color('density', scale=alt.Scale(scheme='magma'), bin=alt.Bin(maxbins=20))
    ).properties(
        title='Top 35 Cities By Population',
        height=500
    )

    st.altair_chart(chart)


def display_pie_chart(df):
    # filter the DataFrame to create a Pie Chart
    # first, create a separate DataFrame that only contains top 5 cities by population
    df_top5 = df[:5]
    df_top5 = df_top5[['city', 'population']]
    df_top5 = df_top5.reset_index()

    # create a new DataFrame that contains population for the rest of the cities in the state
    df_the_rest = df[5:]
    total_population_for_the_rest = df_the_rest[['population']].sum()
    others_dict = {'city': ['Other'], 'population': total_population_for_the_rest}
    others_df = pd.DataFrame(others_dict).reset_index()

    # concatenate two DataFrames
    pie_chart_df = pd.concat([df_top5, others_df], ignore_index=True)

    # using Altair chart to create a pie chart, used documentation
    st.markdown('The following Pie Chart shows the population distribution')
    pie_chart = alt.Chart(pie_chart_df).mark_arc().encode(
        theta=alt.Theta(field='population', type='quantitative'),
        color=alt.Color(field='city', type='nominal')
    )
    st.altair_chart(pie_chart)


def main():
    # LOAD DATA
    df = pd.read_csv('pages/final_project_data/uscities.csv')

    # PAGE LAYOUT
    st.title('United States: Cities Explorer')
    st.caption('Data analytics and visualization by state')

    # GET FILTERS
    state, min_population, max_population = get_filters(df)
    df = df[['state_name', 'city', 'lat', 'lng', 'population', 'density']]
    if state:
        df = df[(df['state_name'] == state)]

    # DISPLAY MAP
    display_map(df)
    st.markdown(TEXT1)

    # DISPLAY CHARTS
    st.header("Let's Take a Deeper Look...")
    display_bar_chart(df, min_population, max_population)

    st.header("Any other insights?")
    display_pie_chart(df)


main()
