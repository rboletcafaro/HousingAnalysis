import requests
import pandas as pd

# Set up your Census API Key (replace with your actual key)
CENSUS_API_KEY = "f8663e5d08cc9e0a4e9098cffc25c5d58184ac50"
BASE_URL_TEMPLATE = "https://api.census.gov/data/{year}/acs/acs1"

# Define available years (EXCLUDING 2020)
VALID_YEARS = [2015, 2016, 2017, 2018, 2019, 2021, 2022]  # No 2020

# Function to fetch Census data for a given year
def get_census_data(year):
    url = BASE_URL_TEMPLATE.format(year=year)
    params = {
        "get": "NAME,B01003_001E",  # Fetch state names and total population
        "for": "state:*",
        "key": CENSUS_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])  # Convert JSON to DataFrame
        df.rename(columns={"B01003_001E": "Population", "NAME": "State"}, inplace=True)
        df["Population"] = df["Population"].astype(int)  # Convert to numeric
        df["Year"] = int(year)  # Add Year column
        return df
    else:
        print(f"Error fetching data for {year}: {response.status_code}")
        return None

# Function to pull data for multiple years
def get_multi_year_data(years):
    dfs = []
    for year in years:
        df = get_census_data(year)
        if df is not None:
            dfs.append(df)

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()  # Return empty DataFrame if no data

# If run directly, fetch and print data
if __name__ == "__main__":
    df = get_multi_year_data(VALID_YEARS)
    if not df.empty:
        print(df.head())
    else:
        print("No valid data fetched.")