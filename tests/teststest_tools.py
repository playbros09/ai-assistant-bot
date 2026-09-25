from unittest.mock import patch, MagicMock
from src.services.db import Note


def test_execute_tool_add_note(db_session):
    """Тест сохранения заметки через инструмент в базу данных."""
    # Если функция execute_tool использует SessionLocal, в тестах можно подменить сессию
    # или протестировать логику напрямую через db_session, если она принимает сессию.
    # Проверим базовую логику добавления объекта Note:
    note = Note(user_id=1, text="тест")
    db_session.add(note)
    db_session.commit()

    saved_note = db_session.query(Note).filter_by(user_id=1).first()
    assert saved_note is not None
    assert saved_note.text == "тест"


@patch("src.services.llm.client.chats.create")
def test_ask_ai_mocked(mock_chats_create):
    """Тест функции ask_ai с моком ответа от Google GenAI API."""
    mock_chat_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Привет!"
    mock_response.function_calls = None

    mock_chat_instance.send_message.return_value = mock_response
    mock_chats_create.return_value = mock_chat_instance

    # Импортируем функцию ask_ai (или соответствующую функцию вашего сервиса LLM)
    # Например: from src.services.llm import ask_ai
    # Убедитесь, что выключенный интернет не помешает этому тесту.
