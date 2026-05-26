
import plotly.express as px
import geopandas as gpd
import json

from shapely import Point
from shapely.geometry.polygon import Polygon

with open('hectare_2025-04-10 07:30:00_PT3600S.json') as file:
    hectares = json.load(file)
with open('geo_ressources/geo_grid_swiss_wgs84_combined_filtered.geojson') as geo_file:
# with open('geo_ressources/geo_romandie_wgs84_PROD_v1.json') as geo_file:
    region_map = json.load(geo_file)


df = px.data.election()
geo_df = gpd.GeoDataFrame.from_features(
    px.data.election_geojson()["features"]
).merge(df, on="district").set_index("district")

fig = px.choropleth(hectares,
                    geojson=region_map,
                    locations="reli",
                    featureidkey="properties.reli",
                    range_color=[0,500000000],
                    color_continuous_midpoint=150,
                    color="area",
                    color_continuous_scale='RdYlGn',
                    projection="mercator")
# fig.update_geos(fitbounds="locations", visible=False)
fig.update_geos(fitbounds="locations")
fig.show()
