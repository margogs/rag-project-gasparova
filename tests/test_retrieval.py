"""Тесты поиска и отказа на маленьком in-memory индексе."""

import pickle

import pytest
from sklearn.feature_extraction.text import TfidfVectorizer

from app.generator import generate_answer
from app.retriever import search

CHUNKS = [
    {"doc_id": "dsld-1", "name": "Immune Shot",
     "text": "Immune shot. Ingredients: vitamin C 1000 mg; zinc 15 mg."},
    {"doc_id": "dsld-2", "name": "Energy Shot",
     "text": "Energy shot. Ingredients: vitamin B6, B12, niacin."},
    {"doc_id": "dsld-3", "name": "Magnesium Shot",
     "text": "Calm shot. Ingredients: magnesium glycinate 200 mg."},
]


@pytest.fixture
def index():
    texts = [c["text"] for c in CHUNKS]
    vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix, CHUNKS


def test_relevant_query_has_positive_score(index):
    vectorizer, matrix, chunks = index
    results = search("vitamin C zinc immune", vectorizer, matrix, chunks, top_k=3)
    assert results[0]["score"] > 0
    assert results[0]["doc_id"] == "dsld-1"


def test_irrelevant_query_scores_zero(index):
    vectorizer, matrix, chunks = index
    results = search("car tire repair", vectorizer, matrix, chunks, top_k=3)
    assert results[0]["score"] == 0


def test_generator_refuses_on_zero_score(index):
    vectorizer, matrix, chunks = index
    results = search("car tire repair", vectorizer, matrix, chunks, top_k=3)
    out = generate_answer("car tire repair", results)
    assert out["refused"] is True
    assert out["sources"] == []


def test_generator_answers_on_relevant(index):
    vectorizer, matrix, chunks = index
    results = search("magnesium for sleep", vectorizer, matrix, chunks, top_k=3)
    out = generate_answer("magnesium for sleep", results)
    assert out["refused"] is False
    assert len(out["sources"]) >= 1
