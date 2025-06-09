# mjml_translate/gemini_client.py
import os
from google import genai
from google.genai import types # <--- 'types' is imported here but not explicitly exported as a name

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=API_KEY) # <--- 'client' is defined here