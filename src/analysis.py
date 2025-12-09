import pandas as pd
import numpy as np

def categorize_political_stance(df):
    """
    Categorizes counties based on vote share.
    Assumption: > 50% Dem vote = Democratic Leaning.
    """
    df['political_lean'] = np.where(df['dem_share'] > 0.5, 'Democratic', 'Republican')
    return df

def categorize_economic_status(df):
    """
    Segments counties into Income Quartiles.
    """
    df = df.dropna(subset=['median_household_income']).copy()
    try:
        df['income_quartile'] = pd.qcut(df['median_household_income'], 4, labels=['Low Income', 'Lower-Mid', 'Upper-Mid', 'High Income'])
    except ValueError:
        print("Warning: Not enough unique income values to calculate quartiles.")
        df['income_quartile'] = 'Unknown'    
    
    return df

def analyze_allocation(df):
    """
    Aggregates soybean production by different categories.
    """
    # 1. By Politics
    pol_agg = df.groupby('political_lean')['soybean_bushels'].sum().reset_index()
    total_soy = pol_agg['soybean_bushels'].sum()
    pol_agg['share'] = pol_agg['soybean_bushels'] / total_soy if total_soy > 0 else 0    

    # 2. By Economic Status
    econ_agg = df.groupby('income_quartile')['soybean_bushels'].sum().reset_index()
    
    # 3. By Race (Majority group in county)
    race_agg = df.groupby('majority_race')['soybean_bushels'].sum().reset_index()
    
    return pol_agg, econ_agg, race_agg