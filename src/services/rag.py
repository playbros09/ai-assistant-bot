import json
import sqlite3
from sentence_transformers import SentenceTransformer
import sqlite_vec

# Загружаем локальную мультиязычную модель для эмбеддингов
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Подключаемся к базе векторов и подключаем расширение sqlite-vec
conn = sqlite3.connect("vectors.db", check_same_thread=False)
conn.enable_load_extension(True)
sqlite_vec.load(conn)
conn.enable_load_extension(False)

# Создаем виртуальную таблицу для векторов (размерность 384) и таблицу для текстов
conn.execute(
    "CREATE VIRTUAL TABLE IF NOT EXISTS doc_chunks USING vec0(embedding float[384])"
)
conn.execute(
    "CREATE TABLE IF NOT EXISTS chunk_text(rowid INTEGER PRIMARY KEY, text TEXT)"
)
conn.commit()


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Разбивает текст на чанки фиксированной длины с перекрытием."""
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return chunks


def embed(texts: list[str]) -> list[list[float]]:
    """Генерирует локальные векторные эмбеддинги для списка текстов."""
    return model.encode(texts).tolist()


def index_chunks(chunks: list[str]) -> None:
    """Индексирует и сохраняет чанки вместе с их эмбеддингами в базу данных."""
    vectors = embed(chunks)
    for i, (text, vec) in enumerate(zip(chunks, vectors)):
        conn.execute(
            "INSERT INTO doc_chunks(rowid, embedding) VALUES (?, ?)",
            (i, json.dumps(vec)),
        )
        conn.execute(
            "INSERT OR REPLACE INTO chunk_text(rowid, text) VALUES (?, ?)",
            (i, text),
        )
    conn.commit()


def search_my_docs(query: str, top_k: int = 3) -> str:
    """Выполняет семантический поиск наиболее релевантных чанков по запросу."""
    q_vec = embed([query])[0]

    # KNN-поиск по векторной базе
    rows = conn.execute(
        "SELECT rowid, distance FROM doc_chunks WHERE embedding MATCH ? "
        "ORDER BY distance LIMIT ?",
        (json.dumps(q_vec), top_k),
    ).fetchall()

    if not rows:
        "По вашему запросу ничего не найдено."

    texts = [
        conn.execute("SELECT text FROM chunk_text WHERE rowid=?", (r[0],)).fetchone()[0]
        for r in rows
    ]
    return "\n---\n".join(texts)


# Пример для проверки (можно запустить как скрипт)
if __name__ == "__main__":
    sample_text = (
        "Дедлайн по проекту нашего Telegram-бота назначен на конец текущего месяца. "
        "Необходимо закончить интеграцию базы данных, настроить RAG и проверить все инструменты. "
        "В качестве локальной модели эмбеддингов используется paraphrase-multilingual-MiniLM-L12-v2."
    )

    chunks = chunk_text(sample_text)
    index_chunks(chunks)

    query = "когда дедлайн проекта?"
    print(f"Запрос: {query}\n")
    result = search_my_docs(query)
    print("Результат поиска:\n", result)
