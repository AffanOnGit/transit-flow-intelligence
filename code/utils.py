"""
utils.py — Shared data-loading and analytics helpers
"""
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def load_routes(csv_path):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["stop_sequence"] = int(row["stop_sequence"])
            row["latitude"]  = float(row["latitude"])  if row.get("latitude")  else None
            row["longitude"] = float(row["longitude"]) if row.get("longitude") else None
            rows.append(row)
    return rows


def group_by_case(rows):
    cases = defaultdict(list)
    for r in rows:
        cases[r["case_id"]].append(r)
    for cid in cases:
        cases[cid].sort(key=lambda x: x["stop_sequence"])
    return dict(cases)


def parse_ts(ts):
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S+00:00", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(ts.split("+")[0], fmt)
        except ValueError:
            continue
    raise ValueError(f"Unparseable timestamp: {ts!r}")


def compute_edges(cases):
    edges = []
    for case_id, stops in cases.items():
        route_id = stops[0]["route_id"]
        for i in range(len(stops) - 1):
            src, tgt = stops[i], stops[i + 1]
            try:
                dur_sec = (parse_ts(tgt["arrival_time"]) - parse_ts(src["departure_time"])).total_seconds()
                dur_sec = max(dur_sec, 0)
            except Exception:
                dur_sec = 0
            edges.append({
                "from_stop": src["stop_name"], "to_stop": tgt["stop_name"],
                "route_id": route_id, "duration_sec": dur_sec, "case_id": case_id,
            })
    return edges


def aggregate_edges(edges):
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
            "case_count": len(data["cases"]), "label": _fmt_duration(avg),
        })
    return result


def _fmt_duration(sec):
    sec = int(sec)
    m, s = divmod(sec, 60)
    return f"{m} min {s:02d} sec" if m > 0 else f"{s} sec"


def compute_throughput(cases):
    results = []
    for case_id, stops in cases.items():
        try:
            dur = (parse_ts(stops[-1]["departure_time"]) - parse_ts(stops[0]["arrival_time"])).total_seconds()
            results.append({
                "case_id": case_id, "route_id": stops[0]["route_id"],
                "duration_sec": dur, "duration_str": _fmt_duration(dur),
                "start_time": parse_ts(stops[0]["arrival_time"]).strftime("%H:%M:%S"),
                "end_time":   parse_ts(stops[-1]["departure_time"]).strftime("%H:%M:%S"),
            })
        except Exception:
            pass
    return results


def throughput_summary(throughput):
    if not throughput:
        return {"avg": "N/A", "min": "N/A", "max": "N/A"}
    durs = [t["duration_sec"] for t in throughput]
    return {
        "avg": _fmt_duration(sum(durs) / len(durs)),
        "min": _fmt_duration(min(durs)),
        "max": _fmt_duration(max(durs)),
    }


def detect_bottlenecks(agg_edges, threshold_multiplier=1.5):
    if not agg_edges:
        return agg_edges
    global_mean = sum(e["avg_sec"] for e in agg_edges) / len(agg_edges)
    threshold = global_mean * threshold_multiplier
    for e in agg_edges:
        e["is_bottleneck"] = e["avg_sec"] > threshold
    return sorted(agg_edges, key=lambda x: x["avg_sec"], reverse=True)


def top_bottlenecks(agg_edges, n=3):
    return sorted(
        [e for e in agg_edges if e.get("is_bottleneck")],
        key=lambda x: x["avg_sec"], reverse=True
    )[:n]


def build_node_positions(rows):
    positions = {}
    for r in rows:
        if r["stop_name"] not in positions and r["latitude"] and r["longitude"]:
            positions[r["stop_name"]] = (r["latitude"], r["longitude"])
    return positions


def get_routes_for_stop(rows, stop_name):
    return sorted({r["route_id"] for r in rows if r["stop_name"] == stop_name})
