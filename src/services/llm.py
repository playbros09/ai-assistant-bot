from google import genai
from google.genai.errors import APIError, ServerError

from src.bot.config import settings
from src.services.db import Message, Note, SessionLocal
from src.tools.definitions import TOOLS, search_my_docs

client = genai.Client(api_key=settings.gemini_api_key)

SYSTEM_INSTRUCTION = "Ты — личный ассистент. Отвечай кратко и по делу, на русском."


def execute_tool(user_id: int, name: str, tool_input: dict) -> str:
    """Реальное выполнение инструментов с сохранением/чтением из БД и RAG."""
    with SessionLocal() as session:
        if name == "add_note":
            text = tool_input.get("text") or tool_input.get("query", "")
            session.add(Note(user_id=user_id, text=text))
            session.commit()
            return "Заметка сохранена."

        if name == "search_notes":
            notes = session.query(Note).filter_by(user_id=user_id).all()
            if not notes:
                return "Заметок пока нет."
            return "\n".join(f"- {n.text}" for n in notes)

        if name == "search_my_docs":
            query = tool_input.get("query", "")
            return search_my_docs(query)
            if name == "delete_note":
                query_text = tool_input.get("text", "").strip()
                # Ищем и удаляем заметки пользователя, содержащие этот текст
                notes_to_delete = (
                    session.query(Note)
                    .filter(Note.user_id == user_id, Note.text.ilike(f"%{query_text}%"))
                    .all()
                )
                if not notes_to_delete:
                    return "Не удалось найти такую заметку для удаления."
                for note in notes_to_delete:
                    session.delete(note)
            session.commit()
            return f"Заметка(и) успешно удалена(ы): {query_text}"

        return "Неизвестный инструмент."


def load_history(user_id: int) -> list[dict]:
    """Загрузка истории сообщений из базы данных."""
    with SessionLocal() as session:
        rows = (
            session.query(Message).filter_by(user_id=user_id).order_by(Message.id).all()
        )
        return [{"role": r.role, "content": r.content} for r in rows[-20:]]


def save_message(user_id: int, role: str, content: str):
    """Сохранение сообщения в базу данных."""
    with SessionLocal() as session:
        session.add(Message(user_id=user_id, role=role, content=content))
        session.commit()


_chats: dict = {}


def get_or_create_chat(user_id: int):
    if user_id not in _chats:
        # Загружаем предыдущую историю из БД при создании сессии чата
        history = load_history(user_id)  # noqa: F841
        # Переводим историю в формат, который принимает Google GenAI если нужно,
        # либо создаем чат с текущими инструментами
        _chats[user_id] = client.chats.create(
            model="gemini-3.6-flash",
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "tools": TOOLS,
            },
        )
    return _chats[user_id]


async def ask_ai(user_id: int, user_message: str) -> str:
    try:
        # Сохраняем сообщение пользователя в БД
        save_message(user_id, role="user", content=user_message)

        chat = get_or_create_chat(user_id)
        response = chat.send_message(user_message)

        # Если модель вызывает инструмент, обрабатываем его с передачей user_id
        if response.function_calls:
            for function_call in response.function_calls:
                name = function_call.name
                args = function_call.args

                tool_result = execute_tool(user_id, name, args)
                response = chat.send_message(tool_result)

        reply_text = response.text

        # Сохраняем ответ ассистента в БД
        save_message(user_id, role="model", content=reply_text)

        return reply_text
    except ServerError:
        return (
            "Сервер временно перегружен. Пожалуйста, повтори запрос через пару секунд."
        )
    except APIError as e:
        return f"Произошла ошибка при обращении к модели. Попробуй ещё раз. (Код: {e.code})"
    except (TimeoutError, ConnectionError):
        return "Проблемы с подключением к сети. Проверь интернет-соединение."
