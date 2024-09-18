import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# Define the path to the input CSV file
input_csv_file = '/workspaces/News_forum_analysis/translated_flashback_forum_posts_20240918_111512.csv'  # Update to the correct CSV file

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(input_csv_file)

# Load FINBERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
model = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')

# Function to calculate sentiment score using FINBERT
def get_sentiment_score(text):
    if text is None or text.strip() == "":
        return None  # Return None if the text is None or empty
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = outputs.logits.softmax(dim=1).numpy()[0]  # Get the softmax probabilities
    return scores[2] - scores[0]  # Neutral - Negative to get a score between -1 (negative) and 1 (positive)

# Calculate sentiment scores for the translated post content
df['sentiment_score'] = df['translated_post_content'].apply(get_sentiment_score)

# Generate a new output CSV file name based on the current time
output_csv_file = f'/workspaces/News_forum_analysis/translated_flashback_forum_posts_with_finbert_sentiment_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv'

# Save the DataFrame with sentiment scores
df.to_csv(output_csv_file, index=False)

print(f"Sentiment scores saved to {output_csv_file}")
