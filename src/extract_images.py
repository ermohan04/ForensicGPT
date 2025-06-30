import fitz  # PyMuPDF for PDF handling
import docx  # python-docx for Word documents
from PIL import Image, ImageDraw, ImageFont
import io
import os

# Define the folder where both PDFs and Word docs are stored
docs_folder = "knowledgebase/papers"
image_folder = "knowledgebase/images"
os.makedirs(image_folder, exist_ok=True)

# Known blood spatter types for quick filtering
KNOWN_SPATTER_TYPES = {
    "passive_spatter",
    "projected_spatter",
    "cast_off_spatter",
    "arterial_spurt",
    "transfer_stain",
}


# --- Utility: classify spatter type from text captions ---
def classify_spatter(caption_text):
    caption = caption_text.lower()
    if "passive" in caption:
        return "passive_spatter"
    elif "projected" in caption:
        return "projected_spatter"
    elif "cast-off" in caption or "cast off" in caption:
        return "cast_off_spatter"
    elif "arterial" in caption or "spurting" in caption:
        return "arterial_spurt"
    elif "transfer" in caption:
        return "transfer_stain"
    else:
        return "unknown"


# --- Utility: Add spatter type text at bottom of image ---
def add_text_to_image(image_bytes, text):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    draw = ImageDraw.Draw(image)
    font_size = max(12, image.width // 20)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    padding = 10
    new_height = image.height + text_height + padding
    new_img = Image.new("RGBA", (image.width, new_height), (255, 255, 255, 255))
    new_img.paste(image, (0, 0))
    draw = ImageDraw.Draw(new_img)
    rect_y0 = image.height
    rect_y1 = new_height
    draw.rectangle([(0, rect_y0), (image.width, rect_y1)], fill=(0, 0, 0, 180))
    text_x = (image.width - text_width) // 2
    text_y = rect_y0 + (padding // 2)
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
    output_buffer = io.BytesIO()
    new_img.convert("RGB").save(output_buffer, format="JPEG")
    return output_buffer.getvalue()


# --- Extract images from PDF ---
def extract_images_from_pdf(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    paper_id = os.path.splitext(os.path.basename(pdf_path))[0]
    saved_images = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        images = page.get_images(full=True)
        text_blocks = page.get_text("blocks")

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_ext = base_image["ext"]

            bbox = fitz.Rect(img[1], img[2], img[3], img[4])

            caption = ""
            # Heuristic: find text block below and near image for caption
            for block in text_blocks:
                block_rect = fitz.Rect(block[:4])
                if (
                    block_rect.y0 >= bbox.y1
                    and abs(block_rect.x0 - bbox.x0) < 150
                    and len(block[4].strip()) > 3
                ):
                    caption = block[4].strip()
                    break

            spatter_type = classify_spatter(caption)

            # Save image only if classified as known spatter type
            if spatter_type not in KNOWN_SPATTER_TYPES:
                continue

            img_bytes_with_text = add_text_to_image(img_bytes, spatter_type)

            img_name = (
                f"{paper_id}_page{page_num+1}_img{img_index+1}_{spatter_type}.jpg"
            )
            img_path = os.path.join(output_folder, img_name)

            with open(img_path, "wb") as f:
                f.write(img_bytes_with_text)

            saved_images.append(
                {
                    "path": img_path,
                    "type": spatter_type,
                    "paper_id": paper_id,
                    "page": page_num + 1,
                    "caption": caption,
                }
            )
    return saved_images


# --- Extract images from Word ---
def extract_images_from_word(doc_path, output_folder):
    doc = docx.Document(doc_path)
    paper_id = os.path.splitext(os.path.basename(doc_path))[0]
    saved_images = []
    paragraphs = doc.paragraphs
    num_paragraphs = len(paragraphs)
    image_counter = 0

    for i, para in enumerate(paragraphs):
        for run in para.runs:
            if run.element.xpath(".//pic:pic"):
                drawing = run.element.xpath(".//pic:pic")[0]
                embed = drawing.xpath(".//a:blip/@r:embed")[0]

                image_part = doc.part.related_parts[embed]
                img_bytes = image_part.blob

                caption = ""
                if i + 1 < num_paragraphs:
                    caption = paragraphs[i + 1].text.strip()

                spatter_type = classify_spatter(caption)

                # Save image only if classified as known spatter type
                if spatter_type not in KNOWN_SPATTER_TYPES:
                    continue

                img_bytes_with_text = add_text_to_image(img_bytes, spatter_type)

                image_counter += 1
                img_name = f"{paper_id}_img{image_counter}_{spatter_type}.jpg"
                img_path = os.path.join(output_folder, img_name)

                with open(img_path, "wb") as f:
                    f.write(img_bytes_with_text)

                saved_images.append(
                    {
                        "path": img_path,
                        "type": spatter_type,
                        "paper_id": paper_id,
                        "caption": caption,
                    }
                )

    return saved_images


# --- Main execution scanning PDFs and Word docs in the folder ---
all_images = []
for file_name in os.listdir(docs_folder):
    file_path = os.path.join(docs_folder, file_name)
    if file_name.lower().endswith(".pdf"):
        print(f"Processing PDF: {file_path}")
        extracted = extract_images_from_pdf(file_path, image_folder)
        all_images.extend(extracted)
    elif file_name.lower().endswith(".docx"):
        print(f"Processing Word doc: {file_path}")
        extracted = extract_images_from_word(file_path, image_folder)
        all_images.extend(extracted)

print(f"Total blood spatter images extracted: {len(all_images)}")
