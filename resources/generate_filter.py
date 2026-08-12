import json

autobus_list = ["1", "5", "8", "9", "11",
                "20", "21", "22", "23", "25", "28",
                "31", "32", "33", "34", "37", "38", "39",
                "40", "41", "42", "43", "44", "45", "46", "47", "48",
                "50", "51", "52", "53", "54", "55", "57", "58", "59",
                "60", "61", "64", "66", "67", "68", "69",
                "70", "70N", "71", "72", "73", "74", "75", "78",
                "80", "82", "83", "83N",
                "91", "92",
                "A", "E", "G", "L"]
trolleybus_list = ["2", "3", "6", "7", "10", "19"]
tram_list = ["12", "14", "15", "17", "18"]
express_line_list = ["E+", "G+"]
seasonal_line_list = ["29"]
school_line_list = ["C1", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
partner_line_list = ["271", "272", "274", "M", "N"]

resulting_file_content = ""
filter_list = []
for line in autobus_list + trolleybus_list + tram_list + express_line_list + seasonal_line_list + school_line_list + partner_line_list:
    current_filter = {"filter_name": "Sans " + line, "filter": {
        "Line": [line]
    }}
    filter_list.append(current_filter)
   
with open("complete.filter", "w") as f:
    f.write(json.dumps(filter_list, indent=4))
