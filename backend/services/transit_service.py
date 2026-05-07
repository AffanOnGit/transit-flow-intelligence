import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

class TransitService:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.rows = self.load_routes()
        self.cases = self.group_by_case()
        self.all_edges = self.aggregate_edges(self.compute_edges())
        self.throughput_data = self.compute_throughput()
        self.node_coords = self.build_node_positions()

    def load_routes(self):
        rows = []
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["stop_sequence"] = int(row["stop_sequence"])
                row["latitude"]  = float(row["latitude"])  if row.get("latitude")  else None
                row["longitude"] = float(row["longitude"]) if row.get("longitude") else None
                rows.append(row)
        return rows

    def group_by_case(self):
        cases = defaultdict(list)
        for r in self.rows:
            cases[r["case_id"]].append(r)
        for cid in cases:
            cases[cid].sort(key=lambda x: x["stop_sequence"])
        return dict(cases)

    def parse_ts(self, ts):
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S+00:00", "%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(ts.split("+")[0], fmt)
            except ValueError:
                continue
        raise ValueError(f"Unparseable timestamp: {ts!r}")

    def compute_edges(self):
        edges = []
        for case_id, stops in self.cases.items():
            route_id = stops[0]["route_id"]
            for i in range(len(stops) - 1):
                src, tgt = stops[i], stops[i + 1]
                try:
                    dur_sec = (self.parse_ts(tgt["arrival_time"]) - self.parse_ts(src["departure_time"])).total_seconds()
                    dur_sec = max(dur_sec, 0)
                except Exception:
                    dur_sec = 0
                edges.append({
                    "from_stop": src["stop_name"], "to_stop": tgt["stop_name"],
                    "route_id": route_id, "duration_sec": dur_sec, "case_id": case_id,
                })
        return edges

    def aggregate_edges(self, edges):
        agg = {}
        for e in edges:
            key = (e["from_stop"], e["to_stop"], e["route_id"])
            agg.setdefault(key, {"durations": [], "cases": set()})
            agg[key]["durations"].append(e["duration_sec"])
            agg[key]["cases"].add(e["case_id"])
        result = []
        for (frm, to, rid), data in agg.items():
            durs = data["durations"]
            avg = sum(durs) / len(durs)
            result.append({
                "from_stop": frm, "to_stop": to, "route_id": rid,
                "avg_sec": avg, "min_sec": min(durs), "max_sec": max(durs),
                "case_count": len(data["cases"]), "label": self._fmt_duration(avg),
            })
        return result

    def _fmt_duration(self, sec):
        sec = int(sec)
        m, s = divmod(sec, 60)
        return f"{m} min {s:02d} sec" if m > 0 else f"{s} sec"

    def compute_throughput(self):
        results = []
        for case_id, stops in self.cases.items():
            try:
                dur = (self.parse_ts(stops[-1]["departure_time"]) - self.parse_ts(stops[0]["arrival_time"])).total_seconds()
                results.append({
                    "case_id": case_id, "route_id": stops[0]["route_id"],
                    "duration_sec": dur, "duration_str": self._fmt_duration(dur),
                    "start_time": self.parse_ts(stops[0]["arrival_time"]).strftime("%H:%M:%S"),
                    "end_time":   self.parse_ts(stops[-1]["departure_time"]).strftime("%H:%M:%S"),
                })
            except Exception:
                pass
        return results

    def throughput_summary(self, throughput):
        if not throughput:
            return {"avg": "N/A", "min": "N/A", "max": "N/A"}
        durs = [t["duration_sec"] for t in throughput]
        return {
            "avg": self._fmt_duration(sum(durs) / len(durs)),
            "min": self._fmt_duration(min(durs)),
            "max": self._fmt_duration(max(durs)),
        }

    def detect_bottlenecks(self, agg_edges, threshold_multiplier=1.5):
        if not agg_edges:
            return agg_edges
        global_mean = sum(e["avg_sec"] for e in agg_edges) / len(agg_edges)
        threshold = global_mean * threshold_multiplier
        for e in agg_edges:
            e["is_bottleneck"] = e["avg_sec"] > threshold
        return sorted(agg_edges, key=lambda x: x["avg_sec"], reverse=True)

    def build_node_positions(self):
        positions = {}
        for r in self.rows:
            if r["stop_name"] not in positions and r["latitude"] and r["longitude"]:
                positions[r["stop_name"]] = (r["latitude"], r["longitude"])
        return positions

    def get_map_elements(self, route_id="All", threshold=1.5):
        nodes = []
        edges = []
        
        filtered_rows = [r for r in self.rows if route_id == "All" or r["route_id"] == route_id]
        stops_in_view = set(r["stop_name"] for r in filtered_rows)
        
        # Normalise Coords for Cytoscape (0 to 1000 scale)
        lats = [c[0] for c in self.node_coords.values()]
        lons = [c[1] for c in self.node_coords.values()]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        for stop in stops_in_view:
            lat, lon = self.node_coords.get(stop, (min_lat, min_lon))
            x = (lon - min_lon) / (max_lon - min_lon + 1e-9) * 1000
            y = 1000 - (lat - min_lat) / (max_lat - min_lat + 1e-9) * 1000
            nodes.append({
                'data': {'id': stop, 'label': stop},
                'position': {'x': x, 'y': y}
            })
            
        current_edges = [e for e in self.all_edges if route_id == "All" or e["route_id"] == route_id]
        current_edges = self.detect_bottlenecks(current_edges, threshold)
        
        for e in current_edges:
            edges.append({
                'data': {
                    'source': e['from_stop'], 
                    'target': e['to_stop'], 
                    'label': e['label'],
                    'avg_sec': e['avg_sec'],
                    'cases': e['case_count'],
                    'route': e['route_id'],
                    'is_bottleneck': e.get("is_bottleneck", False)
                }
            })
            
        return nodes + edges

    def get_stats(self, route_id="All", threshold=1.5):
        filtered_tp = [t for t in self.throughput_data if route_id == "All" or t["route_id"] == route_id]
        summary = self.throughput_summary(filtered_tp)
        
        current_edges = [e for e in self.all_edges if route_id == "All" or e["route_id"] == route_id]
        bottlenecks = [e for e in self.detect_bottlenecks(current_edges, threshold) if e.get("is_bottleneck")]
        
        return {
            "summary": summary,
            "bottlenecks": bottlenecks[:5] # Top 5
        }

    def get_available_routes(self):
        return sorted(list(set(r["route_id"] for r in self.rows)))
