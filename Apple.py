import spacy
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from fpdf import FPDF
import PyPDF2
from collections import Counter

# Load English NLP model
nlp = spacy.load("en_core_web_sm")


def process_text(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    threats = [ent.text for ent in doc.ents if ent.label_ in ["NORP", "LAW", "CRIME"]]
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    times = [ent.text for ent in doc.ents if ent.label_ == "TIME"]
    events = [ent.text for ent in doc.ents if ent.label_ == "EVENT"]

    results = {
        "Location Mentions": dict(Counter(locations)),
        "Organization Mentions": dict(Counter(organizations)),
        "Threat Indicators": list(set(threats)),
        "Dates Mentioned": list(set(dates)),
        "Times Mentioned": list(set(times)),
        "Events Mentioned": list(set(events))
    }
    return results


def save_results_to_pdf(results, output_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="Intelligence Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", style='B', size=12)
    for key, values in results.items():
        pdf.cell(200, 10, txt=key.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='L')
        pdf.set_font("Arial", size=10)
        if isinstance(values, dict):
            for item, count in values.items():
                pdf.multi_cell(0, 8, f"{item}: {count}".encode('latin-1', 'replace').decode('latin-1'))
        else:
            for value in values:
                pdf.multi_cell(0, 8, value.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)
        pdf.set_font("Arial", style='B', size=12)

    pdf.output(output_path, "F")


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text


def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")])
    if not file_path:
        return

    try:
        if file_path.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        results = process_text(text)
        pdf_path = os.path.join(os.getcwd(), "Intelligence_Report.pdf")
        save_results_to_pdf(results, pdf_path)
        messagebox.showinfo("Success", f"Intelligence Report saved to {pdf_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI setup
root = tk.Tk()
root.title("Intelligence File Analyzer")
root.geometry("350x200")

tk.Label(root, text="Upload a text or PDF file for intelligence analysis", wraplength=300).pack(pady=10)
tk.Button(root, text="Upload File", command=upload_file).pack(pady=20)
tk.Button(root, text="Exit", command=root.quit).pack(pady=10)

root.mainloop()