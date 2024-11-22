# Author: Rahul Shah

import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Load the vessel traffic data
gdb_folder = "US_Vessel_Traffic_2024_03.gdb"
vessel_data = gpd.read_file(gdb_folder, layer='US_Vessel_Traffic_2024_03')

# Filter for cargo ships
cargo_ships = vessel_data[vessel_data['vessel_group'] == 'Cargo']

print(f"Number of cargo ship tracks: {len(cargo_ships)}")

# Ensure the data is in the correct CRS
cargo_ships = cargo_ships.to_crs(epsg=4326)

# Simplify the geometries to reduce complexity
cargo_ships['geometry'] = cargo_ships.geometry.simplify(tolerance=0.01)

# Load US states for the basemap
usa = gpd.read_file('us_states_data/cb_2020_us_state_20m.shp')

# Set up the map
fig, ax = plt.subplots(figsize=(20, 15), subplot_kw={'projection': ccrs.AlbersEqualArea(central_longitude=-96, central_latitude=37.5)})

# Set extent to cover the entire US including Alaska and Hawaii
ax.set_extent([-137.69995498, -60.37662866, 17.15849535, 50.73010450], crs=ccrs.PlateCarree())

#-137.69995498,17.15849535,-60.37662866,50.73010450

# Add US states
usa.plot(ax=ax, color='black', edgecolor='#333333', linewidth=0.5)

# Plot cargo ship tracks in red
cargo_ships.plot(ax=ax, color='red', linewidth=0.5, alpha=0.5, transform=ccrs.PlateCarree())

# Add coastlines
ax.add_feature(cfeature.COASTLINE, edgecolor='#333333', linewidth=0.5)

# Remove axes
ax.axis('off')

# Add title
plt.title("US Cargo Ship Traffic - March 2024", fontsize=24, fontweight='bold', color='white')

# Add attribution
plt.text(0.95, 0.05, 'Map: Rahul Shah (@rahul_geo)\nData: ESRI Atlas', 
         horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes,
         fontsize=12, color='white')

# Set background color
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# Save the map
plt.savefig('us_cargo_ship_traffic_2color1.png', dpi=300, bbox_inches='tight', facecolor='black')
plt.close()

print("Map has been saved as 'us_cargo_ship_traffic_2color.png'")

# Print some additional information
print(f"Cargo ships data CRS: {cargo_ships.crs}")
print(f"Bounding box of cargo ships data: {cargo_ships.total_bounds}")
