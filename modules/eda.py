import matplotlib.pyplot as plt
import pandas as pd

# consistent colors across all charts
FUEL_COLORS = {
    'Electric': '#2ecc71',   # green
    'Hybrid':   '#3498db',   # blue
    'Diesel':   '#e67e22',   # orange
    'Flex':     '#9b59b6',   # purple
    'Gasoline': '#95a5a6',   # grey (de-emphasized)
}

def plot_stacked_area(df, city, include_gasoline=False, show_legend=True, ax=None):
    """
    Plots a stacked area chart of fuel type percentage over time for a given city.
    
    Args:
        df (pd.DataFrame): Combined vehicle registration dataframe
        city (str): City name to filter for
        include_gasoline (bool): Whether to include gasoline (default False)
        ax: Optional matplotlib axis to plot on
    """
    city_df = df[df['city'] == city].copy()
    
    if not include_gasoline:
        city_df = city_df[city_df['fuel_type'] != 'Gasoline']

    pivot = city_df.pivot(index='year', columns='fuel_type', values='percentage').fillna(0)
    
    # order columns and assign colors
    cols = [c for c in ['Electric', 'Hybrid', 'Diesel', 'Flex'] if c in pivot.columns]
    pivot = pivot[cols]
    colors = [FUEL_COLORS[c] for c in cols]

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    pivot.plot.area(ax=ax, color=colors, alpha=0.85)
    
    ax.set_title(f'{city}', fontsize=12, fontweight='bold')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('% of Registered Vehicles', fontsize=11)
    ax.legend(title='Fuel Type', bbox_to_anchor=(1.01, 1), loc='upper left')
    ax.set_xticks(pivot.index)

    if show_legend:
        ax.legend(title='Fuel Type', bbox_to_anchor=(1.01, 1), loc='upper left')
    else:
        ax.get_legend().remove() if ax.get_legend() else None
    
    return ax