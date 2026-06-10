"""Тесты чанкинга."""

from app.chunker import chunk_document, chunk_text, split_paragraphs


def test_split_paragraphs_drops_empty():
    text = "Para one.\n\n\n\nPara two."
    assert split_paragraphs(text) == ["Para one.", "Para two."]


def test_chunk_text_respects_max_chars():
    long = "x" * 1200
    chunks = chunk_text(long, max_chars=500, overlap=50)
    assert len(chunks) >= 3
    assert all(len(c) <= 500 for c in chunks)


def test_chunk_document_keeps_doc_id():
    doc = {"doc_id": "dsld-1", "name": "Test Shot",
           "text": "Header part.\n\nIngredients: vitamin C 1000 mg."}
    chunks = chunk_document(doc)
    assert len(chunks) == 2
    assert all(c["doc_id"] == "dsld-1" for c in chunks)
    assert chunks[0]["chunk_id"] == "dsld-1-0"
