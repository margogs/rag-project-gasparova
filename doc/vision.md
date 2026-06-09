# Vision

Техническая рамка MVP. Стек повторяет репозиторий-образец
[MaratNotes/rag-tutorial](https://github.com/MaratNotes/rag-tutorial): TF-IDF + demo-ответ,
без внешней LLM.

## Технологии

- **Язык:** Python 3.10+.
- **Менеджер окружения:** uv (`uv venv`, `uv sync`).
- **Retrieval:** TF-IDF + косинусная близость (scikit-learn). Поиск **по словам**, не по смыслу.
- **Ответ:** demo-режим — ответ собирается из найденных чанков, без вызова внешней LLM.
- **UI:** Streamlit (`app/main.py`).
- **Хранение индекса:** файлы на диске (`vectorizer.pkl`, матрица).

## Как строится индекс

1. `scripts/fetch_data.py` → `data/raw/datasets.json` (один продукт = одна запись с текстом).
2. `scripts/ingest.py` → `data/processed/documents.jsonl` (нормализованные документы).
3. Чанкинг (`app/chunker.py`) → `data/processed/chunks.jsonl` (мелкие фрагменты:
   состав, дозировки, назначение).
4. `scripts/build_index.py` → обучает TF-IDF на чанках, сохраняет векторизатор и матрицу
   в `data/index/`.

## Как работает поиск

1. Запрос пользователя векторизуется тем же TF-IDF.
2. Считается косинусная близость к чанкам, берётся top-k.
3. Если максимальный score ниже порога — **отказ** (нет данных по запросу).
4. Иначе `app/generator.py` формирует ответ из топ-чанков и показывает источники
   (`doc_id`, score, текст).

## Что НЕ используем в MVP

- Семантические эмбеддинги / векторные БД (только TF-IDF по словам).
- Внешнюю LLM для генерации (demo-ответ из чанков).
- Обращение к DSLD API во время запроса (данные выгружаются заранее в `datasets.json`).
- Русскоязычный ввод (данные английские; перевод запроса — в улучшениях).
- Сопоставление с реальным каталогом «микс ит», персонализацию, анализы крови
  (фазы 3–4 брифа), оплату, CV-камеры, вендинг-железо.

## Как запускать

```bash
uv venv
uv sync
uv run python scripts/fetch_data.py --query "vitamin shot" --max 1500   # один раз, собрать данные
uv run python scripts/build_index.py                                    # ingest + chunk + TF-IDF
uv run streamlit run app/main.py                                        # UI на http://localhost:8501
```
