## US Fire Map
# Author: Rahul Shah

import pandas as pd
import folium
from folium import plugins
from datetime import datetime, timedelta
import requests
from io import StringIO
import json

# 1. GET AREA
xmin, ymin, xmax, ymax = -125.0, 24.0, -66.0, 49.5
area_coords = f"{xmin},{ymin},{xmax},{ymax}"

# 2. FIRE DATA
def get_fire_data(main_url, map_key, source, area, day_range, date):
    url = f"{main_url}/{map_key}/{source}/{area}/{day_range}/{date}"
    response = requests.get(url)
    fire_data = pd.read_csv(StringIO(response.content.decode('utf-8')))
    return fire_data

main_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
map_key = "************************"   # Your API key
source = "VIIRS_SNPP_NRT"
day_range = 10
date = (datetime.now() - timedelta(days=11)).strftime('%Y-%m-%d')

fire_data = get_fire_data(main_url, map_key, source, area_coords, day_range, date)

# 3. CREATE MAP
m = folium.Map(location=[37.5, -96], zoom_start=4, tiles='OpenTopoMap')

# 4. PREPARE FIRE DATA FOR ANIMATION
fire_data['datum'] = pd.to_datetime(fire_data['acq_date'])
fire_data['bright_ti5_celsius'] = fire_data['bright_ti5'] - 273.15

# Create a color map function (different shades of red)
def get_color(temp):
    if temp < fire_data['bright_ti5_celsius'].quantile(0.33):
        return '#ffcccb'  # light red
    elif temp < fire_data['bright_ti5_celsius'].quantile(0.66):
        return '#ff6666'  # medium red
    else:
        return '#ff0000'  # bright red

# Prepare GeoJSON for TimestampedGeoJson
features = []
for _, fire in fire_data.iterrows():
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [fire['longitude'], fire['latitude']]
        },
        'properties': {
            'time': fire['datum'].strftime('%Y-%m-%d'),
            'popup': f"Date: {fire['datum']}<br>Temperature: {fire['bright_ti5_celsius']:.2f}°C",
            'icon': 'circle',
            'iconstyle': {
                'fillColor': get_color(fire['bright_ti5_celsius']),
                'fillOpacity': 0.7,
                'stroke': 'false',  # Remove border
                'radius': 5
            }
        }
    }
    features.append(feature)

# Add TimestampedGeoJson to map
plugins.TimestampedGeoJson({
    'type': 'FeatureCollection',
    'features': features
}, period='P1D', add_last_point=True, auto_play=False, loop=False).add_to(m)

# Add custom legend
legend_html = '''
<div style="position: fixed; 
bottom: 50px; right: 50px; width: 120px; height: 90px; 
border:2px solid grey; z-index:9999; font-size:14px;
background-color:white;
">&nbsp; Temperature <br>
&nbsp; <i class="fa fa-circle fa-1x" style="color:#ffcccb"></i> Low<br>
&nbsp; <i class="fa fa-circle fa-1x" style="color:#ff6666"></i> Medium<br>
&nbsp; <i class="fa fa-circle fa-1x" style="color:#ff0000"></i> High
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add attribution (moved higher)
attribution = "Data: NASA FIRMS | Map Created by Rahul Shah (@rahul_geo)"
m.get_root().html.add_child(folium.Element(f'''
<div style="
    position: fixed; 
    bottom: 100px; 
    left: 10px; 
    width: 250px;
    z-index:9999; 
    font-size:12px; 
    background-color:white; 
    border:2px solid grey;
    padding: 5px;
    ">
    {attribution}
</div>
'''))

# Add layer control
folium.LayerControl().add_to(m)

# Save the map
m.save("fire-us-topo-animated.html")
print("Animated map saved as fire-us-topo-animated.html")
