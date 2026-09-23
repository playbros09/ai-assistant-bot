from google import genai

from src.bot.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Привет! Кто ты?",
)

print("Ответ модели:", response.text)
