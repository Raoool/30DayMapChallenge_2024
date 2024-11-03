## Author: Rahul Shah
## Inspired from Milos Popovic

import geopandas as gpd
import zipfile
import requests
import os
from matplotlib import cm, colormaps, pyplot as plt
import numpy as np

# 1. GET COUNTRY BORDERS
resolution_choices = ["01M", "03M", "10M", "30M", "60M"]
res = resolution_choices[4]
country = "NP"  # Changed to Nepal's country code
world_country_borders = gpd.read_file(
    f"https://gisco-services.ec.europa.eu/distribution/v2/countries/geojson/CNTR_RG_{res}_2020_4326.geojson")
country_border = world_country_borders[world_country_borders["CNTR_ID"] == country]

# 2. GET RIVER BASINS
# Changed URL to Asia's HydroBASINS
url = "https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_as_lev03_v1c.zip"
file_name = "hybas_as_lev03_v1c.zip"
r = requests.get(url)
with open(file_name, 'wb') as outfile:
    outfile.write(r.content)
with zipfile.ZipFile(file_name, 'r') as zip_ref:
    zip_ref.extractall()

asia_basin = gpd.read_file(file_name.split(".")[0]+".shp")
country_basin = gpd.overlay(
    country_border, asia_basin, how='intersection')

# 3. GET RIVERS
# Using Asia's HydroRIVERS file (already downloaded in your script)
namerica_rivers = gpd.read_file(os.path.join("HydroRIVERS_v10_as_shp","HydroRIVERS_v10_as.shp"))
country_river_basin = gpd.overlay(
    namerica_rivers, country_basin, how='intersection')

# 4. RIVER WIDTH
def assign_river_width(row):
    if row['ORD_FLOW'] == 1:
        return 0.8
    elif row['ORD_FLOW'] == 2:
        return 0.7
    elif row['ORD_FLOW'] == 3:
        return 0.6
    elif row['ORD_FLOW'] == 4:
        return 0.45
    elif row['ORD_FLOW'] == 5:
        return 0.35
    elif row['ORD_FLOW'] == 6:
        return 0.25
    elif row['ORD_FLOW'] == 7:
        return 0.2
    elif row['ORD_FLOW'] == 8:
        return 0.15
    elif row['ORD_FLOW'] == 9:
        return 0.1
    else:
        return 0

country_river_basin['width'] = country_river_basin.apply(
    assign_river_width, axis=1)
# 5. ENHANCED PLOTTING
# ------------------
# Normalize width values
norm_alpha = (country_river_basin['width'] - country_river_basin['width'].min()) / (
    country_river_basin['width'].max() - country_river_basin['width'].min())

# Create figure with higher DPI for better quality
fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# Get the bounds of Nepal for zooming
bounds = country_border.total_bounds
# Add some padding (10%) to the bounds
padding = 0.1
x_padding = (bounds[2] - bounds[0]) * padding
y_padding = (bounds[3] - bounds[1]) * padding
ax.set_xlim([bounds[0] - x_padding, bounds[2] + x_padding])
ax.set_ylim([bounds[1] - y_padding, bounds[3] + y_padding])

# Plot basins with a subtle color scheme
country_basin.plot(ax=ax, color='#1a1a1a', alpha=0.5, linewidth=0.5, 
                  linestyle='--', edgecolor='#333333')

# Create glow effect by plotting multiple times with decreasing width and opacity
glow_color = '#4287f5'  # Blue color for rivers
n_glow_lines = 10  # Number of lines to create glow effect

for i in range(n_glow_lines):
    # Plot with decreasing width and opacity
    scale = 1 + (n_glow_lines - i) * 0.2
    alpha = 0.03 * (n_glow_lines - i)
    
    country_river_basin.plot(ax=ax, color=glow_color,
                           linewidth=country_river_basin['width'] * scale,
                           alpha=alpha)

# Plot the final, sharpest rivers on top
country_river_basin.plot(ax=ax, color='white',
                       linewidth=country_river_basin['width'],
                       alpha=1)

# Enhanced text styling
title_text = plt.text(0.5, 1.02, 'Rivers of Nepal', 
                     ha='center', va='top', transform=ax.transAxes,
                     fontsize=36, color='white', weight='bold')
#title_text.set_path_effects([withStroke(linewidth=2, foreground='#4287f5')])

plt.text(0.9, 0.02, 'Map created by Rahul Shah (@rahul_geo)', 
         ha='right', va='bottom', transform=ax.transAxes,
         fontsize=12, color='#808080', style='italic')
plt.text(0.1, 0.02, 'Data Source: HydroSheds', 
         ha='left', va='bottom', transform=ax.transAxes,
         fontsize=12, color='#808080', style='italic')

# Remove axis
ax.set_axis_off()

# Tight layout to maximize map size
plt.tight_layout()
plt.show()
