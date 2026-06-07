"""SQL 함수 사전 (치트시트) — Streamlit 멀티페이지.

초급은 쉽지만 고급(윈도우/CTE/시계열)에서 막히는 학습자를 위해
문제 생성기가 실제로 쓰는 함수들을 난이도별로 정리하고,
superstore 테이블로 바로 실행해볼 수 있게 한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.db_connect import get_engine

st.set_page_config(page_title="SQL 함수 사전", page_icon="📘", layout="wide")


@st.cache_resource
def engine():
    return get_engine()


def table_exists(name: str) -> bool:
    try:
        with engine().connect() as conn:
            return bool(
                conn.execute(
                    text(
                        "SELECT 1 FROM information_schema.tables "
                        "WHERE table_name = :t LIMIT 1"
                    ),
                    {"t": name},
                ).fetchone()
            )
    except Exception:
        return False


def run_sql(sql: str) -> pd.DataFrame:
    with engine().connect() as conn:
        with conn.begin() as trans:
            df = pd.read_sql(text(sql), conn)
            trans.rollback()
    return df


LEVEL_COLOR = {"초급": "🟢", "중급": "🟡", "고급": "🔴"}

# ─────────────────────────────────────────────────────────────
# 함수/문법 사전 데이터
#   category, name, level, desc, syntax, example(superstore 기준)
# ─────────────────────────────────────────────────────────────
ENTRIES: list[dict] = [
    # ── 기초 ──
    {
        "cat": "기초", "name": "SELECT / FROM", "level": "초급",
        "desc": "어떤 컬럼을, 어느 테이블에서 가져올지 정한다. `*` 는 모든 컬럼.",
        "syntax": "SELECT 컬럼1, 컬럼2 FROM 테이블",
        "example": "SELECT region, sales FROM superstore",
    },
    {
        "cat": "기초", "name": "WHERE", "level": "초급",
        "desc": "행을 조건으로 거른다. (그룹화 전에 적용)",
        "syntax": "SELECT * FROM 테이블 WHERE 조건",
        "example": "SELECT * FROM superstore WHERE sales > 1000",
    },
    {
        "cat": "기초", "name": "ORDER BY / LIMIT", "level": "초급",
        "desc": "정렬(ASC 오름·DESC 내림) 후 상위 N개만.",
        "syntax": "SELECT * FROM 테이블 ORDER BY 컬럼 DESC LIMIT N",
        "example": "SELECT region, sales FROM superstore ORDER BY sales DESC LIMIT 5",
    },
    {
        "cat": "기초", "name": "DISTINCT", "level": "초급",
        "desc": "중복을 제거하고 고유값만 남긴다.",
        "syntax": "SELECT DISTINCT 컬럼 FROM 테이블",
        "example": "SELECT DISTINCT region FROM superstore",
    },

    # ── 집계 · 그룹 ──
    {
        "cat": "집계·그룹", "name": "COUNT / SUM / AVG / MIN / MAX", "level": "중급",
        "desc": "여러 행을 하나의 값으로 요약하는 '집계 함수'. "
                "COUNT(개수), SUM(합), AVG(평균), MIN/MAX(최소/최대).",
        "syntax": "SELECT AVG(컬럼), SUM(컬럼) FROM 테이블",
        "example": "SELECT COUNT(*) AS 건수, AVG(sales) AS 평균매출, MAX(profit) AS 최대이익 FROM superstore",
    },
    {
        "cat": "집계·그룹", "name": "GROUP BY", "level": "중급",
        "desc": "같은 값끼리 묶어서 그룹별로 집계한다. "
                "`SELECT` 에 쓴 일반 컬럼은 반드시 `GROUP BY` 에 들어가야 한다.",
        "syntax": "SELECT 그룹컬럼, AVG(값) FROM 테이블 GROUP BY 그룹컬럼",
        "example": "SELECT region, AVG(sales) AS 평균매출 FROM superstore GROUP BY region",
    },
    {
        "cat": "집계·그룹", "name": "HAVING", "level": "중급",
        "desc": "WHERE 는 '행'을 거르고, HAVING 은 '그룹 집계 결과'를 거른다. "
                "(집계 함수 조건은 HAVING 에)",
        "syntax": "SELECT 그룹, AVG(값) FROM 테이블 GROUP BY 그룹 HAVING AVG(값) > 100",
        "example": "SELECT region, AVG(sales) AS 평균 FROM superstore "
                   "GROUP BY region HAVING AVG(sales) > 230",
    },
    {
        "cat": "집계·그룹", "name": "CASE WHEN", "level": "중급",
        "desc": "행마다 조건에 따라 다른 값을 부여한다 (SQL 의 if-else). "
                "구간 나누기·라벨링에 자주 쓴다.",
        "syntax": "CASE WHEN 조건 THEN 값1 ELSE 값2 END",
        "example": "SELECT product_name, "
                   "CASE WHEN profit < 0 THEN '손해' "
                   "WHEN profit = 0 THEN '본전' ELSE '이익' END AS 손익구분 "
                   "FROM superstore LIMIT 20",
    },

    # ── 윈도우 함수 (고급의 핵심) ──
    {
        "cat": "윈도우 함수", "name": "OVER ( ) — 윈도우 함수란?", "level": "고급",
        "desc": "**GROUP BY 와 달리 행을 합치지 않는다.** 각 행은 그대로 두고, "
                "그 행 주변(윈도우)을 기준으로 계산한 값을 '새 컬럼'으로 덧붙인다. "
                "`OVER()` 가 붙으면 그 함수는 윈도우 함수가 된다.",
        "syntax": "함수() OVER (PARTITION BY 그룹 ORDER BY 정렬)",
        "example": "SELECT region, sales, "
                   "AVG(sales) OVER (PARTITION BY region) AS 지역평균 "
                   "FROM superstore LIMIT 20",
    },
    {
        "cat": "윈도우 함수", "name": "PARTITION BY", "level": "고급",
        "desc": "윈도우 함수에서 '그룹'을 나누는 기준. GROUP BY 의 그룹과 비슷하지만 "
                "행은 사라지지 않고 그룹 안에서 계산만 한다.",
        "syntax": "함수() OVER (PARTITION BY region)",
        "example": "SELECT region, category, sales, "
                   "SUM(sales) OVER (PARTITION BY region) AS 지역합계 "
                   "FROM superstore LIMIT 20",
    },
    {
        "cat": "윈도우 함수", "name": "RANK / DENSE_RANK / ROW_NUMBER", "level": "고급",
        "desc": "그룹 안에서 순위를 매긴다. "
                "**RANK**: 동점이면 같은 순위, 다음 순위 건너뜀(1,1,3). "
                "**DENSE_RANK**: 동점 같은 순위, 안 건너뜀(1,1,2). "
                "**ROW_NUMBER**: 동점이어도 무조건 1,2,3 순번.",
        "syntax": "RANK() OVER (PARTITION BY 그룹 ORDER BY 값 DESC)",
        "example": "SELECT region, product_name, sales, "
                   "RANK() OVER (PARTITION BY region ORDER BY sales DESC) AS 지역내순위 "
                   "FROM superstore ORDER BY region, 지역내순위 LIMIT 20",
    },
    {
        "cat": "윈도우 함수", "name": "누적 합계 (running total)", "level": "고급",
        "desc": "`ORDER BY` 를 넣은 SUM() OVER 는 '현재 행까지의 누적 합'을 만든다. "
                "시계열 누적 매출 등에 사용.",
        "syntax": "SUM(값) OVER (PARTITION BY 그룹 ORDER BY 정렬)",
        "example": "SELECT region, order_date, sales, "
                   "SUM(sales) OVER (PARTITION BY region ORDER BY order_date) AS 누적매출 "
                   "FROM superstore ORDER BY region, order_date LIMIT 20",
    },

    # ── CTE · 서브쿼리 ──
    {
        "cat": "CTE·서브쿼리", "name": "WITH (CTE)", "level": "고급",
        "desc": "쿼리 안에서 쓸 '임시 결과 테이블'에 이름을 붙여 두고 본 쿼리에서 가져다 쓴다. "
                "복잡한 쿼리를 단계로 쪼개 읽기 쉽게 만든다.",
        "syntax": "WITH 이름 AS ( 서브쿼리 ) SELECT * FROM 이름",
        "example": "WITH region_avg AS ("
                   "  SELECT region, AVG(sales) AS avg_sales FROM superstore GROUP BY region"
                   ") SELECT * FROM region_avg WHERE avg_sales > 230",
    },
    {
        "cat": "CTE·서브쿼리", "name": "서브쿼리 (Subquery)", "level": "고급",
        "desc": "쿼리 안의 쿼리. 괄호 안 결과를 값·집합·테이블처럼 사용한다. "
                "예: 전체 평균보다 큰 행만 고르기.",
        "syntax": "SELECT * FROM 테이블 WHERE 값 > (SELECT AVG(값) FROM 테이블)",
        "example": "SELECT region, sales FROM superstore "
                   "WHERE sales > (SELECT AVG(sales) FROM superstore) LIMIT 20",
    },

    # ── 시계열 ──
    {
        "cat": "시계열", "name": "date_trunc", "level": "고급",
        "desc": "날짜를 원하는 단위로 '잘라낸다'(절삭). 월별·연별 집계의 핵심. "
                "예: 2024-03-15 → date_trunc('month') → 2024-03-01.",
        "syntax": "date_trunc('month', 날짜컬럼)",
        "example": "SELECT date_trunc('month', order_date) AS 월, SUM(sales) AS 월매출 "
                   "FROM superstore GROUP BY 월 ORDER BY 월",
    },
    {
        "cat": "시계열", "name": "EXTRACT", "level": "고급",
        "desc": "날짜에서 연·월·일·요일 등 특정 부분만 숫자로 뽑아낸다.",
        "syntax": "EXTRACT(YEAR FROM 날짜컬럼)",
        "example": "SELECT EXTRACT(YEAR FROM order_date) AS 연도, SUM(sales) AS 연매출 "
                   "FROM superstore GROUP BY 연도 ORDER BY 연도",
    },
]

CATEGORIES = ["기초", "집계·그룹", "윈도우 함수", "CTE·서브쿼리", "시계열"]

# ─────────────────────────────────────────────────────────────
# 화면
# ─────────────────────────────────────────────────────────────
st.title("📘 SQL 함수 사전")
st.caption("문제 생성기가 실제로 쓰는 SQL 함수/문법을 난이도별로 정리했습니다. "
           "예제는 `superstore` 테이블로 바로 실행해볼 수 있어요.")

has_table = table_exists("superstore")
if not has_table:
    st.info("`superstore` 테이블이 없어 예제 실행은 비활성화됩니다. "
            "(먼저 `python src/load_data.py` 로 데이터를 적재하세요. SQL 설명은 그대로 볼 수 있습니다.)")

# 핵심 개념 비교: GROUP BY vs 윈도우 함수 (가장 헷갈리는 지점)
with st.expander("🧠 먼저 읽기 — GROUP BY 와 윈도우 함수(OVER)의 차이", expanded=True):
    c1, c2 = st.columns(2)
    c1.markdown(
        "**GROUP BY** — 행을 *합친다*\n\n"
        "지역별로 묶으면 4개 지역 → **4행**만 남음.\n"
        "원래 개별 행은 사라짐."
    )
    c1.code("SELECT region, SUM(sales)\nFROM superstore\nGROUP BY region", language="sql")
    c2.markdown(
        "**OVER (윈도우)** — 행을 *유지한다*\n\n"
        "모든 원본 행(9,800여 행)은 그대로 두고\n"
        "그 옆에 '지역 합계' 컬럼을 덧붙임."
    )
    c2.code("SELECT region, sales,\n  SUM(sales) OVER (PARTITION BY region)\nFROM superstore",
            language="sql")
    st.markdown("👉 **순위(RANK), 누적합, 그룹내 비교**가 필요하면 윈도우 함수를 떠올리세요.")

# 검색 + 난이도 필터
top = st.columns([2, 1])
keyword = top[0].text_input("🔍 함수 검색", placeholder="예: RANK, date_trunc, HAVING")
levels = top[1].multiselect("난이도", ["초급", "중급", "고급"], default=["초급", "중급", "고급"])

tabs = st.tabs(CATEGORIES)
for tab, cat in zip(tabs, CATEGORIES):
    with tab:
        items = [
            e for e in ENTRIES
            if e["cat"] == cat
            and e["level"] in levels
            and (keyword.lower() in e["name"].lower()
                 or keyword.lower() in e["desc"].lower()
                 if keyword else True)
        ]
        if not items:
            st.write("조건에 맞는 항목이 없습니다.")
            continue

        for e in items:
            with st.container(border=True):
                st.markdown(f"### {LEVEL_COLOR[e['level']]} {e['name']}  &nbsp;`{e['level']}`")
                st.markdown(e["desc"])
                st.markdown("**문법**")
                st.code(e["syntax"], language="sql")
                st.markdown("**예제**")
                st.code(e["example"], language="sql")

                if has_table:
                    key = f"run_{e['name']}"
                    if st.button("▶ 예제 실행", key=key):
                        try:
                            df = run_sql(e["example"])
                            st.dataframe(df, height=240)
                            st.caption(f"{len(df)}행 반환")
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"실행 오류: {exc}")
