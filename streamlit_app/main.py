import sys
import os
import streamlit as st

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml_models.profanity_detection.prediction import predict_profanity
from src.ml_models.privacy_compliance_detection.prediction import predict_privacy_compliance

# Streamlit app
st.title('Text Analysis Dashboard')
st.write('Enter text to analyze for profanity and privacy compliance.')

user_input = st.text_area("Input Text")

if st.button('Analyze'):
    # Profanity Detection
    profanity_label, profanity_prob = predict_profanity(user_input)
    st.success(f"Profanity Detection: {profanity_label} (confidence: {profanity_prob:.2f}%)")
    
    # Privacy Compliance Detection
    privacy_label, privacy_prob = predict_privacy_compliance(user_input)
    st.success(f"Privacy Compliance Detection: {privacy_label} (confidence: {privacy_prob:.2f}%)")
else:
    st.info("Please enter text and click 'Analyze'")