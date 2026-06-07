"""SQL 문제 생성기 — Streamlit 인터페이스 (6단계).

실행: streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
from code_editor import code_editor
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.db_connect import get_engine
from src.grader import grade
from src.load_data import load_csv_to_db
from src.question_generator import generate_questions
from src.schema_analyzer import analyze_table

st.set_page_config(page_title="SQL 문제 생성기", page_icon="🧩", layout="wide")


@st.cache_resource
def engine():
    return get_engine()


def list_tables() -> list[str]:
    with engine().connect() as conn:
        rows = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
        ).fetchall()
    return [r[0] for r in rows]


# 자동완성에 넣을 SQL 키워드/함수
SQL_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "LIMIT",
    "DISTINCT", "AS", "AND", "OR", "NOT", "IN", "BETWEEN", "LIKE", "IS NULL",
    "JOIN", "LEFT JOIN", "INNER JOIN", "ON", "UNION",
    "CASE", "WHEN", "THEN", "ELSE", "END", "ASC", "DESC",
    "COUNT", "SUM", "AVG", "MIN", "MAX", "ROUND",
    "WITH", "OVER", "PARTITION BY", "RANK", "ROW_NUMBER", "DENSE_RANK",
    "date_trunc", "EXTRACT",
]

# 에디터 우하단 '실행/채점' 버튼 (commands:["submit"] -> 결과 dict type=="submit")
SUBMIT_BUTTONS = [{
    "name": "실행·채점",
    "feather": "Play",
    "primary": True,
    "hasText": True,
    "showWithIcon": True,
    "commands": ["submit"],
    "style": {"bottom": "0.44rem", "right": "0.4rem"},
}]

EDITOR_OPTIONS = {
    "wrap": True,
    "enableBasicAutocompletion": True,
    "enableLiveAutocompletion": True,
    "showLineNumbers": True,
}


@st.cache_data(show_spinner=False)
def build_completions(table_name: str) -> list[dict]:
    """선택된 테이블의 컬럼명 + SQL 키워드로 자동완성 후보를 만든다."""
    prof = analyze_table(table_name, engine())
    comps = [
        {"caption": c.name, "value": c.name, "meta": c.kind, "score": 1000}
        for c in prof.columns
    ]
    comps.append({"caption": table_name, "value": table_name, "meta": "table", "score": 900})
    comps += [
        {"caption": k, "value": k, "meta": "keyword", "score": 500}
        for k in SQL_KEYWORDS
    ]
    return comps


st.title("🧩 SQL 문제 생성기")
st.caption("테이블 스키마를 자동 분석해 난이도별 SQL 문제를 만들고, 실행 결과로 채점합니다.")

# ---------------- 사이드바: 데이터 소스 ----------------
with st.sidebar:
    st.header("1. 데이터 선택")

    uploaded = st.file_uploader("CSV 업로드 (선택)", type=["csv"])
    if uploaded is not None:
        new_table = st.text_input("적재할 테이블명", value=Path(uploaded.name).stem.lower())
        if st.button("DB에 적재"):
            tmp = ROOT / "data" / f"_upload_{uploaded.name}"
            tmp.write_bytes(uploaded.getbuffer())
            n = load_csv_to_db(tmp, new_table)
            st.success(f"'{new_table}' 테이블에 {n}행 적재 완료")

    try:
        tables = list_tables()
    except Exception as exc:  # noqa: BLE001
        st.error(f"DB 연결 실패: {exc}")
        st.stop()

    table = st.selectbox("문제를 낼 테이블", tables,
                         index=tables.index("superstore") if "superstore" in tables else 0)

    st.header("2. 문제 설정")
    difficulty = st.selectbox("난이도", ["전체", "초급", "중급", "고급"])
    seed = st.number_input("시드(재현용)", value=0, step=1)
    if st.button("문제 생성 🎲", type="primary"):
        diff = None if difficulty == "전체" else difficulty
        st.session_state["questions"] = generate_questions(
            table, difficulty=diff, seed=int(seed), engine=engine()
        )
        st.session_state["table"] = table

# ---------------- 스키마 분석 결과 ----------------
with st.expander("📊 스키마 자동 분석 결과 보기"):
    try:
        prof = analyze_table(table, engine())
        c1, c2, c3 = st.columns(3)
        c1.metric("숫자형", len(prof.numeric))
        c1.write(", ".join(c.name for c in prof.numeric) or "-")
        c2.metric("범주형", len(prof.categorical))
        c2.write(", ".join(c.name for c in prof.good_categoricals()) + " ...")
        c3.metric("날짜형", len(prof.date))
        c3.write(", ".join(c.name for c in prof.date) or "-")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"분석 불가: {exc}")

# ---------------- 문제 풀이 ----------------
questions = st.session_state.get("questions")
if not questions:
    st.info("← 사이드바에서 테이블/난이도를 고르고 **문제 생성**을 눌러주세요.")
    st.stop()

st.subheader(f"📝 생성된 문제 ({len(questions)}개)")

table_now = st.session_state.get("table", table)
completions = build_completions(table_now)
st.caption("💡 에디터에서 컬럼명/SQL 키워드 자동완성이 동작합니다 "
           "(`Ctrl+Space` 로 후보 호출). 작성 후 우하단 **실행·채점** 버튼을 누르세요.")

for i, q in enumerate(questions):
    with st.container(border=True):
        st.markdown(f"**문제 {i+1}** &nbsp; `{q.difficulty}`")
        st.write(q.prompt)

        response = code_editor(
            "",
            lang="sql",
            height=[4, 10],
            theme="default",
            completions=completions,
            buttons=SUBMIT_BUTTONS,
            options=EDITOR_OPTIONS,
            key=f"editor_{i}",
        )

        # 실행·채점 버튼(submit) 눌렸을 때만 채점하고 결과를 세션에 저장
        if response["type"] == "submit" and response["text"].strip():
            st.session_state[f"result_{i}"] = grade(
                response["text"], q.answer_sql, engine()
            )

        result = st.session_state.get(f"result_{i}")
        if result is not None:
            if result.correct:
                st.success(result.message)
            else:
                st.error(result.message)
            if result.user_result is not None:
                left, right = st.columns(2)
                left.caption("내 결과")
                left.dataframe(result.user_result, height=200)
                right.caption("정답 결과")
                right.dataframe(result.answer_result, height=200)

        with st.expander("👀 모범답안 보기"):
            st.code(q.answer_sql, language="sql")
