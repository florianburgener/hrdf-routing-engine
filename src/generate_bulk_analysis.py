import json
import glob
import sys
from dataclasses import dataclass
from os.path import getmtime
from typing import Any

from pathlib import Path

from choropleth_generator import generate_img_from_hectare
from compute_hectare_display_values import load_and_update_hectare


@dataclass
class FileStats:
    # Base statistics
    max_decrease: float
    max_increase: float
    median: float
    average: float
    winning_nb: float
    losing_nb: float
    percentiles: list
    # Population weighted
    pop_max_decrease: float
    pop_max_increase: float
    pop_median: float
    pop_average: float
    pop_winning_nb: float
    pop_losing_nb: float
    pop_percentiles: list
    # Percentages
    percentage_max_decrease: float
    percentage_max_increase: float
    percentage_median: float
    percentage_average: float
    percentage_winning_nb: float
    percentage_losing_nb: float
    percentage_percentiles: list
    # Percentages weighted by population
    percentage_pop_max_decrease: float
    percentage_pop_max_increase: float
    percentage_pop_median: float
    percentage_pop_average: float
    percentage_pop_winning_nb: float
    percentage_pop_losing_nb: float
    percentage_pop_percentiles: list

    # Global information
    glob_inhabitant_nb: int
    glob_hectares_nb: int


import datetime


# Function to convert string to datetime
def convert(date_time):
    format = '%b %d %Y %I:%M%p'
    datetime_str = datetime.datetime.strptime(date_time, format)

def format_percentage(fs_obj, att):
    att_unit = "%" if "pop" not in att else ""
    if "glob" not in att:
        return " (" + str(round(fs_obj[0][base].__getattribute__("percentage_"+att) * 100, 2)) + f"{att_unit})"
    else:
        return ""

def format_percentage_list(fs_obj, i, att):
    att_unit = "%" if "pop" not in att else ""
    if "glob" not in att:
        return " (" + str(round(fs_obj[0][base].__getattribute__("percentage_"+att)[i] * 100, 2)) + f"{att_unit})"
    else:
        return ""


