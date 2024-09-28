import pandas as pd
from translatepy import Translator
import os

def translate_posts():
    # Define the path to the input CSV file
    input_csv_file = '/workspaces/News_forum_analysis/combined_output.csv'

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(input_csv_file)

    # Initialize the Translator
    translator = Translator()

    # Function to handle the translation
    def translate_text(text):
        if pd.isna(text) or not isinstance(text, str) or text.strip() == "":
            return ""
        
        try:
            print(f"Translating: {text}")  # Debug output
            translation = translator.translate(text, destination_language="English")
            print(f"Translated: {translation.result}")  # Print the translated text
            return translation.result
        except Exception as e:
            print(f"Error translating text '{text}': {e}")  # Include the text that caused the error
            return text  # Return original text in case of error

    # Apply translation to the entire DataFrame
    df['translated_post_content'] = df['Post Content'].apply(translate_text)

    # Save the updated DataFrame back to the same CSV file
    df.to_csv(input_csv_file, index=False)

    print(f"Translated results added to {input_csv_file}")
