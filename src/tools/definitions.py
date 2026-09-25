from src.services.rag import search_my_docs as rag_search


def add_note(text: str) -> str:
    """Сохранить заметку пользователя для последующего поиска.

    Args:
        text: Текст заметки
    """
    return f"Заметка сохранена: {text}"


def search_notes(query: str = "") -> str:
    """Найти ранее сохранённые заметки пользователя по смыслу запроса.

    Args:
        query: Необязательный поисковый запрос или ключевые слова
    """
    return "Поиск заметок..."


def search_my_docs(query: str) -> str:
    """Найти информацию в загруженных пользователем документах и базе знаний.

    Args:
        query: Поисковый запрос для поиска по документам
    """
    return rag_search(query)


def delete_note(text: str) -> str:
    """Удалить ранее сохраненную заметку по её тексту или ключевым словам.

    Args:
        text: Текст или часть текста заметки для удаления
    """
    return text


# Экспортируем список функций как инструменты для Gemini
TOOLS = [add_note, search_notes, search_my_docs, delete_note]
