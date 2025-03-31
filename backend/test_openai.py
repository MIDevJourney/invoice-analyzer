import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Set up the OpenAI client
client = openai.OpenAI(api_key=api_key)

# Make a test API call
response = client.chat.completions.create(
    model="gpt-4",  # Use a model you have access to
    messages=[
        {"role": "user", "content": "Extract the invoice number and total amount from this text: 'Invoice #12345, Date: 2025-03-31, Total: $500.00'"}
    ]
)

# Print the response
print(response.choices[0].message.content)