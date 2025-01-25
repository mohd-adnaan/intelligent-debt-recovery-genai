import re
import os
import json
import pandas as pd
from typing import List, Dict

# Regex patterns for sensitive information
SENSITIVE_INFO_PATTERNS = {
    "balance": re.compile(r"\$\d+(,\d+)*(\.\d+)?"),  # Matches $450, $1,000, etc.
    "ssn": re.compile(r"\d{3}-\d{2}-\d{4}"),  # Matches SSNs like 123-45-6789
    "account_number": re.compile(r"\b\d{9,}\b"),  # Matches account numbers (9+ digits)
}

# VERIFICATION_QUESTIONS = [
#     #DOB
#     "Can you verify your date of birth?", 
#     "can you please verify your date of birth?", 
#     "Can you please verify your date of birth?",
#     "could you please verify your date of birth?",
#     "could you please verify your date of birth?",
#     "could you please confirm your date of birth for verification?",
#     "Can I verify your date of birth first?"
#     "What is your full date of birth?",
#     "Can you confirm your date of birth?",
#     "Can you please confirm your date of birth?",
#     "could you please confirm your date of birth?",
#     "Can you please verify your date of birth for me?",
#     "can you also provide your date of birth?",
#     "Can you please verify your date of birth for security purposes?",
#     "could you please confirm your date of birth for security purposes?",
#     "Could you please verify your date of birth for security purposes?",
#     "Can I get your date of birth to verify your identity?",
#     "Can you also confirm your date of birth?",
#     #SSN
#     "What is your social security number?",
#     "Can you provide the last four digits of your social security number?",
#     "Could you provide your full name and the last four digits of your Social Security number?",
#     "What are the last four digits of your SSN?",
#     "Can you confirm your social security number?",
#     #address
#     "Can you also confirm your current address?",
#     "could you also confirm your address?",
#     "Could you also confirm your current address?",
#     "Can you also confirm your current address for verification?",
#     "Can you also provide your current address for verification?",
#     "Can you confirm your address for verification?",
#     "Can you give me your address instead?",
#     "Can you also confirm your current address for security purposes?",
#     "Can you also confirm your address for security purposes?",
#     "Can you also confirm the address associated with your account?",
#     "Could you also confirm your current address for verification purposes?",
#     "Could you please confirm your address for verification purposes?",
#     "Can you also confirm your current address for security purposes?",
#     "Can I please verify your address?",
#     "Just verify your address so we can get this over with?"
#     "Could you also confirm your current address, please?",
#     "can you confirm your address for me?",
#     "Can you also confirm your current address for me?",
#     "What is your full address?",
#     "Can you confirm your address?",
#     "Can you verify your address on file?",
#     "What is your current address?",
#     "Can you provide your previous address?",
#     "Can you verify your zip code?",
#     #account
#     "Could you please confirm your identity for security purposes?",
#     "Can you provide more details about the account?",
#     "Can I have your account number to assist you?",
#     "What is your account number?",
#     "Can you confirm the phone number associated with your account?",
#     "What is your email address on file?",
#     "Can you verify your mother's maiden name?",
#     "What is your place of birth?",
#     "Can you confirm your driver's license number?",
#     "What is your employer’s name on file?"
# ]
# Keywords for identity verification
VERIFICATION_KEYWORDS = [
    "date of birth", "dob", "address", "current address", "social security number", 
    "ssn","account number", "account details", "identity", "verification", "security purpose"
]

# Function to detect sensitive information
def detect_sensitive_info(text: str) -> Dict[str, List[str]]:
    """
    Detects sensitive information in a given text using regex.
    Args:
        text (str): The text to analyze.
    Returns:
        Dict[str, List[str]]: A dictionary containing detected sensitive information.
    """
    sensitive_info = {key: [] for key in SENSITIVE_INFO_PATTERNS.keys()}
    for key, pattern in SENSITIVE_INFO_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            sensitive_info[key].extend(matches)
    return sensitive_info

# Function to check if identity verification occurs
def is_identity_verified(conversation: List[Dict], sensitive_utterance_index: int) -> bool:
    """
    Checks if identity verification occurs before sharing sensitive information.
    Args:
        conversation (List[Dict]): The conversation data.
        sensitive_utterance_index (int): Index of the utterance containing sensitive information.
    Returns:
        bool: True if identity verification occurs, False otherwise.
    """
    for i in range(sensitive_utterance_index):
        utterance = conversation[i]
        if utterance["speaker"] == "Agent":
            text = utterance["text"].lower()
            if any(keyword in text for keyword in VERIFICATION_KEYWORDS):
                print(f"Identity verification keyword detected: {text}")
                return True
    return False

# Function to analyze a conversation for compliance
def analyze_compliance(conversation: List[Dict]) -> Dict[str, List[str]]:
    """
    Analyzes a conversation for compliance with privacy rules.
    Args:
        conversation (List[Dict]): The conversation data.
    Returns:
        Dict[str, List[str]]: A dictionary containing non-compliant utterances.
    """
    non_compliant_utterances = []

    for i, utterance in enumerate(conversation):
        if utterance["speaker"] == "Agent":
            text = utterance["text"]
            sensitive_info = detect_sensitive_info(text)
            if any(sensitive_info.values()):  # If sensitive info is detected
                print(f"Sensitive info detected: {sensitive_info} in text: {text}")
                if not is_identity_verified(conversation, i):
                    non_compliant_utterances.append(text)

    return {"non_compliant_utterances": non_compliant_utterances}

# Function to process all JSON files for compliance analysis
def process_compliance_analysis(data_dir: str) -> pd.DataFrame:
    """
    Processes all JSON files in the specified directory and analyzes them for compliance.
    Args:
        data_dir (str): Path to the directory containing JSON files.
    Returns:
        pd.DataFrame: A DataFrame containing call IDs and compliance analysis results.
    """
    results = []

    # Iterate over all files in the directory
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(data_dir, filename)
            call_id = os.path.splitext(filename)[0]  # Extract call ID from filename

            # Load and parse the JSON file
            with open(file_path, "r") as file:
                try:
                    conversation = json.load(file)
                    print(f"Processing call ID: {call_id}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")
                    continue

            # Analyze the conversation for compliance
            compliance_result = analyze_compliance(conversation)

            # Append results
            results.append({
                "call_id": call_id,
                "non_compliant_utterances": compliance_result["non_compliant_utterances"]
            })

    # Convert results to a DataFrame
    return pd.DataFrame(results)

# Main function
if __name__ == "__main__":
    # Path to the directory containing JSON files
    data_dir = "/Users/mohammadadnaan/Downloads/Prodigal_Tech/intelligent-debt-recovery-genai/data"

    # Process all conversations for compliance analysis
    compliance_results_df = process_compliance_analysis(data_dir)

    # Save results to a CSV file
    output_file = "src/pattern_matching/privacy_compliance_detection/compliance_analysis_results.csv"
    compliance_results_df.to_csv(output_file, index=False)
    print(f"Compliance analysis results saved to {output_file}")