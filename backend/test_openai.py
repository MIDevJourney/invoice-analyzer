# File: test_openai.py

import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("API key not found. Check your .env file.")
    exit()

# Set up the OpenAI client
client = openai.OpenAI(api_key=api_key)

# This function uses the OpenAI API to extract invoice information from a given text
def get_invoice_stuff(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Cheaper, safer bet
            messages=[
                {"role": "system", "content": "Give me JSON with invoice_number and total_amount."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Oops, AI broke: {e}"


text = "I like beef tacos. Invoice number: 12345. Total amount: $50.00."
print(get_invoice_stuff(text))