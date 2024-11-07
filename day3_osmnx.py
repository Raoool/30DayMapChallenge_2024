# Import required libraries
import osmnx as ox  
import matplotlib.pyplot as plt 
import matplotlib.colors as mcolors
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set up the plotting style
plt.style.use('dark_background')
ox.config(log_console=True, use_cache=True)

def create_building_map(city_name, colors, title):
    """Create a building footprint map for the specified city"""
    # Create a custom colormap
    cmap = mcolors.LinearSegmentedColormap.from_list("custom", colors)
    
    # Get the administrative boundary
    print(f"Downloading data for {city_name}...")
    admin_district = ox.geocode_to_gdf(city_name)
    admin_poly = admin_district.geometry.values[0]
    
    # Download building footprints
    print("Downloading building footprints...")
    footprints = ox.features_from_polygon(admin_poly, tags={"building": True})
    print(f"Number of buildings: {len(footprints)}")
    
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 15), facecolor='black')
    
    # Plot buildings
    footprints.plot(
        ax=ax,
        cmap=cmap,
        alpha=0.9,
        linewidth=0.5,
        edgecolor='#2d2d2d'
    )
    
    # Customize the plot
    ax.axis('off')
    plt.title(title, 
              pad=20,
              color='white',
              fontsize=20,
              fontfamily='monospace')
    
    # Add attribution
    plt.text(
        0.02, 0.02,
        'Data: OpenStreetMap Contributors\nMap: Rahul shah (@rahul_geo) | #30DayMapChallenge',
        transform=ax.transAxes,
        color='white',
        fontsize=10,
        alpha=0.7,
        fontfamily='monospace'
    )
    
    return fig, ax

# Choose one of these color schemes:
color_schemes = {
    'neon_city': ["#00ffff", "#ff00ff"],  # Cyberpunk feel
    'sunset': ["#FF4E50", "#F9D423"],      # Warm sunset colors
    'ocean': ["#43cea2", "#185a9d"],       # Ocean blues/greens
    'purple_gold': ["#904e95", "#e96443"], # Royal colors
    'matrix': ["#00ff00", "#003300"],      # Matrix-style
    'fire': ["#ff0000", "#ffff00"]         # Fire colors
}

# Example usage - choose a city and color scheme
city = "Manhattan, New York City"  # You can change this to any city
colors = color_schemes['sunset']  # Choose one from color_schemes
title = "MANHATTAN\nBUILDING FOOTPRINTS"

# Create the map
fig, ax = create_building_map(city, colors, title)
plt.show()
