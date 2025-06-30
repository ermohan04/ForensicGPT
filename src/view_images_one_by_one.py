import gradio as gr
import os
from PIL import Image

# Folder where extracted images are saved
image_folder = "knowledgebase/images"


def load_images_metadata():
    images = []
    for filename in os.listdir(image_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            parts = filename.split("_")
            paper_id = parts[0]
            page = None
            spatter_type = None

            for part in parts:
                if part.startswith("page"):
                    page = part.replace("page", "")
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
spatter_types = sorted(set(img["spatter_type"] for img in all_images))
spatter_types.insert(0, "All")


def filter_images(spatter_type):
    if spatter_type == "All":
        filtered = all_images
    else:
        filtered = [img for img in all_images if img["spatter_type"] == spatter_type]
    return filtered


def show_image_by_index(image_list, index):
    # Wrap index within bounds
    if not image_list:
        return None, "No images to display.", index
    index = max(0, min(index, len(image_list) - 1))
    img_info = image_list[index]
    img_obj = Image.open(img_info["path"])
    caption = f"{img_info['filename']} - Paper: {img_info['paper_id']} - Page: {img_info['page']} - Type: {img_info['spatter_type']}"
    return img_obj, caption, index


with gr.Blocks() as demo:
    gr.Markdown("# Blood Spatter Image Viewer ")

    dropdown = gr.Dropdown(
        spatter_types,
        label="Filter by Blood Spatter Type",
        value="All",
        interactive=True,
    )

    image_display = gr.Image(label="Image", type="pil")
    caption_display = gr.Label()
    prev_btn = gr.Button("Previous")
    next_btn = gr.Button("Next")

    # Store filtered images and current index in state variables
    state_images = gr.State(all_images)
    state_index = gr.State(0)

    def on_filter_change(selected_type, current_index):
        filtered = filter_images(selected_type)
        if not filtered:
            return None, "No images found for this filter.", [], 0
        return (
            Image.open(filtered[0]["path"]),
            f"{filtered[0]['filename']} - Paper: {filtered[0]['paper_id']} - Page: {filtered[0]['page']} - Type: {filtered[0]['spatter_type']}",
            filtered,
            0,
        )

    def on_next(filtered_images, current_index):
        if not filtered_images:
            return None, "No images available.", current_index
        new_index = (current_index + 1) % len(filtered_images)
        img_info = filtered_images[new_index]
        img_obj = Image.open(img_info["path"])
        caption = f"{img_info['filename']} - Paper: {img_info['paper_id']} - Page: {img_info['page']} - Type: {img_info['spatter_type']}"
        return img_obj, caption, new_index

    def on_prev(filtered_images, current_index):
        if not filtered_images:
            return None, "No images available.", current_index
        new_index = (current_index - 1) % len(filtered_images)
        img_info = filtered_images[new_index]
        img_obj = Image.open(img_info["path"])
        caption = f"{img_info['filename']} - Paper: {img_info['paper_id']} - Page: {img_info['page']} - Type: {img_info['spatter_type']}"
        return img_obj, caption, new_index

    # When dropdown changes, update images and reset index
    dropdown.change(
        on_filter_change,
        inputs=[dropdown, state_index],
        outputs=[image_display, caption_display, state_images, state_index],
    )

    # Next button moves forward
    next_btn.click(
        on_next,
        inputs=[state_images, state_index],
        outputs=[image_display, caption_display, state_index],
    )

    # Previous button moves backward
    prev_btn.click(
        on_prev,
        inputs=[state_images, state_index],
        outputs=[image_display, caption_display, state_index],
    )

    # Initial load (all images, index 0)
    demo.load(
        fn=show_image_by_index,
        inputs=[state_images, state_index],
        outputs=[image_display, caption_display, state_index],
    )


if __name__ == "__main__":
    demo.launch()
