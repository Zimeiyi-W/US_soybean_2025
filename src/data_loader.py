import pandas as pd
import numpy as np
import requests
import os
from dotenv import load_dotenv
import json

# --- CONFIGURATION ---
load_dotenv() # Load the variables from the .env file
CENSUS_API_KEY = os.getenv("CENSUS_API") # Got the key here: https://api.census.gov/data/key_signup.html
if CENSUS_API_KEY:
    print(f"Success! Key loaded: {CENSUS_API_KEY[:4]}...")
else:
    print("Error: API_KEY not found.")
AG_API_KEY = os.getenv("AG_API")
if AG_API_KEY:
    print(f"Success! Key loaded: {AG_API_KEY[:4]}...")
else:
    print("Error: AG_API key not found in environment variables.")

def load_election_data(filepath='2024_US_County_Level_Presidential_Results.csv'):
    """
    Loads the 2024 Election CSV.
    """
    print(f"Loading Election Data from {filepath}...")
    try:
        df = pd.read_csv(filepath)
        # Ensure FIPS is 5 digits (e.g., 1001 -> '01001')
        df['county_fips'] = df['county_fips'].astype(str).str.zfill(5)
        
        # Rename columns to match the standard
        df = df.rename(columns={
            'county_fips': 'fips',
            'per_dem': 'dem_share',
            'per_gop': 'rep_share'
        })
        return df[['fips', 'state_name', 'county_name', 'dem_share', 'rep_share', 'total_votes']]
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return None

def fetch_census_data(api_key):
    """
    Fetches 2023 ACS 5-Year Data for Income, Education, and Race.
    """

    print("Fetching real Census Data via API...")
    
    # Variables:
    # B19013_001E: Median Household Income
    # B15003_001E: Total Pop 25+
    # B15003_022E: Bachelor's Degree
    # B03002_003E: White (Non-Hispanic)
    # B03002_004E: Black (Non-Hispanic)
    # B03002_012E: Hispanic
    variables = "B19013_001E,B15003_001E,B15003_022E,B03002_003E,B03002_004E,B03002_012E"
    
    url = f"https://api.census.gov/data/2023/acs/acs5?get={variables}&for=county:*&key={api_key}"
    
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print(f"API Error: {r.text}")
            return None
            
        data = r.json()
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        df['fips'] = df['state'] + df['county']
        
        # Convert types
        cols_to_numeric = ['B19013_001E', 'B15003_001E', 'B15003_022E', 'B03002_003E', 'B03002_004E', 'B03002_012E']
        for col in cols_to_numeric:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Calculate Derived Metrics
        df['median_household_income'] = df['B19013_001E']
        df['pct_bachelors_degree'] = (df['B15003_022E'] / df['B15003_001E']) * 100
        
        # Determine Majority Race
        race_cols = {
            'B03002_003E': 'White',
            'B03002_004E': 'Black',
            'B03002_012E': 'Hispanic'
        }
        df['majority_race'] = df[list(race_cols.keys())].idxmax(axis=1).map(race_cols)
        
        return df[['fips', 'median_household_income', 'pct_bachelors_degree', 'majority_race']]
        
    except Exception as e:
        print(f"Failed to fetch Census data: {e}")
        return None


def fetch_soybean_data():
    """
    Fetches 2022 Census of Agriculture data for Soybean Production (in Bushels)
    by County from the USDA NASS Quick Stats API.
    """
    print("Fetching Soybean Data from USDA NASS API...")
    url = "http://quickstats.nass.usda.gov/api/api_GET/"

    # Parameters to filter
    params = {
        'key': AG_API_KEY,
        'source_desc': 'CENSUS',
        'sector_desc': 'CROPS',
        'group_desc': 'FIELD CROPS',
        'commodity_desc': 'SOYBEANS',
        'statisticcat_desc': 'PRODUCTION',
        'short_desc': 'SOYBEANS - PRODUCTION, MEASURED IN BU',
        'domain_desc': 'TOTAL',
        'agg_level_desc': 'COUNTY',
        'year': '2022'
    }

    try:
        r = requests.get(url, params=params)
        r.raise_for_status() # Check for HTTP errors

        # NASS returns data in a 'data' key within the JSON
        json_data = r.json()
        if 'data' not in json_data:
            print("No data found or API error.")
            return None
        
        df = pd.DataFrame(json_data['data'])

        # --- Data Cleaning ---
        
        # 1. Create FIPS Code: State ANSI + County ANSI
        df['fips'] = df['state_ansi'].astype(str).str.zfill(2) + \
                     df['county_ansi'].astype(str).str.zfill(3)
        # 2. Clean the 'Value' column
        # NASS returns numbers as strings with commas (e.g., "1,000")
        # NASS uses "(D)" for withheld data (privacy). We coerce these to NaN.
        df['soybean_bushels'] = pd.to_numeric(
            df['Value'].astype(str).str.replace(',', '', regex=False), 
            errors='coerce'
        )
        # 3. Filter columns and return
        final_df = df[['fips', 'soybean_bushels']].copy()

        print(f"Successfully loaded {len(final_df)} counties.")
        return final_df
    
    except Exception as e:
        print(f"Failed to fetch NASS data: {e}")
        return None
    
def get_merged_data():
    # 1. Load Real Election Data
    pol_df = load_election_data()
    if pol_df is None:
        print("CRITICAL: Election CSV missing. Cannot proceed.")
        return None
        
    # 2. Load Census (Real or Synthetic)
    demo_df = fetch_census_data(CENSUS_API_KEY)
    pol_df = pol_df.merge(demo_df, on='fips', how='left')
    
    # 3. Load Soybeans
    ag_df = fetch_soybean_data()
    
    
    pol_df = pol_df.merge(ag_df, on='fips', how='left')
    pol_df['soybean_bushels'] = pol_df['soybean_bushels'].fillna(0)

    return pol_df