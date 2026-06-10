"""Нарезка документов на чанки по абзацам с ограничением размера и перекрытием."""

from app.config import MAX_CHARS, OVERLAP


def split_paragraphs(text):
    """Разбивает текст на абзацы по пустым строкам."""
    parts = [p.strip() for p in text.split("\n\n")]
    return [p for p in parts if p]


def _split_long(paragraph, max_chars, overlap):
    """Режет слишком длинный абзац на куски max_chars с перекрытием overlap."""
    if len(paragraph) <= max_chars:
        return [paragraph]
    pieces = []
    start = 0
    step = max(1, max_chars - overlap)
    while start < len(paragraph):
        pieces.append(paragraph[start:start + max_chars])
        start += step
    return pieces


def chunk_text(text, max_chars=MAX_CHARS, overlap=OVERLAP):
    """Возвращает список чанков (строк) для одного документа."""
    chunks = []
    for para in split_paragraphs(text):
        chunks.extend(_split_long(para, max_chars, overlap))
    return chunks


def chunk_document(document, max_chars=MAX_CHARS, overlap=OVERLAP):
    """Превращает документ {doc_id, name, text, ...} в список чанков-словарей."""
    result = []
    pieces = chunk_text(document.get("text", ""), max_chars, overlap)
    for i, piece in enumerate(pieces):
        result.append({
            "chunk_id": f"{document['doc_id']}-{i}",
            "doc_id": document["doc_id"],
            "name": document.get("name", ""),
            "source_file": document.get("source_file", ""),
            "text": piece,
        })
    return result
