##Author: Rahul Shah

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Load the obesity data
obesity_data = pd.read_csv("/rshah/30DayMapChallenge/LakeCounty_Health_2397514566901885190.csv")

# Load US states shapefile
url = "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_state_20m.zip"
us_states = gpd.read_file(url)

# Merge obesity data with shapefile
merged = us_states.merge(obesity_data, left_on='NAME', right_on='NAME', how='left')

# Convert to Web Mercator projection for basemap
merged = merged.to_crs(epsg=3857)

# Filter for continental US
merged_continental = merged[~merged['NAME'].isin(['Alaska', 'Hawaii', 'Puerto Rico'])]

# Create the plot
fig, ax = plt.subplots(figsize=(20, 12))

# Plot the choropleth map
im = merged_continental.plot(column='Obesity', cmap='YlOrBr', linewidth=0.8, edgecolor='0.8', 
                             ax=ax, legend=False)

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, alpha=0.5)

# Set the extent to continental US
x1, y1, x2, y2 = merged_continental.total_bounds
ax.set_xlim(x1, x2)
ax.set_ylim(y1, y2)

# Create a color bar
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="2%", pad=0.1)
sm = plt.cm.ScalarMappable(cmap='YlOrBr', norm=plt.Normalize(vmin=merged_continental['Obesity'].min(), 
                                                             vmax=merged_continental['Obesity'].max()))
sm._A = []
cbar = fig.colorbar(sm, cax=cax)
cbar.set_label('Obesity Rate (%)', fontsize=14, fontweight='bold')
cbar.ax.tick_params(labelsize=12)

# Add state initials
for idx, row in merged_continental.iterrows():
    state_center = row.geometry.centroid
    ax.annotate(row['STUSPS'], xy=(state_center.x, state_center.y), 
                xytext=(3, 3), textcoords="offset points",
                fontsize=10, fontweight='bold', ha='center', va='center')

# Customize the plot
ax.set_title('Obesity Rates by State in the Continental United States', fontsize=22, fontweight='bold')
ax.axis('off')

# Add attribution
plt.text(0.01, 0.04, 'Map: Rahul shah (@rahul_geo) | Data: HDX & CDC BRFSS', 
         transform=ax.transAxes, fontsize=12, verticalalignment='bottom', 
         bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

# Adjust layout and display
plt.tight_layout()
plt.savefig('US_obesity_rates_map_updated.png', dpi=300, bbox_inches='tight')
plt.show()
