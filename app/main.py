"""Streamlit UI: вопрос -> найденные фрагменты -> ответ -> источники."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.config import VECTORIZER_PATH
from app.generator import generate_answer
from app.retriever import load_index, search

st.set_page_config(page_title="микс ит — подбор шотов (RAG)", page_icon="🥤")
st.title("микс ит — подбор витаминных шотов")
st.caption("RAG поверх этикеток DSLD. Ответ только по данным базы, иначе — отказ.")

# Проверка, что индекс собран
if not VECTORIZER_PATH.exists():
    st.error(
        "Индекс не собран. Сначала выполните:\n\n"
        "`uv run python scripts/build_index.py`"
    )
    st.stop()


@st.cache_resource
def get_index():
    return load_index()


vectorizer, matrix, chunks = get_index()

DEMO = [
    "immune shot with vitamin C and zinc",
    "energy shot with B vitamins",
    "magnesium shot for stress and sleep",
    "how to change a car tire",  # negative
]

with st.sidebar:
    st.header("Demo-вопросы")
    for q in DEMO:
        if st.button(q):
            st.session_state["query"] = q

query = st.text_input("Ваш запрос:", value=st.session_state.get("query", ""))

if query:
    results = search(query, vectorizer, matrix, chunks)
    out = generate_answer(query, results)

    st.subheader("Ответ")
    if out["refused"]:
        st.warning(out["answer"])
    else:
        st.write(out["answer"])

    st.subheader("Найденные фрагменты (top-k)")
    for r in results:
        st.markdown(
            f"**doc_id:** `{r['doc_id']}` · **score:** {r['score']:.4f}"
            f"{' · ' + r['name'] if r['name'] else ''}"
        )
        st.text(r["text"])
