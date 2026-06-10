"""Единая конфигурация проекта: пути и параметры pipeline."""

from pathlib import Path

# Корень проекта (на уровень выше папки app/)
ROOT = Path(__file__).resolve().parent.parent

# Данные
RAW_DATASETS = ROOT / "data" / "raw" / "datasets.json"
PROCESSED_DIR = ROOT / "data" / "processed"
DOCUMENTS_JSONL = PROCESSED_DIR / "documents.jsonl"
CHUNKS_JSONL = PROCESSED_DIR / "chunks.jsonl"

# Индекс
INDEX_DIR = ROOT / "data" / "index"
VECTORIZER_PATH = INDEX_DIR / "vectorizer.pkl"
MATRIX_PATH = INDEX_DIR / "matrix.npz"
INDEX_CHUNKS_PATH = INDEX_DIR / "chunks.jsonl"

# Параметры чанкинга
MAX_CHARS = 500       # максимальный размер чанка в символах
OVERLAP = 50          # перекрытие между чанками в символах

# Параметры поиска
TOP_K = 5             # сколько чанков возвращать
SCORE_THRESHOLD = 0.05  # ниже этого score считаем, что данных нет -> отказ
