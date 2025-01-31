import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import requests

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

def fetch_acs_data(state, year):
    base_url = "https://api.census.gov/data/{}/acs/acs5".format(year)
    variables = "B01003_001E"  # Total population
    params = {
        "get": f"NAME,{variables}",
        "for": "county:*",
        "in": f"state:{state}",
        "key": "f8663e5d08cc9e0a4e9098cffc25c5d58184ac50"
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])
        df.rename(columns={"B01003_001E": "Population", "NAME": "County"}, inplace=True)
        df["Population"] = df["Population"].astype(int)
        return df
    else:
        return None

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
    
    df = fetch_acs_data(state, year)
    if df is None:
        return "Error fetching data from ACS API", px.scatter(), px.choropleth()
    
    # Create a population distribution bar chart
    fig_bar = px.bar(df, x='County', y='Population', title=f'Population Distribution in {state}, {year}')
    
    # Create a map visualization
    fig_map = px.choropleth(df, geojson="counties.json", locations="county", color="Population",
                             title=f'Population Map of {state} in {year}',
                             scope="usa")
    
    return f"Data fetched for {state} in {year}", fig_bar, fig_map

if __name__ == '__main__':
    app.run_server(debug=True)
