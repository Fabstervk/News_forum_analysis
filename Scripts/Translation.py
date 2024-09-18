import pandas as pd
from translatepy import Translator
import os

# Define the path to the input CSV file
input_csv_file = '/workspaces/News_forum_analysis/flashback_forum_posts.csv'

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(input_csv_file)

# Initialize the Translator
translator = Translator()

# Function to handle the translation
def translate_text(text):
    if text is None or text.strip() == "":
        return ""  # Return empty string if the text is None or empty
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

# Generate a new output CSV file name based on the current time
output_csv_file = f'/workspaces/News_forum_analysis/translated_flashback_forum_posts_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv'

# Save the translated DataFrame
df.to_csv(output_csv_file, index=False)

print(f"Translated results saved to {output_csv_file}")
