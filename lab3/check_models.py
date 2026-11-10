import os
from dotenv import load_dotenv
import google.generativeai as genai

# Завантажуємо ключ
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Доступні моделі для генерації тексту:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Помилка доступу: {e}")