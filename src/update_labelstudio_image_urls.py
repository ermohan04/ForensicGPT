import json

# Path to your existing labelstudio_tasks.json file
input_json_path = "knowledgebase/labelstudio_tasks.json"

# Path to save the updated JSON file
output_json_path = "knowledgebase/labelstudio_tasks_with_urls.json"

# Base URL where your images are served from
base_url = "http://localhost:8000/images/"

# Load existing tasks
with open(input_json_path, "r", encoding="utf-8") as f:
    tasks = json.load(f)

# Update image URLs
for task in tasks:
    # Original image path: e.g. knowledgebase/images/7_page5_img1.jpeg
    original_path = task.get("data", {}).get("image", "")
    # Extract just the filename (last part)
    filename = original_path.split("/")[-1]
    # Replace with full URL
    task["data"]["image"] = base_url + filename

# Save updated tasks
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(tasks, f, indent=2, ensure_ascii=False)

print(f"Updated tasks saved to {output_json_path}")
