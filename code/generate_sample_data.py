"""
generate_sample_data.py — Generates routes.csv with 8 CDA-style routes
Run: python generate_sample_data.py
"""
import csv, os
from datetime import datetime, timedelta
from pathlib import Path

ROUTES = {
    "FR-01": [
        ("Khanna Pul",            33.6103, 72.9983,  0),
        ("Sangjani Interchange",  33.6270, 73.0150,  5),
        ("Golra Mor",             33.6435, 73.0199, 10),
        ("Shamsabad",             33.6605, 73.0296, 14),
        ("Faizabad Interchange",  33.7080, 73.0614, 20),
        ("Aabpara",               33.7216, 73.0766, 25),
        ("F-7 Markaz",            33.7215, 73.0523, 30),
        ("F-10 Markaz",           33.7007, 73.0282, 36),
        ("H-9",                   33.6850, 73.0100, 41),
        ("FAST University H-11",  33.6844, 73.0479, 47),
    ],
    "FR-02": [
        ("Rawat",                 33.5844, 73.2087,  0),
        ("Koral Chowk",           33.6044, 73.1789,  6),
        ("Loi Bher",              33.6187, 73.1520, 11),
        ("T-Chowk",               33.6380, 73.1234, 16),
        ("I-8 Markaz",            33.6683, 73.0888, 22),
        ("I-10 Markaz",           33.6594, 73.0656, 27),
        ("H-11 Markaz",           33.6737, 73.0492, 32),
        ("FAST University H-11",  33.6844, 73.0479, 35),
    ],
    "FR-03": [
        ("Tarnol",                33.6650, 72.9367,  0),
        ("Margalla View Society", 33.6720, 72.9650,  7),
        ("Airport Road",          33.6781, 72.9985, 13),
        ("Golra Mor",             33.6435, 73.0199, 19),
        ("Peshawar Mor",          33.6667, 73.0200, 23),
        ("OGTI",                  33.6750, 73.0300, 27),
        ("H-8 Markaz",            33.6800, 73.0400, 31),
        ("H-9",                   33.6850, 73.0100, 35),
        ("FAST University H-11",  33.6844, 73.0479, 40),
    ],
    "FR-04": [
        ("PWD Colony",            33.6480, 73.1067,  0),
        ("Bhara Kahu",            33.6603, 73.1367,  5),
        ("Park Road CDA",         33.6793, 73.0983, 11),
        ("PAEC",                  33.6880, 73.0783, 16),
        ("Islamabad Club",        33.7080, 73.0814, 22),
        ("IMC",                   33.7180, 73.0767, 26),
        ("Zero Point",            33.7100, 73.0483, 31),
        ("PIMS",                  33.7003, 73.0600, 36),
        ("Aabpara",               33.7216, 73.0766, 41),
        ("F-6 Markaz",            33.7283, 73.0667, 46),
        ("F-7 Markaz",            33.7215, 73.0523, 50),
    ],
    "FR-05": [
        ("Bara Kahu",             33.7267, 73.2333,  0),
        ("Saidpur Village",       33.7367, 73.1200,  8),
        ("Daman-e-Koh Rd",        33.7400, 73.0967, 14),
        ("Shakar Parian",         33.7150, 73.0533, 21),
        ("Jinnah Avenue",         33.7050, 73.0667, 25),
        ("F-8 Markaz",            33.7133, 73.0450, 29),
        ("F-10 Markaz",           33.7007, 73.0282, 34),
        ("H-9",                   33.6850, 73.0100, 39),
        ("FAST University H-11",  33.6844, 73.0479, 44),
    ],
    "FR-06": [
        ("G-9 Markaz",            33.6950, 73.0533,  0),
        ("G-10 Markaz",           33.6917, 73.0400,  5),
        ("G-11 Markaz",           33.6883, 73.0267,  9),
        ("H-11 Markaz",           33.6737, 73.0492, 14),
        ("FAST University H-11",  33.6844, 73.0479, 17),
    ],
    "FR-07": [
        ("Faizabad Interchange",  33.7080, 73.0614,  0),
        ("G-9 Markaz",            33.6950, 73.0533,  7),
        ("G-10 Markaz",           33.6917, 73.0400, 11),
        ("G-11 Markaz",           33.6883, 73.0267, 15),
        ("H-8 Markaz",            33.6800, 73.0400, 19),
        ("H-9",                   33.6850, 73.0100, 23),
        ("H-10 Markaz",           33.6820, 72.9967, 27),
        ("H-11 Markaz",           33.6737, 73.0492, 31),
        ("FAST University H-11",  33.6844, 73.0479, 34),
    ],
    "FR-08": [
        ("I-8 Markaz",            33.6683, 73.0888,  0),
        ("I-9 Markaz",            33.6717, 73.0733,  5),
        ("I-10 Markaz",           33.6594, 73.0656,  9),
        ("G-10 Markaz",           33.6917, 73.0400, 14),
        ("G-11 Markaz",           33.6883, 73.0267, 18),
        ("H-11 Markaz",           33.6737, 73.0492, 23),
        ("FAST University H-11",  33.6844, 73.0479, 27),
    ],
}

TRIPS_PER_ROUTE = 3
BASE_TIME = datetime(2026, 4, 23, 8, 0, 0)
TRIP_INTERVAL_MINUTES = 30


def generate_routes_csv(output_path="../data/routes.csv"):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for route_id, stops in ROUTES.items():
        for trip_num in range(TRIPS_PER_ROUTE):
            trip_base = BASE_TIME + timedelta(minutes=TRIP_INTERVAL_MINUTES * trip_num)
            case_id = f"{route_id}-T{trip_num + 1:02d}"
            for seq, (stop_name, lat, lon, offset_min) in enumerate(stops, start=1):
                arr_time = trip_base + timedelta(minutes=offset_min)
                dep_time = arr_time + timedelta(seconds=60)
                rows.append({
                    "case_id": case_id, "route_id": route_id, "trip_number": trip_num + 1,
                    "stop_sequence": seq, "stop_name": stop_name,
                    "latitude": lat, "longitude": lon,
                    "arrival_time":   arr_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "departure_time": dep_time.strftime("%Y-%m-%dT%H:%M:%S"),
                })
    fieldnames = ["case_id","route_id","trip_number","stop_sequence","stop_name",
                  "latitude","longitude","arrival_time","departure_time"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} rows -> {output_path}")


if __name__ == "__main__":
    # Get absolute path for reliability
    script_dir = Path(__file__).parent
    csv_path = script_dir.parent / "data" / "routes.csv"
    generate_routes_csv(str(csv_path))
