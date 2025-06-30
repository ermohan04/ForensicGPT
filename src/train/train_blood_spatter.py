# src/train/train_blood_spatter.py

"""
Example training script for blood spatter image classification or analysis.
This script loads images and labels, defines a model, trains it, and saves the model.
"""

import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.callbacks import ModelCheckpoint

# Define paths to data folders
DATA_DIR = Path("knowledgebase/images")  # Your images directory
LABELS_FILE = Path("knowledgebase/labels.csv")  # CSV file mapping images to labels

# Define output directory for saved model
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist


def load_data():
    """
    Load image filenames and labels from the CSV file.
    Return training and validation splits.
    """
    import pandas as pd

    df = pd.read_csv(LABELS_FILE)
    # Split dataset into train and validation sets (80/20 split)
    train_df, val_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["label"]
    )
    return train_df, val_df


def build_model(input_shape=(128, 128, 3), num_classes=4):
    """
    Define a simple CNN model for classification.
    """
    model = Sequential(
        [
            Conv2D(32, (3, 3), activation="relu", input_shape=input_shape),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation="relu"),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(128, activation="relu"),
            Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )
    return model


def main():
    # Load training and validation data info
    train_df, val_df = load_data()

    # Setup image data generators for real-time augmentation
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
    )
    val_datagen = ImageDataGenerator(rescale=1.0 / 255)

    # Create training and validation generators from dataframes
    train_generator = train_datagen.flow_from_dataframe(
        dataframe=train_df,
        directory=str(DATA_DIR),
        x_col="image_filename",
        y_col="label",
        target_size=(128, 128),
        batch_size=32,
        class_mode="categorical",
    )

    val_generator = val_datagen.flow_from_dataframe(
        dataframe=val_df,
        directory=str(DATA_DIR),
        x_col="image_filename",
        y_col="label",
        target_size=(128, 128),
        batch_size=32,
        class_mode="categorical",
    )

    # Build the CNN model
    model = build_model()

    # Setup checkpoint to save the best model
    checkpoint_path = MODEL_DIR / "best_model.h5"
    checkpoint = ModelCheckpoint(
        filepath=str(checkpoint_path),
        save_best_only=True,
        monitor="val_accuracy",
        mode="max",
    )

    # Train the model
    model.fit(
        train_generator,
        epochs=20,
        validation_data=val_generator,
        callbacks=[checkpoint],
    )

    print(f"Training complete. Best model saved at: {checkpoint_path}")


if __name__ == "__main__":
    main()
