"""
task2_xes.py — Converts routes.csv to XES event log
"""
import pandas as pd
import pm4py
from pathlib import Path

def convert_csv_to_xes(csv_path, xes_path):
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # Convert arrival_time to datetime
    df['arrival_time'] = pd.to_datetime(df['arrival_time'])
    df['departure_time'] = pd.to_datetime(df['departure_time'])
    
    # pm4py expects certain column names or a mapping
    # Case ID: case_id
    # Activity: stop_name
    # Timestamp: arrival_time (or departure_time, we'll use arrival)
    
    event_log = pm4py.format_dataframe(
        df, 
        case_id='case_id', 
        activity_key='stop_name', 
        timestamp_key='arrival_time'
    )
    
    # Export to XES
    pm4py.write_xes(event_log, xes_path)
    print(f"Successfully converted {csv_path} to {xes_path}")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / "data" / "routes.csv"
    xes_path = root_dir / "data" / "event_log.xes"
    
    if csv_path.exists():
        convert_csv_to_xes(str(csv_path), str(xes_path))
    else:
        print(f"Error: {csv_path} not found. Run Task 1 first.")
