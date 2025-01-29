import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import papermill as pm
import os

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("ACS Census Data Visualization"),
    
    dcc.Dropdown(
        id='state-dropdown',
        options=[
            {'label': 'North Carolina', 'value': 'NC'},
            {'label': 'California', 'value': 'CA'},
            {'label': 'Texas', 'value': 'TX'}
        ],
        placeholder="Select a State"
    ),
    
    dcc.Input(id='year-input', type='number', placeholder='Enter Year', value=2022),
    html.Button('Fetch Data', id='fetch-button', n_clicks=0),
    
    html.Div(id='output-container'),
    
    dcc.Graph(id='population-chart'),
    dcc.Graph(id='map-visualization')
])

@app.callback(
    [Output('output-container', 'children'),
     Output('population-chart', 'figure'),
     Output('map-visualization', 'figure')],
    [Input('fetch-button', 'n_clicks')],
    [dash.State('state-dropdown', 'value'), dash.State('year-input', 'value')]
)
def update_output(n_clicks, state, year):
    if not state or not year:
        return "Please select a state and enter a year", px.scatter(), px.choropleth()
    
    # Run Jupyter notebook to fetch data
    pm.execute_notebook(
        "fetch_acs_data.ipynb", "output.ipynb",
        parameters=dict(state=state, year=year)
    )
    
    # Load data
    df = pd.read_csv("acs_data.csv")
    
    # Create a population distribution bar chart
    fig_bar = px.bar(df, x='County', y='Population', title=f'Population Distribution in {state}, {year}')
    
    # Create a map visualization
    fig_map = px.choropleth(df, geojson="counties.json", locations="FIPS", color="Population",
                             title=f'Population Map of {state} in {year}',
                             scope="usa")
    
    return f"Data fetched for {state} in {year}", fig_bar, fig_map

if __name__ == '__main__':
    app.run_server(debug=True)
