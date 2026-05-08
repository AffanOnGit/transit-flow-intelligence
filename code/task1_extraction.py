"""
task1_extraction.py — Real CDA PDF Extraction (Regex Version)
Scrapes cda.gov.pk/cdaTransitMap, downloads PDFs, and parses schedules using regex.
"""
import os
import csv
import requests
import pdfplumber
import argparse
import re
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta
import tempfile

# Known coordinates for common stops (expanded from sample data)
STOP_COORDS = {
    "Khanna Pul": (33.6103, 72.9983), "Khana Pul": (33.6103, 72.9983),
    "Sangjani Interchange": (33.6270, 73.0150),
    "Golra Mor": (33.6435, 73.0199),
    "Shamsabad": (33.6605, 73.0296),
    "Faizabad Interchange": (33.7080, 73.0614), "Faizabad": (33.7080, 73.0614),
    "Aabpara": (33.7216, 73.0766),
    "F-7 Markaz": (33.7215, 73.0523),
    "F-10 Markaz": (33.7007, 73.0282),
    "H-9": (33.6850, 73.0100),
    "FAST University H-11": (33.6844, 73.0479), "FAST University": (33.6844, 73.0479),
    "Rawat": (33.5844, 73.2087),
    "Koral Chowk": (33.6044, 73.1789),
    "Loi Bher": (33.6187, 73.1520),
    "T-Chowk": (33.6380, 73.1234),
    "I-8 Markaz": (33.6683, 73.0888),
    "I-10 Markaz": (33.6594, 73.0656),
    "H-11 Markaz": (33.6737, 73.0492),
    "Nust Metro Station": (33.6844, 73.0123), "NUST Metro Station": (33.6844, 73.0123),
    "Police Foundation Metro Station": (33.6700, 73.0300),
    "Islamic University": (33.6850, 73.0250),
}

CDA_PORTAL_URL = "https://cda.gov.pk/cdaTransitMap"
BASE_DOMAIN = "https://cda.gov.pk"

def scrape_pdf_links():
    print(f"Scraping {CDA_PORTAL_URL} for PDF links...")
    try:
        response = requests.get(CDA_PORTAL_URL, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.endswith(".pdf") and "/Assets/metro_transit_route/" in href:
                if not href.startswith("http"): href = BASE_DOMAIN + href
                links.append(href)
        return sorted(list(set(links)))
    except Exception as e:
        print(f"Error scraping portal: {e}")
        return []

def parse_cda_pdf(pdf_url):
    # Extract route id from filename, e.g., FR-01 from FR-01_Forward.pdf
    filename = pdf_url.split("/")[-1]
    route_id = filename.split("_")[0]
    direction = "Forward" if "Forward" in filename else "Backward"
    
    print(f"Parsing {route_id} ({direction}) from {filename}...")
    
    all_stops = []
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            resp = requests.get(pdf_url, timeout=10)
            tmp.write(resp.content)
            tmp_path = tmp.name
        
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                
                # Regex to find: Stop Name followed by two HH:MM:SS times
                matches = re.findall(r'(.+?)\s+(\d{2}:\d{2}:\d{2})\s+(\d{2}:\d{2}:\d{2})', text)
                
                # We need to detect "Trip ID" or "Start Time" to separate trips
                # But for the purpose of Task 1, we can just treat consecutive stops as parts of a trace.
                # Heuristic: If arrival time decreases, it's a new trip.
                
                current_trip_stops = []
                last_time = None
                
                for m in matches:
                    stop_name, arr_str, dep_str = m[0].strip(), m[1].strip(), m[2].strip()
                    
                    # Ignore headers
                    if stop_name.lower() == "stop_name": continue
                    
                    try:
                        arr_dt = datetime.strptime(arr_str, "%H:%M:%S")
                        if last_time and arr_dt < last_time:
                            # New trip started
                            if current_trip_stops: all_stops.append(current_trip_stops)
                            current_trip_stops = []
                        
                        current_trip_stops.append({
                            "stop_name": stop_name,
                            "arrival": arr_str,
                            "departure": dep_str
                        })
                        last_time = arr_dt
                    except:
                        continue
                
                if current_trip_stops:
                    all_stops.append(current_trip_stops)
                    
        os.unlink(tmp_path)
    except Exception as e:
        print(f"Error parsing PDF {pdf_url}: {e}")
        
    return route_id, direction, all_stops

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fallback", action="store_true")
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    csv_path = script_dir.parent / "data" / "routes.csv"
    
    if args.fallback:
        import generate_sample_data
        generate_sample_data.generate_routes_csv(str(csv_path))
        return

    pdf_links = scrape_pdf_links()
    if not pdf_links:
        print("No links found. Using fallback.")
        import generate_sample_data
        generate_sample_data.generate_routes_csv(str(csv_path))
        return

    all_rows = []
    base_date = datetime(2026, 4, 23)
    
    # Extra Instructions Check:
    # 1. 4 Members = 8 Datasets/Routes
    # 2. Consider FORWARD pass only
    # 3. Fulfill Part 6 requirements (Need FR-01, FR-06, FR-08, FR-02)
    
    unique_routes = {} # rid -> link
    
    # First, prioritize the routes needed for Task 6
    priority_routes = ["FR-01", "FR-02", "FR-06", "FR-08"]
    
    # Filter links for Forward pass only
    forward_links = [l for l in pdf_links if "Forward" in l]
    
    for rid_req in priority_routes:
        for link in forward_links:
            if rid_req in link:
                unique_routes[rid_req] = link
                break
                
    # Fill remaining to get to 8 routes
    for link in forward_links:
        rid = link.split("/")[-1].split("_")[0]
        if rid not in unique_routes:
            unique_routes[rid] = link
        if len(unique_routes) >= 8:
            break
            
    selected_links = list(unique_routes.values())
    print(f"Selected 8 Forward-only routes: {list(unique_routes.keys())}")

    for i, link in enumerate(selected_links, start=1):
        print(f"[{i}/8] Processing route...")
        rid, direction, trips = parse_cda_pdf(link)
        for t_idx, trip_stops in enumerate(trips, start=1):
            # Unique case ID per trip and direction
            case_id = f"{rid}-{direction[0]}-T{t_idx:02d}"
            
            for seq, stop in enumerate(trip_stops, start=1):
                sname = stop["stop_name"]
                
                # Convert time strings to ISO8601
                arr_dt = base_date + timedelta(hours=int(stop["arrival"][:2]), 
                                             minutes=int(stop["arrival"][3:5]), 
                                             seconds=int(stop["arrival"][6:8]))
                dep_dt = base_date + timedelta(hours=int(stop["departure"][:2]), 
                                             minutes=int(stop["departure"][3:5]), 
                                             seconds=int(stop["departure"][6:8]))
                
                lat, lon = STOP_COORDS.get(sname, (33.6844, 73.0479))
                
                all_rows.append({
                    "case_id": case_id,
                    "route_id": rid,
                    "trip_number": t_idx,
                    "stop_sequence": seq,
                    "stop_name": sname,
                    "latitude": lat, "longitude": lon,
                    "arrival_time": arr_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "departure_time": dep_dt.strftime("%Y-%m-%dT%H:%M:%S")
                })

    if not all_rows:
        print("No data extracted. Falling back.")
        import generate_sample_data
        generate_sample_data.generate_routes_csv(str(csv_path))
        return

    fieldnames = ["case_id","route_id","trip_number","stop_sequence","stop_name",
                  "latitude","longitude","arrival_time","departure_time"]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
        
    print(f"Extraction Successful. Total Events: {len(all_rows)}. Saved to {csv_path}")

if __name__ == "__main__":
    main()
