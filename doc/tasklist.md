# Tasklist

Пошаговый маршрут реализации MVP. Каждая итерация — задачи + команда проверки.

## Прогресс по итерациям

| # | Итерация | Статус |
|---|----------|--------|
| 0 | Окружение | ⬜ |
| 1 | Сбор данных (DSLD → datasets.json) | ⬜ |
| 2 | Ingest (documents.jsonl) | ⬜ |
| 3 | Чанкинг (chunks.jsonl, цель 1000+) | ⬜ |
| 4 | Индекс TF-IDF | ⬜ |
| 5 | Retrieval | ⬜ |
| 6 | Demo-ответ + отказ | ⬜ |
| 7 | UI (Streamlit) | ⬜ |
| 8 | Тесты + README + demo/negative-вопросы | ⬜ |

## Итерации

### 0. Окружение
- Задачи: `uv venv`, `uv sync`, базовая структура папок `app/`, `scripts/`, `data/`, `tests/`, `doc/`.
- Проверка: `uv run python -c "import sklearn, streamlit"` без ошибок.

### 1. Сбор данных
- Задачи: запустить `scripts/fetch_data.py --query "vitamin shot"`, получить `data/raw/datasets.json`,
  проверить пример записи (название, бренд, форма, состав не пустые).
- Проверка: `uv run python -c "import json;print(len(json.load(open('data/raw/datasets.json'))))"` ≥ 10.

### 2. Ingest
- Задачи: `scripts/ingest.py` нормализует записи в `data/processed/documents.jsonl`.
- Проверка: файл существует, число строк = числу продуктов.

### 3. Чанкинг
- Задачи: `app/chunker.py` режет документы на чанки (состав / дозировки / назначение).
- Проверка: число чанков в `data/processed/chunks.jsonl`; для «отлично» — 1000+.

### 4. Индекс
- Задачи: `scripts/build_index.py` обучает TF-IDF, сохраняет векторизатор и матрицу в `data/index/`.
- Проверка: `uv run python scripts/build_index.py` отрабатывает, файлы индекса созданы.

### 5. Retrieval
- Задачи: `app/retriever.py` — TF-IDF + косинус, top-k, порог отказа.
- Проверка: `uv run python scripts/check_retrieval.py` — релевантный чанк по тестовому запросу.

### 6. Demo-ответ + отказ
- Задачи: `app/generator.py` + `app/prompts.py` — ответ из чанков с источниками; отказ вне данных.
- Проверка: `uv run python scripts/check_generator.py` — ответ на «положительный» запрос, отказ на negative.

### 7. UI
- Задачи: `app/main.py` — поле ввода, ответ, источники (`doc_id`, score, текст).
- Проверка: `uv run streamlit run app/main.py`, вручную прогнать demo- и negative-вопросы.

### 8. Тесты и сдача
- Задачи: 3+ теста, README с инструкцией запуска, 3 demo-вопроса + 1 negative.
- Проверка: `uv run pytest tests/ -v` — все green.

## Текущая итерация
- Итерация 1 (данные собраны скриптом `fetch_data.py`, проверяем пример записи).

## Критерии завершения MVP
- Pipeline проходит итерации 0–7 без ручных правок.
- 3 demo-вопроса дают релевантные ответы с источником, 1 negative — отказ.
- `pytest` green; README запускается на чистой машине.
