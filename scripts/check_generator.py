"""Проверка demo-ответа и отказа из консоли (итерация 6)."""

from app.generator import generate_answer
from app.retriever import load_index, search

POSITIVE = "energy shot with B vitamins"
NEGATIVE = "how to change a car tire"


def run(query):
    vectorizer, matrix, chunks = load_index()
    results = search(query, vectorizer, matrix, chunks)
    out = generate_answer(query, results)
    print(f"\n=== Запрос: {query}")
    print(f"refused={out['refused']}")
    print(out["answer"])
    if out["sources"]:
        print("Источники:", out["sources"])


def main():
    run(POSITIVE)   # ожидаем ответ + источники
    run(NEGATIVE)   # ожидаем отказ


if __name__ == "__main__":
    main()
