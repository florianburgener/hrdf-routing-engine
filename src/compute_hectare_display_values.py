import json

def load_and_update_hectare(hectare_file: str) -> tuple[dict, int]:
    with open(hectare_file) as file:
        hectares = json.load(file)

    highest_cmp = 0
    for h in hectares:
        if len(h["area"]) < 2 :
            continue
        previous_max, previous_mid, previous_min = h["area"][0]
        if len(h["area"]) > highest_cmp:
            highest_cmp = len(h["area"])
        for i, a in enumerate(h["area"][1:]):
            max, mid, min = a
            h["diff_max_"+str(i)] = max - previous_max
            h["diff_mid_"+str(i)] = mid - previous_mid
            h["diff_min_"+str(i)] = min - previous_min
            previous_max, previous_mid, previous_min = a
    return hectares, highest_cmp - 1

def write_hectare(hectare_file: str, hectares: dict):
    with open(hectare_file + "_split" + ".json", "w") as out_file:
        json.dump(hectares, out_file)

if __name__ == "__main__":
    hectare_file = "hectare_2025-04-10 07:30:00_PT1800S"
    write_hectare(hectare_file, load_and_update_hectare(hectare_file + '.json')[0])