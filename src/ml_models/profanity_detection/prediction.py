import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import load_model
import pickle

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

# Load resources
model = load_model('src/ml_models/profanity_detection/profanity.keras')
with open('src/ml_models/profanity_detection/tfidf_vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

def predict_profanity(text):
    processed = preprocess_text(text)
    features = vectorizer.transform([processed]).toarray()
    pred = model.predict(features)[0][0]
    return ("profane", pred*100) if pred > 0.5 else ("not profane", (1-pred)*100)