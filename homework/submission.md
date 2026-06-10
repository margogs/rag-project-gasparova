# SUBMISSION

## Ссылка на репозиторий с выполненным заданием

https://github.com/margogs/rag-project-gasparova

## Краткое описание

Учебный RAG: подбор витаминных «шотов» по текстовому запросу.
Прикладной контекст — ИИ-бот вендингового проекта «микс ит».

- **Данные:** NIH Dietary Supplement Label Database (DSLD), публичный API,
  лицензия CC0. Собрано 1500 этикеток шотов → 4943 чанка после нарезки.
- **Pipeline:** данные (`scripts/fetch_data.py`) → ingest → chunking → TF-IDF индекс →
  retrieval (cosine top-k) → demo-ответ с источниками → Streamlit UI.
- **Поведение:** ответ строго по найденным чанкам с показом `doc_id` и score;
  при отсутствии данных — честный отказ.

## Запуск

```bash
uv venv && uv sync
uv run python scripts/fetch_data.py --query "vitamin shot" --max 1500
uv run python scripts/build_index.py
uv run streamlit run app/main.py
```

## Demo-проверка

| Вопрос | Результат |
|--------|-----------|
| immune shot with vitamin C and zinc | ответ, `dsld-337258`, score 0.4825 |
| energy shot with B vitamins | ответ, `dsld-8517`, score 0.4067 |
| magnesium shot for stress and sleep | ответ, `dsld-35844`, score 0.4320 |
| how to change a car tire | отказ (нет данных) |

Тесты: `uv run pytest tests/ -v` — 7 passed.
