import os
from google.generativeai import configure, GenerativeModel

API_KEY = os.getenv("GEMINI_API_KEY")
configure(api_key=API_KEY)

def get_gemini_client():
    return GenerativeModel("gemini-1.5-flash")