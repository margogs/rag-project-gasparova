"""Преобразует data/raw/datasets.json в data/processed/documents.jsonl.

Добавляет метаданные: doc_id, name, source_file.
"""

import json

from app.config import DOCUMENTS_JSONL, PROCESSED_DIR, RAW_DATASETS


def load_datasets():
    with open(RAW_DATASETS, encoding="utf-8") as f:
        data = json.load(f)
    return data["datasets"]


def to_document(record, index):
    """Запись datasets -> документ с метаданными."""
    doc_id = record.get("id") or f"doc-{index}"
    return {
        "doc_id": doc_id,
        "name": record.get("name", ""),
        "source_file": "datasets.json",
        "source": record.get("source", ""),
        "text": record.get("text", ""),
    }


def main():
    records = load_datasets()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(DOCUMENTS_JSONL, "w", encoding="utf-8") as f:
        for i, rec in enumerate(records):
            doc = to_document(rec, i)
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"Создан {DOCUMENTS_JSONL}: {len(records)} документов")


if __name__ == "__main__":
    main()
