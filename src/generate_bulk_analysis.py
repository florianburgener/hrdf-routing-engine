import json
import glob
import sys

from choropleth_generator import generate_img_from_hectare
from compute_hectare_display_values import load_and_update_hectare

if __name__ == "__main__":
    generate_img = True
    generate_stats = True
    print_stat = False
    wanted_percentiles = 20
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
            for base in ["max", "mid", "min"]:
                attribute = "diff_" + base + "_" + str(i)
                if generate_stats or print_stat:
                    hectares.sort(key= lambda v : v[attribute])
                    total_hectares = len(hectares)
                    lines = ""
                    lines += f"Highest loss : {hectares[0][attribute]}\n"
                    lines += f"Highest increase : {hectares[-1][attribute]}\n"
                    lines += f"Median : {hectares[total_hectares//2][attribute]}\n"
                    lines += f"Average: {sum(v[attribute] for v in hectares)/total_hectares}\n"
                    lines += f"Winning hectares: {sum(1 for v in hectares if v[attribute] > 0)}\n"
                    lines += f"Losing hectares: {sum(1 for v in hectares if v[attribute] < 0)}\n"
                    lines += f"For the percentile | we have at most won | m²\n"
                    lines += f"_____________________________________________\n"
                    for p in range(wanted_percentiles):
                        p_line = f"{p * 100 / wanted_percentiles}% | {hectares[(total_hectares * p) // wanted_percentiles][attribute]} m²\n"
                        lines += p_line

                    if print_stat:
                        print(lines)

                    if generate_stats:
                        with open(fn.split(".json")[0] + "_" + attribute + ".stat", "w") as f:
                            f.write(lines)

                if generate_img:
                    generate_img_from_hectare(hectares, region_map, attribute, fn.split(".json")[0] + "_" + attribute)
