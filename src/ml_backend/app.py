# src/ml_backend/app.py

"""
Simple FastAPI app to serve ML model predictions for blood spatter images.
Clients (e.g. chatbot) can send images, and get prediction results.
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import io
from PIL import Image

app = FastAPI(title="ForensicGPT ML Backend")

# Enable CORS to allow frontend/chatbot to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing, adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained model (update path as needed)
MODEL_PATH = "models/best_model.h5"
model = load_model(MODEL_PATH)

# Define class labels in same order as training
CLASS_LABELS = ["Passive Spatter", "Projected Spatter", "Transfer Spatter", "Other"]


def preprocess_image(image_bytes):
    """
    Load image bytes, resize and normalize it to feed to model.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((128, 128))  # Resize to model input size
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0  # Normalize pixel values to [0,1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array


@app.post("/predict")
async def predict(image_file: UploadFile = File(...)):
    """
    Receive an image file and return blood spatter type prediction.
    """
    image_bytes = await image_file.read()
    processed_img = preprocess_image(image_bytes)

    preds = model.predict(processed_img)
    pred_label = CLASS_LABELS[np.argmax(preds)]

    return {"prediction": pred_label, "confidence": float(np.max(preds))}


if __name__ == "__main__":
    import uvicorn

    # Run the app with hot reload for development
    uvicorn.run("src.ml_backend.app:app", host="0.0.0.0", port=8001, reload=True)
