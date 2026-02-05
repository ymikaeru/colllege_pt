import google.generativeai as genai
import os

API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

try:
    for m in genai.list_models():
        print(f"name: {m.name}")
        print(f"description: {m.description}")
        print(f"supported_generation_methods: {m.supported_generation_methods}")
        print("---")
except Exception as e:
    print(f"Error listing models: {e}")
