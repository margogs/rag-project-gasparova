# RAG: подбор витаминных шотов (микс ит)

Учебный RAG на текстовых этикетках добавок: **TF-IDF + demo-ответ с источниками**.
Прикладной контекст — ИИ-бот вендингового проекта «микс ит»: по запросу о состоянии
(«energy», «immune», «stress») подбирает витаминный шот и объясняет состав строго по
данным этикетки. Pipeline: данные → чанки → индекс → поиск → ответ → UI.

Документы планирования — в [doc/](doc/). Данные — [doc/DATA.md](doc/DATA.md).

## Требования

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

## Быстрый старт

```bash
# 1. Окружение
uv venv
uv sync

# 2. (один раз) собрать данные из NIH DSLD API
uv run python scripts/fetch_data.py --query "vitamin shot" --max 1500

# 3. Сборка индекса (ingest + chunk + TF-IDF)
uv run python scripts/build_index.py

# 4. Запуск UI
uv run streamlit run app/main.py
```

Откройте http://localhost:8501

> В репозитории уже лежит небольшой образец `data/raw/datasets.json` (12 записей),
> чтобы pipeline и тесты работали сразу. Для оценки «отлично» замените его реальной
> выгрузкой шага 2 (1000+ записей / 1000+ чанков).

## Demo-вопросы

| Вопрос | Ожидание |
|--------|----------|
| immune shot with vitamin C and zinc | ответ, источник sample-01, score > 0.4 |
| energy shot with B vitamins | ответ, источник sample-04 |
| magnesium shot for stress and sleep | ответ, источник sample-06 |
| how to change a car tire | отказ (нет данных) |

## Проверка из консоли

```bash
uv run pytest tests/ -v                      # тесты
uv run python scripts/check_retrieval.py     # поиск (итерация 5)
uv run python scripts/check_generator.py     # ответ + отказ (итерация 6)
```

## Структура проекта

```
.
├── app/
│   ├── config.py       # пути, top_k, размер чанка, порог отказа
│   ├── chunker.py      # нарезка текста по абзацам
│   ├── retriever.py    # TF-IDF + cosine top-k
│   ├── generator.py    # demo-ответ + отказ
│   ├── prompts.py      # тексты и правила
│   └── main.py         # Streamlit UI
├── scripts/
│   ├── fetch_data.py       # сбор данных из DSLD API
│   ├── ingest.py           # datasets.json -> documents.jsonl
│   ├── build_index.py      # ingest + chunk + TF-IDF
│   ├── check_retrieval.py
│   └── check_generator.py
├── data/
│   ├── raw/datasets.json   # исходные данные (коммитится)
│   ├── processed/          # documents.jsonl, chunks.jsonl (генерируются)
│   └── index/              # vectorizer.pkl, matrix.npz, chunks.jsonl (генерируются)
├── tests/
└── doc/
```

## Ограничения MVP

- Поиск по **словам** (TF-IDF), не по смыслу — синонимы могут не находиться.
- Demo-режим: ответ из найденных чанков, без внешней LLM.
- Данные английские; русскоязычный запрос по английским этикеткам не сматчится
  (направление улучшений — перевод запроса / русские теги).
- Индексируется только текст этикеток.

## Источник данных

NIH Dietary Supplement Label Database (DSLD), https://dsld.od.nih.gov/ ·
лицензия CC0 1.0 Universal (public domain). Подробнее — [doc/DATA.md](doc/DATA.md).
