from transformers import pipeline

# Load a pre-trained LLM
profanity_detector = pipeline("text-classification", model="fine-tuned-profanity-model")

# Example usage
text = "What the hell are you doing?"
result = profanity_detector(text)
print(result)  # Output: {'label': 'profane', 'score': 0.95}