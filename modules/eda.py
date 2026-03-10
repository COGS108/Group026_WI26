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

def build_city_df(city_str, air_quality_df, asthma_df, smoking_df, ev_df, ridership_df, years=range(2015, 2023), city_label=None):
    
    def filt(df, city_col, year_col):
        df = df[df[city_col].str.contains(city_str, case=False)]
        return df[df[year_col].isin(years)]

    air = filt(air_quality_df, "cbsa", "year")[["year","value"]].rename(columns={"value":"air_quality"})
    asth = filt(asthma_df, "city", "year")[["year","percentage"]].rename(columns={"percentage":"asthma"})
    smoke = filt(smoking_df, "Geography", "Year")[["Year","Current_Smoker_Pct"]].rename(columns={"Year":"year","Current_Smoker_Pct":"smoking"})
    ride = filt(ridership_df, "city", "year")[["year","ridership"]]
    ev = filt(ev_df, "city", "year")
    ev = ev[ev["fuel_type"] == "Electric"][["year","percentage"]].rename(columns={"percentage":"ev"})

    df = air.merge(asth, on="year").merge(smoke, on="year").merge(ev, on="year").merge(ride, on="year")

    df["city"] = city_label if city_label else city_str
    return df.rename(columns={
        "air_quality": "pm25",
        "asthma": "asthma_pct",
        "smoking": "smoking_pct",
        "ev": "ev_pct",
        "ridership": "ridership_count"
    })