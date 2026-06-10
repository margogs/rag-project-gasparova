"""
Сбор данных по витаминным "шотам" из NIH DSLD API в data/raw/datasets.json.

Источник: NIH Dietary Supplement Label Database (DSLD), https://dsld.od.nih.gov/
Лицензия: CC0 1.0 Universal (public domain).
Цитирование: National Institutes of Health, Office of Dietary Supplements.
             Dietary Supplement Label Database, 2026. https://dsld.od.nih.gov/

Формат вывода (ожидается ingest.py):
    {"datasets": [ {"id", "name", "text", "source"}, ... ]}

Структура ответа search-filter: {"hits": [ {"_id", "_source": {...}}, ... ]}.
Состав есть прямо в _source, поэтому второй запрос label/{id} не нужен.

Запуск:
    uv run python scripts/fetch_data.py --query "vitamin shot" --max 1500
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

BASE = "https://api.ods.od.nih.gov/dsld/v9"
HEADERS = {"Accept": "application/json", "User-Agent": "rag-homework/1.0"}
OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "datasets.json"


def get_json(url, params=None, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                wait = 60 * (attempt + 1)
                print(f"  rate limit, ждём {wait} c...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"  HTTP {r.status_code} для {url}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"  ошибка сети: {e}", file=sys.stderr)
            time.sleep(5)
    return None


def hit_to_record(hit):
    """Элемент hits -> запись datasets.json. Текст разбит на абзацы для чанкинга."""
    dsld_id = str(hit.get("_id", ""))
    src = hit.get("_source", {})

    name = src.get("fullName") or src.get("productName") or "Unknown product"
    brand = src.get("brandName") or "—"

    form = src.get("physicalState") or {}
    form = form.get("langualCodeDescription", "—") if isinstance(form, dict) else "—"

    # Ингредиенты: имя + notes (там форма/дозировка, если есть)
    ingredients = []
    for ing in src.get("allIngredients", []) or []:
        ing_name = (ing.get("name") or ing.get("ingredientGroup") or "").strip()
        note = (ing.get("notes") or "").strip()
        if not ing_name:
            continue
        ingredients.append(f"{ing_name} ({note})" if note else ing_name)
    ingredients_text = "; ".join(ingredients) if ingredients else "ingredients not listed"

    # Типы заявлений на этикетке (Structure/Function и т.п.)
    claims = [c.get("langualCodeDescription", "").strip()
              for c in (src.get("claims", []) or []) if c.get("langualCodeDescription")]
    claims_text = ", ".join(claims)

    text = (
        f"{name} (brand: {brand}). Form: {form}.\n\n"
        f"Ingredients: {ingredients_text}."
    )
    if claims_text:
        text += f"\n\nLabel claim type: {claims_text}"

    return {
        "id": f"dsld-{dsld_id}",
        "name": name,
        "text": text,
        "source": f"https://dsld.od.nih.gov/label/{dsld_id}",
    }


def fetch_records(query, max_items):
    records, page_size, offset = [], 50, 0
    seen = set()
    while len(records) < max_items:
        data = get_json(f"{BASE}/search-filter",
                        params={"q": query, "size": page_size, "from": offset})
        if not data:
            break
        hits = data.get("hits", []) if isinstance(data, dict) else data
        if not hits:
            break
        new = 0
        for h in hits:
            hid = h.get("_id")
            if hid in seen:
                continue
            seen.add(hid)
            records.append(hit_to_record(h))
            new += 1
        print(f"  собрано записей: {len(records)}", file=sys.stderr)
        if new == 0:
            break                      # новых не приходит -> страницы кончились
        offset += page_size
        time.sleep(0.4)
        if len(hits) < page_size:
            break
    return records[:max_items]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="vitamin shot")
    ap.add_argument("--max", type=int, default=1500)
    args = ap.parse_args()

    records = fetch_records(args.query, args.max)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"datasets": records}, f, ensure_ascii=False, indent=2)
    print(f"\nГотово: {len(records)} записей -> {OUT}", file=sys.stderr)
    if records:
        print("\nПример первой записи:", file=sys.stderr)
        print(json.dumps(records[0], ensure_ascii=False, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
