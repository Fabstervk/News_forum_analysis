import pandas as pd
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

# Define the path to the input CSV file
input_csv_file = '/workspaces/News_forum_analysis/Output/Translated_flashback_content.csv'  # Update to the correct CSV file

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(input_csv_file)

# Load DistilBERT model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)  # Adjust num_labels based on your task

# Function to calculate sentiment score using DistilBERT
def get_distilbert_sentiment(text):
    if text is None or text.strip() == "":
        return None  # Return None if the text is None or empty
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Get the softmax probabilities
    scores = outputs.logits.softmax(dim=1).detach().numpy()[0]
    # Return the sentiment score: Positive (1) - Negative (0)
    return scores[1] - scores[0]  # Adjust based on how your labels are set up

# Calculate sentiment scores for the translated post content
df['sentiment_score'] = df['translated_post_content'].apply(get_distilbert_sentiment)

# Generate a new output CSV file name based on the current time
output_csv_file = f'/workspaces/News_forum_analysis/translated_flashback_forum_posts_with_distilbert_sentiment_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv'

# Save the DataFrame with sentiment scores
df.to_csv(output_csv_file, index=False)

print(f"Sentiment scores saved to {output_csv_file}")