def write_summary(files_stats: dict[str, dict[int, dict[str, FileStats]]], out_file: list[str], write_on_disk: bool,
                  print_result: bool):
    format_with_weekday = "%A %Y-%m-%d"
    column_width = 30

    days_from = [datetime.datetime.fromisoformat(fn.split("_")[-2]) for fn in out_file]
    days_to = [datetime.datetime.fromisoformat(fn.split("_")[1]) for fn in out_file]
    bases = list(files_stats.values())[0][0].keys()
    first_datetime = min(days_to)
    last_datetime = max(days_to)
    first_time = first_datetime.time()
    last_time = last_datetime.time()
    first_day = first_datetime.date()
    last_day = last_datetime.date()
    lines: list[str] = []
    lines += [
        f"Summary of analysis from the {first_day.strftime(format_with_weekday)} at {first_time} to the {last_day.strftime(format_with_weekday)} at {last_time}"]
    lines += ['Résultat des comparaisons sur une semaine, entre les horaires 2024 et 2025.',
              "Nous comparons les surfaces de l'isochrone minimal, le médian et le maximal.",
              "Pour chacune de ces comparaisons, nous affichons pour chaque jour les valeurs calculées.",
              "",
              "Description des valeurs :",
              "Max_decrease : la surface perdue de l'hectare ayant le plus perdu de surface",
              "max_increase : la surface gagnée de l'hectare ayant le plus gagné en surface",
              "median : la médiane de différence de surface",
              "average : la moyenne de différence de surface",
              "winning_nb : le nombre d'hectares ayant gagné en surface",
              "losing_nb : le nombre d'hectares ayant perdu en surface",
              "percentiles : le tableau représentant les percentiles affiché, avec à chaque fois la surface gagnée (ou perdue si négatif) correspondant à ce percentile",
              "les champs suivants, avec pop_, sont équivalents aux champs décris ci-dessus, mais sont pondérés par le nombre d'habitants habitant dans chaque hectare",
              "les champs pop_winning_nb et pop_losing_nb indiquent combien de personnes ont vu la surface de l'isochrone de leur lieu d'habitant se réduire.",
              "inhabitant_nb: Le nombre d'habitants total pour tous les hectares considérés",
              "hectares_nb: Le nombre total d'hectares considérés",
              ]
    lines += [""]
    for num, base in zip(["First", "Second", "Third", "Fourth, Fifth"], bases):
        lines += [f"{num} array giving values for {base} comparisons :"]
        lines += [""]
        lines += [" | ".join(
            ["Statistic".center(column_width)] + [dt.date().strftime(format_with_weekday).center(column_width) for dt in
                                                  days_to])]
        lines += ["_" * len(lines[-1])]
        for att in files_stats[out_file[0]][0][base].__dict__.keys():
            att_unit = "%" if "pop" not in att else ""
            if "percentage" not in att:
                if type(files_stats[out_file[0]][0][base].__getattribute__(att)) != list:
                    lines += [" | ".join(
                        [att.center(column_width)] + [(str(round(fs_obj[0][base].__getattribute__(att), 3)) + format_percentage(fs_obj, att)).center(column_width)
                                                      for fs_obj in files_stats.values()])]
                else:
                    lists = [fs_obj[0][base].__getattribute__(att) for fs_obj in files_stats.values()]
                    for i in range(len(lists[0])):
                        lines += [" | ".join([(att if i == 0 else "").center((column_width * 2) // 3)] + [
                            (str(i * 100 // len(lists[0])) + "%").center(column_width // 3 - 3)] + [
                                                 (str(round(fs_obj[0][base].__getattribute__(att)[i], 3)) + format_percentage_list(fs_obj, i, att)).center(column_width) for
                                                 fs_obj in files_stats.values()])]
                lines += ["-" * len(lines[-1])]
        lines += ["Comments:"]
        lines += [""]
        lines += ["=" * len(lines[-1])]
        lines += [""]
        lines += [""]

    if print_result:
        print("\n".join(lines))
    if write_on_disk:
        with open("summary_" + first_datetime.isoformat() + "_" + last_datetime.isoformat() + ".stat", "w") as f:
            f.write("\n".join(lines))


def compute_stats(hectares, attribute, wanted_percentiles, lines, factor) -> tuple[float, float, float, float, int, int, list[float], str]:
    hectares.sort(key=lambda v: v[attribute] * factor(v))
    max_decrease = hectares[0][attribute] * factor(hectares[0])
    max_increase = hectares[-1][attribute] * factor(hectares[-1])
    median = hectares[total_hectares // 2][attribute] * factor(hectares[total_hectares // 2])
    avg = sum(v[attribute] * factor(v) for v in hectares) / total_hectares
    winning_nb = sum(factor(v) for v in hectares if v[attribute] > 0)
    losing_nb = sum(factor(v) for v in hectares if v[attribute] < 0)
    percentiles = []
    lines += f"Highest loss : {max_decrease}\n"
    lines += f"Highest increase : {max_increase}\n"
    lines += f"Median : {median}\n"
    lines += f"Average: {avg}\n"
    lines += f"Winning hectares: {winning_nb}\n"
    lines += f"Losing hectares: {losing_nb}\n"
    lines += f"For the percentile | we have at most won | m²\n"
    lines += f"_____________________________________________\n"
    for p in range(wanted_percentiles):
        concerned_hectare = hectares[(total_hectares * p) // wanted_percentiles]
        percentile = concerned_hectare[attribute] * factor(concerned_hectare)
        percentiles.append(percentile)
        p_line = f"{p * 100 / wanted_percentiles}% | {percentile} m²\n"
        lines += p_line
    return max_decrease, max_increase, median, avg, winning_nb, losing_nb, percentiles, lines


if __name__ == "__main__":
    generate_img = 2
    generate_stats = True
    print_stat = True
    compute_summary = False
    wanted_percentiles = 20
    hectare_files = []
    if len(sys.argv) >= 2:
        hectare_file = sys.argv[1]
        hectare_files.append(hectare_file)
    else:
        hectare_files = glob.glob("hectare_*.json")

    geojson_filename = "geo_ressources/geo_grid_swiss_wgs84_combined_filtered"
    with open(geojson_filename + '.geojson') as geo_file:
        # with open('geo_ressources/geo_romandie_wgs84_PROD_v1.json') as geo_file:
        region_map = json.load(geo_file)

    summary = {}
    for hectare_file in hectare_files:
        data_modified_time = getmtime(hectare_file)

        try:
            hectares, nb = load_and_update_hectare(hectare_file)
        except Exception as e:
            print(f"File {hectare_file} has bad format : {e}", file=sys.stderr)
            continue

        summary[hectare_file] = {}
        available_attributes = [key for key in hectares[0].keys() if "-" in key]

        for i, attribute in enumerate(available_attributes):
            # for i in range(nb):
                summary[hectare_file][i] = {}
                for base_ix, base in enumerate(["max", "mid", "min"]):
                    # attribute = attribute.split("_")[0] + "_diff_" + base + "_" + str(i)
                    stat_filename = hectare_file.split(".json")[0] + "_" + attribute + ".stat"
                    img_filename = hectare_file.split(".json")[0] + "_" + attribute + '.svg'
                    if (generate_stats and (not Path(stat_filename).exists() or getmtime(stat_filename) < data_modified_time)) or print_stat:
                        total_hectares = len(hectares)
                        total_inhabitant = sum(v["population"] for v in hectares)

                        # get all base stats
                        max_decrease, max_increase, median, avg, winning_nb, losing_nb, percentiles, lines = compute_stats(
                                                            hectares, attribute, wanted_percentiles, "", lambda x: 1)

                        # Now computing the same values but weighted by concerned population
                        pop_max_decrease, pop_max_increase, pop_median, pop_avg, pop_winning_nb, pop_losing_nb, pop_percentiles, pop_lines = compute_stats(
                            hectares, attribute, wanted_percentiles, "", lambda x: x["population"])

                        # Now computing the same values but in percentage
                        per_max_decrease, per_max_increase, per_median, per_avg, per_winning_nb, per_losing_nb, per_percentiles, per_lines = compute_stats(
                            hectares, attribute, wanted_percentiles, "", lambda x: 1.0/x["area"][1][1][0][base_ix])

                        # Now computing the same values but weighted by concerned population
                        perpop_max_decrease, perpop_max_increase, perpop_median, perpop_avg, perpop_winning_nb, perpop_losing_nb, perpop_percentiles, perpop_lines = compute_stats(
                            hectares, attribute, wanted_percentiles, "", lambda x: x["population"]/total_inhabitant)

                        if print_stat:
                            print(lines)

                        summary[hectare_file][i][base] = FileStats(max_decrease=max_decrease,
                                                                   max_increase=max_increase,
                                                                   median=median,
                                                                   average=avg,
                                                                   winning_nb=winning_nb,
                                                                   losing_nb=losing_nb,
                                                                   percentiles=percentiles,
                                                                   pop_max_decrease=pop_max_decrease,
                                                                   pop_max_increase=pop_max_increase,
                                                                   pop_median=pop_median,
                                                                   pop_average=pop_avg,
                                                                   pop_winning_nb=pop_winning_nb,
                                                                   pop_losing_nb=pop_losing_nb,
                                                                   pop_percentiles=pop_percentiles,
                                                                   percentage_max_decrease=per_max_decrease,
                                                                   percentage_max_increase=per_max_increase,
                                                                   percentage_median=per_median,
                                                                   percentage_average=per_avg,
                                                                   percentage_winning_nb=per_winning_nb,
                                                                   percentage_losing_nb=per_losing_nb,
                                                                   percentage_percentiles=per_percentiles,
                                                                   percentage_pop_max_decrease=perpop_max_decrease,
                                                                   percentage_pop_max_increase=perpop_max_increase,
                                                                   percentage_pop_median=perpop_median,
                                                                   percentage_pop_average=perpop_avg,
                                                                   percentage_pop_winning_nb=perpop_winning_nb,
                                                                   percentage_pop_losing_nb=perpop_losing_nb,
                                                                   percentage_pop_percentiles=perpop_percentiles,
                                                                   glob_inhabitant_nb=total_inhabitant,
                                                                   glob_hectares_nb=total_hectares,
                                                                   )

                        if generate_stats and (not Path(stat_filename).exists() or getmtime(stat_filename) < data_modified_time):
                            with open(
                                    stat_filename,
                                    "w") as f:
                                f.write(lines)

                    if generate_img:
                        if not Path(img_filename).exists() or getmtime(img_filename) < data_modified_time:
                            generate_img_from_hectare(hectares, region_map, attribute,
                                                      img_filename)
                        if generate_img > 1:
                            # attribute = "area_" + str(i + 1) + "_" + base
                            add_img_filename = hectare_file.split(".json")[0] + "_" + attribute + '.svg'
                            if not Path(add_img_filename).exists() or getmtime(add_img_filename) < data_modified_time:
                                generate_img_from_hectare(hectares, region_map, attribute, add_img_filename)

    if compute_summary:
        write_summary(summary, hectare_files, generate_stats, print_stat)
