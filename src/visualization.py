import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
# This is used to create some basic visuals like bar charts and scatterplots.

# Set professional style
sns.set_theme(style="whitegrid")
COLOR_PALETTE = {'Democratic': '#00AEF3', 'Republican': '#E81B23'}

def plot_political_allocation(pol_agg):
    plt.figure(figsize=(10, 6))
    
    ax = sns.barplot(x='political_lean', y='soybean_bushels', data=pol_agg, palette=COLOR_PALETTE)
    
    # Formatting
    plt.title('US Soybean Production Allocation by Political Leaning (2020 Vote)', fontsize=16, fontweight='bold')
    plt.ylabel('Total Bushels Produced', fontsize=12)
    plt.xlabel('County Majority Vote', fontsize=12)
    
    # Format Y-axis to Billions/Millions
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x/1e6:,.0f}M'))
    
    # Add percentage labels
    for p, share in zip(ax.patches, pol_agg['share']):
        height = p.get_height()
        ax.text(p.get_x() + p.get_width()/2., height + (height*0.01),
                f'{share:.1%}', ha="center", fontsize=12, fontweight='bold')
                
    plt.tight_layout()
    plt.savefig('output_political_allocation.png')
    print("Saved: output_political_allocation.png")

def plot_economic_scatter(df):
    plt.figure(figsize=(10, 6))
    
    # Filter for cleaner viz (exclude 0 production counties if any)
    plot_df = df[df['soybean_bushels'] > 0]
    
    sns.scatterplot(x='median_household_income', y='soybean_bushels', 
                    hue='political_lean', palette=COLOR_PALETTE, 
                    alpha=0.6, data=plot_df)
    
    plt.title('Soybean Output vs. Economic Status', fontsize=16, fontweight='bold')
    plt.xlabel('Median Household Income ($)', fontsize=12)
    plt.ylabel('Soybean Production (Bushels)', fontsize=12)
    plt.yscale('log') # Log scale because ag production is often power-law distributed
    
    plt.tight_layout()
    plt.savefig('output_economic_scatter.png')
    print("Saved: output_economic_scatter.png")

def plot_demographic_dist(race_agg):
    plt.figure(figsize=(10, 6))
    sns.barplot(x='majority_race', y='soybean_bushels', data=race_agg, palette='viridis')
    plt.title('Soybean Production by County Majority Demographics', fontsize=16, fontweight='bold')
    plt.ylabel('Total Bushels', fontsize=12)
    plt.tight_layout()
    plt.savefig('output_demographic_dist.png')
    print("Saved: output_demographic_dist.png")