"""Поиск релевантных чанков: TF-IDF + косинусная близость, top-k."""

import json
import pickle

import numpy as np
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import linear_kernel

from app.config import (
    INDEX_CHUNKS_PATH,
    MATRIX_PATH,
    TOP_K,
    VECTORIZER_PATH,
)


def load_index():
    """Загружает векторизатор, матрицу и чанки из data/index/."""
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    matrix = load_npz(MATRIX_PATH)
    chunks = []
    with open(INDEX_CHUNKS_PATH, encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return vectorizer, matrix, chunks


def search(query, vectorizer, matrix, chunks, top_k=TOP_K):
    """Возвращает top-k чанков с полями text, doc_id, name, score."""
    q_vec = vectorizer.transform([query])
    # TF-IDF матрица L2-нормирована, поэтому скалярное произведение = косинус
    scores = linear_kernel(q_vec, matrix).flatten()
    order = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in order:
        ch = chunks[idx]
        results.append({
            "text": ch["text"],
            "doc_id": ch["doc_id"],
            "name": ch.get("name", ""),
            "score": float(scores[idx]),
        })
    return results
