import fitz  # PyMuPDF
import os

# Folder where your PDF papers are stored
input_folder = "knowledgebase/papers"

# Folder to save extracted text files
output_folder = "knowledgebase/texts"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)


def extract_text_from_pdf(pdf_path):
    """
    Extract full text from a PDF,
    while keeping track of page breaks by inserting a page delimiter.
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text()
        # Add a marker to indicate page breaks for later splitting
        full_text += f"\n\n--- PAGE {page_num} ---\n\n"
        full_text += page_text
    return full_text


# Process each PDF file in the input folder
for pdf_file in os.listdir(input_folder):
    if pdf_file.lower().endswith(".pdf"):
        pdf_path = os.path.join(input_folder, pdf_file)
        text = extract_text_from_pdf(pdf_path)
        text_filename = os.path.splitext(pdf_file)[0] + ".txt"
        with open(
            os.path.join(output_folder, text_filename), "w", encoding="utf-8"
        ) as f:
            f.write(text)
        print(f"Extracted text with page markers from {pdf_file} to {text_filename}")
