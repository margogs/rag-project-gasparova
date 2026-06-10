"""Тексты и правила формирования ответа (demo-режим, без внешней LLM)."""

REFUSAL_MESSAGE = (
    "No data on this request. The knowledge base contains only vitamin/supplement "
    "shot labels, so I can't answer this. Try asking about a shot by goal or "
    "ingredient (e.g. immune support, B vitamins, magnesium)."
)

ANSWER_HEADER = "Based on the shot labels in the knowledge base:"

# Напоминание о границах ответа (используется как ориентир, не как промпт к LLM):
# - отвечаем только по найденным чанкам;
# - не выдумываем состав/дозировки;
# - без медицинских заявлений («лечит», «снижает болезнь»).
