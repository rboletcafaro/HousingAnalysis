import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from data_pull import get_multi_year_data

# Fetch Census data for multiple years (EXCLUDING 2020)
years = [2015, 2016, 2017, 2018, 2019, 2021, 2022]
df = get_multi_year_data(years)

# Handle case where no data is fetched
if df.empty:
    raise ValueError("No valid Census data available. Check API or years.")

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the Dash app
app.layout = html.Div(children=[
    html.H1("US Census Data - State Population"),

    # Dropdown to select year for bar chart
    html.Label("Select Year:"),
    dcc.Dropdown(
        id="year-dropdown",
        options=[{"label": str(year), "value": year} for year in years],
        value=max(years),  # Default to latest available year
        clearable=False
    ),

    # Bar Chart
    dcc.Graph(id="population-bar-chart"),

    # Multi-select dropdown for state selection in the line chart
    html.Label("Select States:"),
    dcc.Dropdown(
        id="state-dropdown",
        options=[{"label": state, "value": state} for state in df["State"].unique()],
        multi=True,
        value=["California", "Texas"]  # Default selections
    ),

    # Line Chart
    dcc.Graph(id="population-time-series")
])

# Callback to update the bar chart based on selected year
@app.callback(
    Output("population-bar-chart", "figure"),
    Input("year-dropdown", "value")
)
def update_bar_chart(selected_year):
    filtered_df = df[df["Year"] == selected_year]

    # Sort data by population (largest to smallest)
    filtered_df = filtered_df.sort_values(by="Population", ascending=False)

    # Create the bar chart
    fig = px.bar(filtered_df, 
                 x="State", 
                 y="Population", 
                 title=f"State Population in {selected_year}",
                 labels={"Population": "Population", "State": "State"},
                 color="Population",
                 color_continuous_scale="blues")

    return fig

# Callback to update the line chart based on selected states
@app.callback(
    Output("population-time-series", "figure"),
    Input("state-dropdown", "value")
)
def update_line_chart(selected_states):
    filtered_df = df[df["State"].isin(selected_states)]
    fig = px.line(filtered_df, x="Year", y="Population", color="State",
                  title="Population Over Time by State",
                  labels={"Population": "Population", "Year": "Year"})
    return fig

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
