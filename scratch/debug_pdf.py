import pdfplumber
import requests
import tempfile
import os
import re

pdf_url = "https://cda.gov.pk/Assets/metro_transit_route/FR-01_Forward.pdf"
print(f"Downloading {pdf_url}...")
resp = requests.get(pdf_url)
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
    tmp.write(resp.content)
    tmp_path = tmp.name

print(f"Analyzing {tmp_path}...")
with pdfplumber.open(tmp_path) as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"--- Page {i} ---")
        text = page.extract_text()
        if text:
            # Regex to find: Stop Name followed by two HH:MM:SS times
            # Example: Nust Metro Station 08:00:00 08:00:00
            matches = re.findall(r'(.+?)\s+(\d{2}:\d{2}:\d{2})\s+(\d{2}:\d{2}:\d{2})', text)
            print(f"Regex matches found: {len(matches)}")
            for m in matches[:10]:
                print(f"  {m}")

os.unlink(tmp_path)
