import json  # To save results in JSON format
import os  # To work with file paths and directories
import re  # For regular expressions to parse filenames

# Define folder paths where texts and images are stored
texts_folder = "knowledgebase/texts"
images_folder = "knowledgebase/images"


def load_text_chunks_by_page(text_file):
    """
    Read a text file and split its content into pages using page markers.
    Returns a dictionary mapping page number to the text content of that page.
    """
    with open(text_file, "r", encoding="utf-8") as f:
        content = f.read()  # Read the entire content of the text file

    # Split content by page markers like '--- PAGE 2 ---'
    pages = content.split("--- PAGE ")
    page_texts = {}  # Dictionary to hold page number -> text chunk mapping

    # Skip first chunk as it may be before the first page marker
    for page in pages[1:]:
        try:
            # Separate page number and page text content
            page_num_str, text = page.split(" ---", 1)
            page_num = int(page_num_str.strip())  # Convert page number to integer
            page_texts[page_num] = text.strip()  # Store text chunk for this page number
        except Exception as e:
            print(f"Skipping malformed page chunk: {e}")  # Warn if format unexpected

    return page_texts  # Return the dictionary of page texts


# List to hold mappings of each image to its text chunk
image_text_map = []

# Loop through all files in the images folder
for image_filename in os.listdir(images_folder):
    # Consider only image files with these extensions
    if image_filename.endswith((".png", ".jpeg", ".jpg")):
        # Use regex to find the page number in the filename (e.g. 'page3')
        match = re.search(r"page(\d+)", image_filename)
        if not match:
            print(
                f"Skipping {image_filename}: no page number found"
            )  # Skip files with no page info
            continue

        page_num = int(match.group(1))  # Extract page number as integer

        # Extract paper ID as everything before '_page' in filename
        paper_id = image_filename.split("_page")[0]

        # Build path to corresponding text file for this paper ID
        text_file = os.path.join(texts_folder, f"{paper_id}.txt")

        # Check if text file exists
        if os.path.exists(text_file):
            # Load text chunks split by page for this paper
            page_texts = load_text_chunks_by_page(text_file)

            # Check if extracted page number is in the text chunks
            if page_num in page_texts:
                related_text = page_texts[page_num]  # Get text for this page

                # Append a dictionary with image, paper, page, and related text info
                image_text_map.append(
                    {
                        "image": os.path.join(images_folder, image_filename),
                        "page": page_num,
                        "paper_id": paper_id,
                        "text_chunk": related_text,
                    }
                )
            else:
                print(
                    f"No text for page {page_num} in {paper_id}.txt"
                )  # Page missing in text file
        else:
            print(f"Text file {text_file} not found.")  # Text file for paper ID missing

# After processing all images, save the image-text mapping to a JSON file
with open("knowledgebase/image_text_links.json", "w", encoding="utf-8") as json_file:
    json.dump(
        image_text_map, json_file, indent=2, ensure_ascii=False
    )  # Pretty-print JSON

print(
    f"Saved image-text mappings for {len(image_text_map)} images to knowledgebase/image_text_links.json"
)
