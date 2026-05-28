import plotly.express as px
import json

def generate_img_from_hectare(data_to_display, region_to_display, displayed_value:str, output_filename:str):
    fig = px.choropleth(data_to_display,
                        geojson=region_to_display,
                        locations="reli",
                        featureidkey="properties.reli",
                        # range_color=[0,500000000],
                        color_continuous_midpoint=0,
                        color=displayed_value,
                        color_continuous_scale='RdYlGn',
                        projection="mercator")
    # fig.update_geos(fitbounds="locations", visible=False)
    fig.update_geos(fitbounds="locations")
    fig.write_image(file=output_filename + '.svg', scale=100, width=8000, height=8000)

if __name__ == "__main__":
    hectare_filename = "hectare_2025-04-10 07:30:00_PT1800S_split"
    geojson_filename = "geo_ressources/geo_grid_swiss_wgs84_combined_filtered"
    with open(geojson_filename + '.geojson') as geo_file:
        # with open('geo_ressources/geo_romandie_wgs84_PROD_v1.json') as geo_file:
        region_map = json.load(geo_file)


    with open(hectare_filename + '.json') as file:
        hectares = json.load(file)
    generate_img_from_hectare(hectares, region_map, "diff_max_0", hectare_filename)

