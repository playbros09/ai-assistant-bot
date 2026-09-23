from google import genai
from google.genai.errors import APIError, ServerError

from src.bot.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

SYSTEM_INSTRUCTION = "Ты — личный ассистент. Отвечай кратко и по делу, на русском."

_chats: dict = {}


def get_or_create_chat(user_id: int):
    if user_id not in _chats:
        _chats[user_id] = client.chats.create(
            model="gemini-3.6-flash", config={"system_instruction": SYSTEM_INSTRUCTION}
        )
    return _chats[user_id]


async def ask_ai(user_id: int, user_message: str) -> str:
    try:
        chat = get_or_create_chat(user_id)
        response = chat.send_message(user_message)
        return response.text
    except ServerError:
        return (
            "Сервер временно перегружен. Пожалуйста, повтори запрос через пару секунд."
        )
    except APIError as e:
        return f"Произошла ошибка при обращении к модели. Попробуй ещё раз. (Код: {e.code})"
    except (TimeoutError, ConnectionError):
        return "Проблемы с подключением к сети. Проверь интернет-соединение."
