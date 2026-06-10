"""Быстрая проверка поиска из консоли (итерация 5)."""

from app.retriever import load_index, search

QUERIES = [
    "immune shot with vitamin C and zinc",   # релевантный
    "how to change a car tire",               # нерелевантный -> score ~ 0
]


def main():
    vectorizer, matrix, chunks = load_index()
    for q in QUERIES:
        print(f"\n=== Запрос: {q}")
        results = search(q, vectorizer, matrix, chunks, top_k=3)
        for r in results:
            print(f"  score={r['score']:.4f}  doc_id={r['doc_id']}  {r['text'][:70]}")


if __name__ == "__main__":
    main()
