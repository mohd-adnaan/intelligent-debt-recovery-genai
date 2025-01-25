import sys
import os
import streamlit as st
import pandas as pd
import json
import PyPDF2
from io import BytesIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml_models.profanity_detection.prediction import predict_profanity
from src.ml_models.privacy_compliance_detection.prediction import predict_privacy_compliance

# Configure page
st.set_page_config(
    page_title="Text Analytics Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with strict color scheme
st.markdown("""
<style>
    /* Base styles */
    .main {background-color: #f8f9fa; color: #000000;}  /* Light gray background */
    
    /* Boxes - Blue */
    .result-box {
        background-color: #e3f2fd !important;  /* Light blue */
        border: 2px solid #1976d2 !important;  /* Dark blue */
        color: #000000 !important;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Buttons - Orange (single color) */
    .stButton>button {
        background-color: #ff6f00 !important;  /* Dark orange */
        color: #ffffff !important;  /* White text */
        border: none;
        border-radius: 5px;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #ff8f00 !important;  /* Brighter orange on hover */
        transform: scale(1.02);
    }
    
    /* Dark background sections */
    .stSidebar {
        background-color: #1a237e !important;  /* Dark blue */
        color: #ffffff !important;
    }
    
    /* Input fields */
    .stTextArea textarea {background-color: #ffffff !important; color: #000000 !important;}
    .stTextInput input {background-color: #ffffff !important; color: #000000 !important;}
</style>
""", unsafe_allow_html=True)

def process_uploaded_file(uploaded_file):
    """Extract text from various file formats"""
    try:
        file_type = uploaded_file.type
        text = ""
        
        if file_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages])
            
        elif file_type in ["text/plain", "text/csv"]:
            text = uploaded_file.getvalue().decode("utf-8")
            
        elif file_type == "application/json":
            data = json.load(uploaded_file)
            text = json.dumps(data, indent=2)
            
        elif file_type in ["application/vnd.ms-excel", 
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            df = pd.read_excel(uploaded_file)
            text = df.to_string(index=False)
            
        return text.strip()
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def display_result(label, probability, threshold=0.5):
    """Styled result display based on prediction confidence"""
    if probability >= threshold * 100:
        box_class = "alert" if "Sensitive" in label else "warning"
    else:
        box_class = "safe"
    
    st.markdown(f"""
    <div class="result-box {box_class}">
        <strong>{label}</strong><br>
        Confidence: {probability:.2f}%
    </div>
    """, unsafe_allow_html=True)

# Sidebar File Upload
with st.sidebar:
    st.header("📁 File Upload")
    uploaded_file = st.file_uploader(
        "Upload documents (PDF/CSV/JSON/Excel/TXT)",
        type=["pdf", "csv", "json", "xlsx", "txt"],
        accept_multiple_files=False
    )

# Main Content
st.markdown("<h1 style='color: black;'>📊 Intelligent Debt Recovery GenAI</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='color: black;'>Enter text to analyze for profanity and privacy compliance.</h2>", unsafe_allow_html=True)

# Create columns for input/output layout
col1, col2 = st.columns([2, 1])

with col1:
    if uploaded_file:
        st.subheader("Uploaded Document Preview")
        file_info = f"""
        <div class="file-info">
            <strong>Filename:</strong> {uploaded_file.name}<br>
            <strong>Type:</strong> {uploaded_file.type}<br>
            <strong>Size:</strong> {uploaded_file.size//1024} KB
        </div>
        """
        st.markdown(file_info, unsafe_allow_html=True)
        
        extracted_text = process_uploaded_file(uploaded_file)
        if extracted_text:
            with st.expander("View Extracted Text"):
                st.text(extracted_text[:2000] + ("..." if len(extracted_text) > 2000 else ""))
    else:
        st.subheader("Direct Text Input")
        user_input = st.text_area("Enter text to analyze", height=200)

with col2:
    st.markdown("<h3 style='color: black;'>Analysis Results</h3>", unsafe_allow_html=True)
    
    if st.button("🚀 Run Analysis"):
        if uploaded_file:
            analysis_text = extracted_text[:5000] if extracted_text else ""
        else:
            analysis_text = user_input.strip()
            
        if analysis_text:
            # Profanity Analysis
            profanity_label, profanity_prob = predict_profanity(analysis_text)
            
            # Privacy Compliance Analysis
            privacy_label, privacy_prob = predict_privacy_compliance(analysis_text)
            
            # Display results
            st.markdown("<h2 style='color: black;'>Profanity Detection</h2>", unsafe_allow_html=True)
            display_result(profanity_label, profanity_prob)
            
            st.markdown("<h2 style='color: black;'>Privacy Compliance</h2>", unsafe_allow_html=True)
            display_result(privacy_label, privacy_prob)
            
            # Show text sample
            with st.expander("View Analyzed Text"):
                st.text(analysis_text[:1000] + ("..." if len(analysis_text) > 1000 else ""))
        else:
            st.warning("Please provide text input or upload a file with readable content")

