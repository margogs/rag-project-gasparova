"""Формирование demo-ответа строго из найденных чанков. Без внешней LLM."""

from app.config import SCORE_THRESHOLD
from app.prompts import ANSWER_HEADER, REFUSAL_MESSAGE


def generate_answer(query, results, threshold=SCORE_THRESHOLD):
    """
    Собирает ответ из top-чанков. Если лучший score ниже порога — отказ.
    Возвращает dict: {answer, refused, sources}.
    """
    relevant = [r for r in results if r["score"] >= threshold]

    if not relevant:
        return {"answer": REFUSAL_MESSAGE, "refused": True, "sources": []}

    lines = [ANSWER_HEADER, ""]
    for r in relevant:
        lines.append(f"- {r['text']}")
    answer = "\n".join(lines)

    sources = [
        {"doc_id": r["doc_id"], "name": r["name"], "score": round(r["score"], 4)}
        for r in relevant
    ]
    return {"answer": answer, "refused": False, "sources": sources}
