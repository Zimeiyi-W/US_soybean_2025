from src.data_loader import get_merged_data
from src.analysis import categorize_political_stance, categorize_economic_status, analyze_allocation
from src.visualization import plot_political_allocation, plot_economic_scatter, plot_demographic_dist
from src.advanced_maps import generate_advanced_maps

def main():
    # 1. Acquire Data
    df = get_merged_data()
    
    if df is None:
        return

    # 2. Process Data
    print("Processing data...")
    df = categorize_political_stance(df)
    df = categorize_economic_status(df)
    
    # 3. Analyze
    print("Analyzing allocation...")
    pol_agg, econ_agg, race_agg = analyze_allocation(df)
    
    # 4. Visualize
    print("Generating visuals...")
    plot_political_allocation(pol_agg)
    plot_economic_scatter(df)
    plot_demographic_dist(race_agg)
    
    # 5. Generate Map
    print("Generating Advanced Maps...")
    try:
        generate_advanced_maps(df)
    except Exception as e:
        print(f"Map Error: {e}")
    
    print("Analysis Complete. Check output images.")

if __name__ == "__main__":
    main()