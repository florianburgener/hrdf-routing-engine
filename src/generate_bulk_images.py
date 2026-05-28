import json
import glob
import sys

from choropleth_generator import generate_img_from_hectare
from compute_hectare_display_values import load_and_update_hectare

if __name__ == "__main__":

    fns = []
    if len(sys.argv) >= 2:
        fn = sys.argv[1]
        fns.append(fn)
    else:
        fns = glob.glob("hectare_*.json")

    geojson_filename = "geo_ressources/geo_grid_swiss_wgs84_combined_filtered"
    with open(geojson_filename + '.geojson') as geo_file:
        # with open('geo_ressources/geo_romandie_wgs84_PROD_v1.json') as geo_file:
        region_map = json.load(geo_file)
    for fn in fns:
        try:
            hectares, nb = load_and_update_hectare(fn)
        except Exception as e:
            print(f"File {fn} has bad format : {e}", file=sys.stderr)
            continue
        for i in range(nb):
            for base in ["diff_max_", "diff_mid_", "diff_min_"]:
                attribute = base + str(i)
                generate_img_from_hectare(hectares, region_map, attribute, fn.split(".json")[0] + "_" + attribute)
