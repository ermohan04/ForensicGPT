import gradio as gr
import os
from PIL import Image

# Folder where extracted images are saved
image_folder = "knowledgebase/images"


# Load image metadata from filenames assuming naming pattern
def load_images_metadata():
    images = []
    for filename in os.listdir(image_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            parts = filename.split("_")
            paper_id = parts[0]
            page = None
            spatter_type = None

            # Try to parse page and spatter type if possible
            for part in parts:
                if part.startswith("page"):
                    page = part.replace("page", "")
                # Check if part is a known spatter type with extension
                known_types = [
                    "passive_spatter.jpg",
                    "projected_spatter.jpg",
                    "cast_off_spatter.jpg",
                    "arterial_spurt.jpg",
                    "transfer_stain.jpg",
                    "unknown.jpg",
                ]
                if part in known_types:
                    spatter_type = part.replace(".jpg", "")

            # Fallback if not parsed properly
            if not spatter_type:
                spatter_type = filename.split(".")[-2].split("_")[-1]

            images.append(
                {
                    "filename": filename,
                    "paper_id": paper_id,
                    "page": page,
                    "spatter_type": spatter_type,
                    "path": os.path.join(image_folder, filename),
                }
            )
    return images


all_images = load_images_metadata()

# Get list of unique spatter types for filtering dropdown
spatter_types = sorted(set(img["spatter_type"] for img in all_images))
spatter_types.insert(0, "All")  # Add option to show all


def filter_images(spatter_type):
    if spatter_type == "All":
        filtered = all_images
    else:
        filtered = [img for img in all_images if img["spatter_type"] == spatter_type]

    # Prepare list of (image, caption) tuples for Gradio gallery
    gallery_data = []
    for img in filtered:
        image_obj = Image.open(img["path"])
        caption = f"{img['filename']} - Paper: {img['paper_id']} - Page: {img['page']} - Type: {img['spatter_type']}"
        gallery_data.append((image_obj, caption))
    return gallery_data


with gr.Blocks() as demo:
    gr.Markdown("# Blood Spatter Image Viewer")

    dropdown = gr.Dropdown(
        spatter_types,
        label="Filter by Blood Spatter Type",
        value="All",
        interactive=True,
    )

    # Create gallery without style() to avoid AttributeError
    gallery = gr.Gallery(label="Extracted Blood Spatter Images", show_label=True)

    # Set initial gallery images at launch
    gallery.value = filter_images("All")

    # Update gallery when dropdown value changes
    dropdown.change(fn=filter_images, inputs=dropdown, outputs=gallery)

if __name__ == "__main__":
    demo.launch()
