import os
import json
import pandas as pd
import re

# Path to the directory containing JSON files
data_dir = "/Users/mohammadadnaan/Downloads/Prodigal_Tech/intelligent-debt-recovery-genai/data"

# List to store annotated data
annotated_data = []

# Function to normalize text
def normalize_text(text):
    """
    Normalizes text by:
    1. Converting to lowercase.
    2. Removing special characters except apostrophes and hyphens.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters except apostrophes and hyphens
    text = re.sub(r"[^a-zA-Z0-9\s'-]", "", text)
    
    return text

# Iterate over all JSON files
for filename in os.listdir(data_dir):
    if filename.endswith(".json"):
        file_path = os.path.join(data_dir, filename)

        # Load and parse the JSON file
        with open(file_path, "r") as file:
            conversation = json.load(file)

        # Annotate each utterance with label = 0 by default
        for utterance in conversation:
            text = utterance["text"]
            speaker = utterance["speaker"]  # Extract speaker information
            normalized_text = normalize_text(text)  # Normalize the text
            annotated_data.append({
                "text": normalized_text,
                "label": 0,  # Default label is 0
                "speaker": speaker  # Add speaker information
            })

# Save annotated data to an Excel file
df = pd.DataFrame(annotated_data)
df.to_excel("profanity_data_new.xlsx", index=False)
print("Annotated data saved to profanity_data_new.xlsx")