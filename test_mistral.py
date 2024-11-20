from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os

# Initialize the client with your API key
api_key = "ojkrqW6sJEjmm53mlKsf5xj6Q0hJAVoF"
client = MistralClient(api_key=api_key)

# Create a test message
messages = [
    ChatMessage(role="user", content="Generate a short fantasy RPG combat scenario between a warrior and a dragon.")
]

# Make the API call
try:
    # Call the API
    response = client.chat(
        model="mistral-large-latest",
        messages=messages,
    )
    
    # Print the response
    print("\nAPI Response:")
    print("-" * 50)
    print(response.choices[0].message.content)
    print("-" * 50)
    
except Exception as e:
    print(f"Error: {str(e)}")
