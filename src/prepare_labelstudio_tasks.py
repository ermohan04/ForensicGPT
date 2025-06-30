import json

# Load the existing mapping of images to text chunks
with open("knowledgebase/image_text_links.json", "r", encoding="utf-8") as f:
    image_text_map = json.load(f)

# Prepare list of Label Studio tasks
tasks = []
for item in image_text_map:
    task = {
        "data": {
            "image": item["image"],  # Path to image file
            "text_context": item["text_chunk"],  # Related text chunk for context
        }
    }
    tasks.append(task)

# Save tasks in Label Studio import format
with open("knowledgebase/labelstudio_tasks.json", "w", encoding="utf-8") as f:
    json.dump(tasks, f, indent=2, ensure_ascii=False)

print(f"Saved {len(tasks)} tasks to knowledgebase/labelstudio_tasks.json")
