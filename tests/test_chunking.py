from src.services.rag import chunk_text


def test_chunk_text_basic():
    text = "a" * 1200
    chunks = chunk_text(text, size=500, overlap=50)
    assert len(chunks) == 3
    assert all(len(c) <= 500 for c in chunks)
