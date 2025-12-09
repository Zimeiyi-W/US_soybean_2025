import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np

# Politics color scale
POLITICAL_CMAPS = {
    'Republican': 'Reds',
    'Democratic': 'Blues'
}

def get_color_political(row, max_soy):
    """
    Returns a color based on Political Stance (Hue) and Soybean Output (Saturation).
    """
    if row['soybean_bushels'] == 0 or pd.isna(row['soybean_bushels']):
        return "#f0f0f0fe" # Grey for no data
    
    # Normalize soybean production (0 to 1) for intensity
    # Use a log scale because ag data has huge outliers
    # The log1p function is useful when dealing with very small number
    intensity = np.log1p(row['soybean_bushels']) / np.log1p(max_soy)
    
    # Ensure valid range
    intensity = max(0.1, min(intensity, 1.0)) 
    
    base_cmap = plt.get_cmap(POLITICAL_CMAPS.get(row['political_lean'], 'Greys'))
    
    # Get color from the map at the specific intensity
    return mcolors.to_hex(base_cmap(intensity))


def get_color_race(row, max_soy):
    """
    Hue = Race, Saturation = Soybeans
    """
    if row['soybean_bushels'] == 0 or pd.isna(row['soybean_bushels']):
        return '#f0f0f0'
        
    intensity = np.log1p(row['soybean_bushels']) / np.log1p(max_soy)
    intensity = max(0.2, min(intensity, 1.0))
    
    # Define hues for races
    race_cmaps = {
        'White': 'Greens',
        'Black': 'Purples',
        'Hispanic': 'Oranges'
    }
    
    cmap_name = race_cmaps.get(row['majority_race'], 'Greys')
    return mcolors.to_hex(plt.get_cmap(cmap_name)(intensity))

def load_us_counties_shapefile():
    """
    Downloads a lightweight (20m resolution) US County shapefile directly from the US Census Bureau.
    This allows the code to run without manual file downloads.
    """
    print("Fetching US County shapefiles (this may take a moment)...")
    url = "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_20m.zip"
    gdf = gpd.read_file(url)
    
    # Create a 'fips' column to match our data (State FIPS + County FIPS)
    gdf['fips'] = gdf['STATEFP'] + gdf['COUNTYFP']
    return gdf

def generate_advanced_maps(df):
    gdf = load_us_counties_shapefile()

    # Merge data and a bit cleanup
    # We do a 'left' merge on the shapefile to keep the map shape even if data is missing
    map_data = gdf.merge(df, on='fips', how='left')
    # Convert 0 values to NaN (Missing) so that they can be removed from the greens color scale
    map_data['soybean_bushels'] = map_data['soybean_bushels'].replace(0, np.nan)

    
    # Filter Lower 48 for better view
    map_data = map_data[~map_data['STATEFP'].isin(['02', '15', '72'])]
    
    # Global max for scaling
    max_soy = map_data['soybean_bushels'].max()


    # --- MAP 1: Soy Output ---
    print("Generating Soybean Output Map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    custom_greens = ['#c7e9c0', '#74c476', '#41ab5d', '#238b45', '#005a32']
    my_cmap = mcolors.ListedColormap(custom_greens)

    # Plotting the data
    map_data.plot(column='soybean_bushels', 
                  ax=ax, 
                  legend=True,
                  cmap=my_cmap,
                  scheme='quantiles', # Helps visualize data with outliers
                  k=5, # Number of color buckets
                  legend_kwds={'loc': 'lower right', 'title': 'Bushels', 'fmt': '{:.0f}'},
                  missing_kwds={
                      'color': 'lightgrey',
                      "edgecolor": "white",
                      "hatch": "///",
                      "label": "No Production"} # Deal with NaN
                )
    # Formatting
    plt.title('US Soybean Production Intensity by County', fontsize=20, fontweight='bold')
    ax.axis('off') # Turn off lat/long axis numbers
    
    plt.tight_layout()
    plt.savefig('output_soybean_map.png')
    print("Saved: output_soybean_map.png")


    # --- MAP 2: Politics + Soy ---
    print("Generating Politics Map...")
    map_data['color_pol'] = map_data.apply(lambda x: get_color_political(x, max_soy), axis=1)
    
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    map_data.plot(color=map_data['color_pol'], ax=ax)
    plt.title('Soybean Output vs Political Landscape\n(Darker = More Soybeans, Red=Rep, Blue=Dem)', fontsize=16)
    ax.axis('off')
    plt.savefig('map_politics_soy.png')

    # --- MAP 3: Race + Soy ---
    print("Generating Race Map...")
    map_data['color_race'] = map_data.apply(lambda x: get_color_race(x, max_soy), axis=1)
    
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    map_data.plot(color=map_data['color_race'], ax=ax)
    
    # Legend
    plt.text(0.1, 0.1, "Green = White Majority\nPurple = Black Majority\nOrange = Hispanic Majority", 
             transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.8))
             
    plt.title('Soybean Output by Demographic Majority', fontsize=16)
    ax.axis('off')
    plt.savefig('map_race_soy.png')

    
    print("All Maps Generated.")