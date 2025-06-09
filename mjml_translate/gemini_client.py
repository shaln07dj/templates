import os
from gemini_sdk import Client, types  # Replace with your actual Gemini client import

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = Client(api_key=API_KEY)
