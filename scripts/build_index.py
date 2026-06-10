"""Полная сборка индекса: ingest -> chunk -> TF-IDF -> сохранение артефактов.

Создаёт:
  data/processed/documents.jsonl
  data/processed/chunks.jsonl
  data/index/chunks.jsonl
  data/index/vectorizer.pkl
  data/index/matrix.npz
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import pickle

from scipy.sparse import save_npz
from sklearn.feature_extraction.text import TfidfVectorizer

from app.chunker import chunk_document
from app.config import (
    CHUNKS_JSONL,
    DOCUMENTS_JSONL,
    INDEX_CHUNKS_PATH,
    INDEX_DIR,
    MATRIX_PATH,
    PROCESSED_DIR,
    VECTORIZER_PATH,
)
from scripts.ingest import main as run_ingest


def read_documents():
    docs = []
    with open(DOCUMENTS_JSONL, encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    return docs


def build_chunks(documents):
    chunks = []
    for doc in documents:
        chunks.extend(chunk_document(doc))
    return chunks


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    # 1. ingest
    run_ingest()

    # 2. chunk
    documents = read_documents()
    chunks = build_chunks(documents)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(CHUNKS_JSONL, chunks)
    write_jsonl(INDEX_CHUNKS_PATH, chunks)
    print(f"Чанков: {len(chunks)}")

    # 3. TF-IDF fit
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
    matrix = vectorizer.fit_transform(texts)

    # 4. сохранить
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    save_npz(MATRIX_PATH, matrix)

    print(f"Матрица: {matrix.shape[0]} чанков x {matrix.shape[1]} признаков")
    print(f"Индекс сохранён в {INDEX_DIR}")


if __name__ == "__main__":
    main()
