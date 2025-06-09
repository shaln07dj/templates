import os
from google.generativeai import Client, types  # Adjust import to your actual Gemini SDK

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = Client(api_key=API_KEY)
