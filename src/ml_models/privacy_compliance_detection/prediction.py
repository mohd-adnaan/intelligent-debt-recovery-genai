import numpy as np
import re
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import pickle

# Load the pre-trained privacy compliance detection model
model = load_model('src/ml_models/privacy_compliance_detection/privacy_compliance_lstm_model.keras')

# Load the tokenizer (assuming it was saved during training)
with open('src/ml_models/privacy_compliance_detection/tokenizer.pkl', 'wb') as f:
    tokenizer = pickle.load(f)

# Preprocessing function
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    
    # Lemmatization (simple rule-based)
    lemmatized = []
    for word in text.split():
        if word.endswith('ing'): word = word[:-3]
        elif word.endswith('ed'): word = word[:-2]
        elif word.endswith('s'): word = word[:-1]
        lemmatized.append(word)
    
    # Remove stop words
    stop_words = {"the", "and", "is", "in", "it", "to", "of", 
                 "for", "with", "on", "at", "by", "this", "that"}
    return " ".join([word for word in lemmatized if word not in stop_words])

def predict_privacy_compliance(text):
    # Step 1: Preprocess the input text
    processed_text = preprocess_text(text)
    
    # Step 2: Tokenize and pad the text
    sequence = tokenizer.texts_to_sequences([processed_text])
    padded_sequence = pad_sequences(sequence, maxlen=100, padding="post")
    
    # Step 3: Make a prediction using the trained model
    pred = model.predict(padded_sequence)[0][0]
    
    # Step 4: Interpret the prediction
    label = "Sensitive Info Shared Without Verification" if pred > 0.5 else "No Issue"
    probability = pred * 100 if label == "Sensitive Info Shared Without Verification" else (1 - pred) * 100
    
    return label, probability