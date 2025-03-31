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
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

# Print the response
print(response.choices[0].message.content)