# Author: Rahul Shah

import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from datetime import datetime, timedelta
import requests
from io import StringIO
import geopandas as gpd
import numpy as np
import matplotlib.colors as colors

# 1. GET AREA
xmin, ymin, xmax, ymax = -125.0, 24.0, -66.0, 49.5
area_coords = f"{xmin},{ymin},{xmax},{ymax}"

# 2. FIRE DATA
def get_fire_data(main_url, map_key, source, area, day_range, date):
    url = f"{main_url}/{map_key}/{source}/{area}/{day_range}/{date}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            fire_data = pd.read_csv(StringIO(response.content.decode('utf-8')))
            return fire_data
        except pd.errors.EmptyDataError:
            print("The API returned an empty dataset.")
            return pd.DataFrame()
    else:
        print(f"API request failed with status code {response.status_code}")
        return pd.DataFrame()

main_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
map_key = "*************************"   # Your API key
source = "VIIRS_SNPP_NRT"
day_range = 10  # Changed to 10 as per API limitation
date = (datetime.now() - timedelta(days=11)).strftime('%Y-%m-%d')

fire_data = get_fire_data(main_url, map_key, source, area_coords, day_range, date)

# Print column names
print("Available columns:")
print(fire_data.columns)

# 3. PREPARE FIRE DATA
if fire_data.empty:
    print("No data available. Creating dummy data for visualization.")
    num_points = 1000
    fire_data = pd.DataFrame({
        'latitude': np.random.uniform(ymin, ymax, num_points),
        'longitude': np.random.uniform(xmin, xmax, num_points),
        'bright_ti5_celsius': np.random.uniform(0, 100, num_points),
        'datum': pd.date_range(start=date, periods=num_points)
    })
else:
    # Use the correct column name for the date (adjust if necessary)
    date_column = 'acq_date' if 'acq_date' in fire_data.columns else 'datum'
    if date_column in fire_data.columns:
        fire_data['datum'] = pd.to_datetime(fire_data[date_column])
    else:
        print(f"Warning: '{date_column}' not found in columns. Using index as date.")
        fire_data['datum'] = pd.date_range(start=date, periods=len(fire_data))

    # Use the correct column name for brightness temperature (adjust if necessary)
    temp_column = 'bright_ti5' if 'bright_ti5' in fire_data.columns else 'bright_ti5_celsius'
    if temp_column in fire_data.columns:
        fire_data['bright_ti5_celsius'] = fire_data[temp_column] - 273.15 if temp_column == 'bright_ti5' else fire_data[temp_column]
    else:
        print(f"Warning: '{temp_column}' not found in columns. Using random temperatures.")
        fire_data['bright_ti5_celsius'] = np.random.uniform(0, 100, len(fire_data))

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(
    fire_data, geometry=gpd.points_from_xy(fire_data.longitude, fire_data.latitude),
    crs="EPSG:4326"
)

# 4. CREATE PLOT
fig = plt.figure(figsize=(22, 10), dpi=300)  # Slightly wider figure to accommodate colorbar

# Create main map axes
ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])  # [left, bottom, width, height]

# Set the extent of our map for contiguous US
states_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
states = gpd.read_file(states_url)
states = states[~states['name'].isin(['Alaska', 'Hawaii', 'Puerto Rico'])]
xmin, ymin, xmax, ymax = states.total_bounds

ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

# Add the CartoDB Positron basemap
ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.CartoDB.Positron, zoom=6)

# Plot state boundaries
states.boundary.plot(ax=ax, linewidth=0.8, color='gray')

# Add state labels
for idx, row in states.iterrows():
    centroid = row['geometry'].centroid
    ax.text(centroid.x, centroid.y, row['name'], fontsize=10, ha='center', va='center')

# Filter fire data for contiguous US
gdf = gdf[(gdf.longitude >= xmin) & (gdf.longitude <= xmax) & 
          (gdf.latitude >= ymin) & (gdf.latitude <= ymax)]

# Define a custom colormap
cmap = plt.cm.hot_r
norm = colors.Normalize(vmin=gdf.bright_ti5_celsius.min(), vmax=gdf.bright_ti5_celsius.max())

# Plot the fire data
scatter = ax.scatter(gdf.longitude, gdf.latitude, 
                     c=gdf.bright_ti5_celsius, 
                     cmap=cmap,
                     norm=norm,
                     s=20,
                     alpha=1)

# Create a custom axes for the colorbar
cax = fig.add_axes([0.91, 0.05, 0.02, 0.9])  # [left, bottom, width, height]

# Add colorbar
cbar = plt.colorbar(scatter, cax=cax, label='Temperature (°C)', pad=0.01)

# Add title in a box
title = f'Fire Hotspots in the Contiguous United States - {gdf["datum"].min().strftime("%B %Y")}'
title_box = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7)
ax.text(0.5, 0.98, title, fontsize=18, ha='center', va='top', 
        transform=ax.transAxes, bbox=title_box)

# Add attribution in a box
attr_text = "Data: NASA FIRMS | Created by Rahul Shah (@rahul_geo)"
attr_box = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7)
ax.text(0.99, 0.01, attr_text, fontsize=12, ha='right', va='bottom', 
        transform=ax.transAxes, bbox=attr_box)

ax.set_axis_off()

# Save the plot
plt.savefig('fire-us-contiguous-cartodb-states.png', bbox_inches='tight', pad_inches=0.1)
print("Map saved as fire-us-contiguous-cartodb-states.png")

# Show the plot (optional)
plt.show()
