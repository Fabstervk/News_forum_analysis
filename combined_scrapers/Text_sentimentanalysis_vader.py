import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk


def Vaderanalysis ():

    # Download the VADER lexicon
    nltk.download('vader_lexicon')

    # Define the path to the input CSV file
    input_csv_file = '/workspaces/News_forum_analysis/combined_output.csv'  # Update to the correct CSV file

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(input_csv_file)

    # Initialize VADER Sentiment Analyzer
    sia = SentimentIntensityAnalyzer()

    # Function to get sentiment score using VADER
    def get_vader_sentiment(text):

        if pd.isna(text) or not isinstance(text, str) or text.strip() == "":
            return None  # Return None if the text is None, NaN, or empty
        
        
        return sia.polarity_scores(text)['compound']  # Returns a score between -1 (negative) and 1 (positive)

    # Calculate sentiment scores for the translated post content
    df['sentiment_score'] = df['translated_post_content'].apply(get_vader_sentiment)

    

    # Save the DataFrame with sentiment scores
    df.to_csv(input_csv_file, index=False)

    print(f"Sentiment scores saved to {input_csv_file}")
