import plotly.express as px
import json

hectare_filename = "hectare_2025-04-10 07:30:00_PT1800S_split"
geojson_filename = "geo_ressources/geo_grid_swiss_wgs84_combined_filtered"
with open(geojson_filename + '.geojson') as geo_file:
# with open('geo_ressources/geo_romandie_wgs84_PROD_v1.json') as geo_file:
    region_map = json.load(geo_file)


with open(hectare_filename + '.json') as file:
    hectares = json.load(file)

fig = px.choropleth(hectares,
                    geojson=region_map,
                    locations="reli",
                    featureidkey="properties.reli",
                    # range_color=[0,500000000],
                    color_continuous_midpoint=0,
                    color="diff_max_0",
                    color_continuous_scale='RdYlGn',
                    projection="mercator")
# fig.update_geos(fitbounds="locations", visible=False)
fig.update_geos(fitbounds="locations")
fig.write_image(file=hectare_filename + '.svg')
