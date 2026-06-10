"""
Сбор данных по витаминным "шотам" из NIH DSLD API в data/raw/datasets.json.

Источник: NIH Dietary Supplement Label Database (DSLD), https://dsld.od.nih.gov/
Лицензия: CC0 1.0 Universal (public domain).
Цитирование: National Institutes of Health, Office of Dietary Supplements.
             Dietary Supplement Label Database, 2026. https://dsld.od.nih.gov/

Формат вывода соответствует ожиданиям ingest.py:
    {"datasets": [ {"id", "name", "text", "source"}, ... ]}

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


def iter_search_ids(query, max_items):
    collected, page_size, offset = [], 50, 0
    while len(collected) < max_items:
        data = get_json(f"{BASE}/search-filter",
                        params={"q": query, "size": page_size, "from": offset})
        if not data:
            break
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break
        for h in hits:
            dsld_id = h.get("_id") or h.get("_source", {}).get("dsldId")
            if dsld_id:
                collected.append(str(dsld_id))
        print(f"  собрано id: {len(collected)}", file=sys.stderr)
        offset += page_size
        time.sleep(0.5)
        if len(hits) < page_size:
            break
    return collected[:max_items]


def fetch_label(dsld_id):
    return get_json(f"{BASE}/label/{dsld_id}")


def label_to_record(label, dsld_id):
    """Карточка DSLD -> запись datasets.json. Текст разбит на абзацы для чанкинга."""
    if not label:
        return None
    name = label.get("fullName") or label.get("productName") or "Unknown product"
    brand = label.get("brandName") or "—"
    form = label.get("physicalState", {})
    form = form.get("langualCodeDescription") if isinstance(form, dict) else (form or "—")

    ingredients = []
    for ing in label.get("ingredientRows", []) or []:
        ing_name = ing.get("name") or ing.get("ingredientName") or ""
        qty = ing.get("quantity")
        unit = ing.get("unit") or ""
        if isinstance(qty, list) and qty:
            qty = qty[0].get("quantity") if isinstance(qty[0], dict) else qty[0]
        amount = f"{qty} {unit}".strip() if qty not in (None, "") else ""
        if ing_name:
            ingredients.append(f"{ing_name} {amount}".strip())
    ingredients_text = "; ".join(ingredients) if ingredients else "ingredients not listed"

    statements = [st.get("notes", "").strip()
                  for st in (label.get("statements", []) or []) if st.get("notes")]
    claims_text = " ".join(statements)

    # Абзацы (\n\n) -> chunker нарежет на отдельные чанки
    text = (
        f"{name} (brand: {brand}). Form: {form}.\n\n"
        f"Ingredients: {ingredients_text}."
    )
    if claims_text:
        text += f"\n\nLabel claim: {claims_text}"

    return {
        "id": f"dsld-{dsld_id}",
        "name": name,
        "text": text,
        "source": f"https://dsld.od.nih.gov/label/{dsld_id}",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="vitamin shot")
    ap.add_argument("--max", type=int, default=1500)
    args = ap.parse_args()

    ids = iter_search_ids(args.query, args.max)
    print(f"Найдено id: {len(ids)}. Тяну составы...", file=sys.stderr)

    records = []
    for i, dsld_id in enumerate(ids, 1):
        rec = label_to_record(fetch_label(dsld_id), dsld_id)
        if rec:
            records.append(rec)
        if i % 25 == 0:
            print(f"  обработано {i}/{len(ids)}", file=sys.stderr)
        time.sleep(0.4)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"datasets": records}, f, ensure_ascii=False, indent=2)
    print(f"\nГотово: {len(records)} записей -> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
