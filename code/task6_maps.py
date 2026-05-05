"""
task6_maps.py — Personal Route Maps (Bonus Task)
"""
import folium
import os
from pathlib import Path
from utils import load_routes

# Placeholder member data - USER should update these with real details
MEMBERS = [
    {
        "name":           "Member 1 — Affan",
        "home_area":      "Khanna Pul, Islamabad",
        "home_lat":       33.6103,
        "home_lon":       72.9983,
        "nearest_stop":   "Khanna Pul",
        "routes_used":    ["FR-01"],
        "est_time_min":   47,
    },
    {
        "name":           "Member 2 — Team Mate 2",
        "home_area":      "G-9 Markaz, Islamabad",
        "home_lat":       33.6950,
        "home_lon":       73.0533,
        "nearest_stop":   "G-9 Markaz",
        "routes_used":    ["FR-06"],
        "est_time_min":   17,
    },
    {
        "name":           "Member 3 — Team Mate 3",
        "home_area":      "I-8 Markaz, Islamabad",
        "home_lat":       33.6683,
        "home_lon":       73.0888,
        "nearest_stop":   "I-8 Markaz",
        "routes_used":    ["FR-08"],
        "est_time_min":   27,
    },
    {
        "name":           "Member 4 — Team Mate 4",
        "home_area":      "Rawat, Islamabad",
        "home_lat":       33.5844,
        "home_lon":       73.2087,
        "nearest_stop":   "Rawat",
        "routes_used":    ["FR-02"],
        "est_time_min":   35,
    },
]

FAST_UNIVERSITY = {"name": "FAST University H-11", "lat": 33.6844, "lon": 73.0479}

def generate_member_maps(csv_path, output_dir):
    rows = load_routes(csv_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for member in MEMBERS:
        # Create map centered at FAST
        m = folium.Map(location=[33.68, 73.05], zoom_start=12, tiles="cartodbpositron")
        
        # Add Home Marker
        folium.Marker(
            [member["home_lat"], member["home_lon"]],
            popup=f"Home: {member['home_area']}",
            icon=folium.Icon(color='red', icon='home')
        ).add_to(m)
        
        # Add FAST Marker
        folium.Marker(
            [FAST_UNIVERSITY["lat"], FAST_UNIVERSITY["lon"]],
            popup=FAST_UNIVERSITY["name"],
            icon=folium.Icon(color='blue', icon='education', prefix='fa')
        ).add_to(m)
        
        # Trace the route
        for route_id in member["routes_used"]:
            route_stops = [r for r in rows if r["route_id"] == route_id and r["trip_number"] == 1]
            route_stops.sort(key=lambda x: x["stop_sequence"])
            
            points = [[r["latitude"], r["longitude"]] for r in route_stops if r["latitude"] and r["longitude"]]
            if points:
                folium.PolyLine(points, color="blue", weight=5, opacity=0.7, tooltip=f"Route {route_id}").add_to(m)
                for stop in route_stops:
                    folium.CircleMarker(
                        location=[stop["latitude"], stop["longitude"]],
                        radius=3,
                        color="blue",
                        fill=True,
                        popup=stop["stop_name"]
                    ).add_to(m)
        
        # Save map
        filename = f"{member['name'].replace(' ', '_')}_Map.html"
        save_path = Path(output_dir) / filename
        m.save(str(save_path))
        print(f"Saved map for {member['name']} to {save_path}")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    csv_path = script_dir.parent / "data" / "routes.csv"
    output_dir = script_dir.parent / "report" / "member_maps"
    generate_member_maps(str(csv_path), str(output_dir))
