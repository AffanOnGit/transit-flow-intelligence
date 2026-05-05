"""
task1_extraction.py — CDA PDF Extraction (with Fallback)
"""
import sys
import argparse
from pathlib import Path
import generate_sample_data

def main():
    parser = argparse.ArgumentParser(description="Extract CDA bus route data from PDFs.")
    parser.add_argument("--fallback", action="store_true", help="Use sample data generator instead of scraping.")
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    csv_path = script_dir.parent / "data" / "routes.csv"
    
    if args.fallback:
        print("Using fallback sample data generator...")
        generate_sample_data.generate_routes_csv(str(csv_path))
    else:
        # Placeholder for real scraping logic
        print("Real scraping logic not yet implemented. Use --fallback for now.")
        # In a real scenario, this would use requests and pdfplumber to scrape cda.gov.pk/cdaTransitMap
        pass

if __name__ == "__main__":
    main()
