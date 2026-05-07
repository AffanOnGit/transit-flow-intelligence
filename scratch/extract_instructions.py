import pdfplumber

with pdfplumber.open("PMS_Project.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    
    with open("project_instructions.txt", "w", encoding="utf-8") as f:
        f.write(text)
