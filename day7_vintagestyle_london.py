##Author: Rahul Shah

import osmnx as ox
import matplotlib.pyplot as plt 
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.patches import Rectangle
import warnings
import time
warnings.filterwarnings('ignore')

# Set up the plotting style
plt.style.use('default')
ox.config(log_console=True, use_cache=True, timeout=300)

def create_vintage_building_map(city_name, colors, title):
    """Create a vintage-style building footprint map for the specified city"""
    try:
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
        
        # Download rivers
        print("Downloading rivers...")
        rivers = ox.features_from_polygon(admin_poly, tags={"waterway": ["river", "stream", "canal"]})
        print(f"Number of river features: {len(rivers)}")
        
        # Create the plot
        fig, ax = plt.subplots(1, 1, figsize=(12, 15), facecolor='#f3e7d3')  # Vintage paper color
        
        # Plot rivers
        rivers.plot(ax=ax, color='#4a7496', linewidth=1, alpha=0.7)
        
        # Plot buildings
        footprints.plot(
            ax=ax,
            cmap=cmap,
            alpha=0.9,
            linewidth=0.5,
            edgecolor='#8b7765'  # Vintage brown color
        )
        
        # Customize the plot
        ax.axis('off')
        plt.title(title, 
            pad=20,
            color='#8b7765',  # Vintage brown color
            fontsize=20,
            fontfamily='serif',
            fontweight='bold'
        )
        
        # Add a border to mimic old map style
        border = Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, 
                           edgecolor='#8b7765', linewidth=5)
        ax.add_patch(border)
        
        # Add attribution
        plt.text(
            0.02, 0.02,
            'Data: OpenStreetMap Contributors\nMap: Rahul shah (@rahul_geo) | #30DayMapChallenge',
            transform=ax.transAxes,
            color='#8b7765',
            fontsize=10,
            alpha=0.7,
            fontfamily='serif',
            bbox=dict(facecolor='#f3e7d3', edgecolor='#8b7765', alpha=0.7)
        )
        
        return fig, ax
    except Exception as e:
        print(f"An error occurred while processing {city_name}: {str(e)}")
        return None, None

# Vintage color scheme
vintage_colors = ['#f3e7d3', '#d6c6a9']

# List of cities to map (focusing on smaller areas)
cities = [
    ("London, United Kingdom", "LONDON\nBUILDING FOOTPRINTS"),
    ("Downtown Dubai, United Arab Emirates", "DOWNTOWN DUBAI\nBUILDING FOOTPRINTS")
]

# Create maps for each city
for city, title in cities:
    print(f"\nCreating map for {city}")
    fig, ax = create_vintage_building_map(city, vintage_colors, title)
    if fig is not None:
        # Display the plot (optional, comment out if running in a non-interactive environment)
        plt.show()
        
        # Add a small delay
        time.sleep(1)
        
        # Save the plot
        filename = f"vintage_{city.split(',')[0].lower().replace(' ', '_')}_building_map_with_rivers.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#f3e7d3', format='png')
        plt.close(fig)
        print(f"Vintage-style {city} building map with rivers saved as '{filename}'")
    else:
        print(f"Failed to create map for {city}")

print("\nAll maps have been processed.")
