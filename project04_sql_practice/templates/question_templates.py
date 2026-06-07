"""난이도별 문제 템플릿 (데이터 기반 선언).

각 템플릿은 placeholder 를 가진 문제/정답 쿼리와,
필요한 컬럼 종류(requires)를 선언한다.
실제 컬럼 대입과 값 계산은 question_generator.py 가 수행한다.

placeholder
  {table} 테이블명
  {num}, {num2}  숫자형 컬럼
  {cat}, {cat2}  범주형 컬럼 (GROUP BY 적합)
  {date}         날짜형 컬럼
  {value}        value 스펙으로 DB에서 계산한 상수

requires (필요 컬럼 개수)
  num / cat / date 키에 정수

value (선택) — DB에서 계산해 {value} 에 대입할 상수
  {"agg": "AVG"|"MIN"|"MAX"|"PERCENTILE", "col": "num", "round": n}
"""

TEMPLATES = [
    # ---------------- 초급: SELECT / WHERE / ORDER BY / LIMIT ----------------
    {
        "id": "basic_limit",
        "difficulty": "초급",
        "requires": {},
        "prompt": "{table} 테이블에서 상위 10개 행의 모든 컬럼을 조회하세요.",
        "sql": 'SELECT * FROM "{table}" LIMIT 10',
    },
    {
        "id": "basic_orderby",
        "difficulty": "초급",
        "requires": {"num": 1},
        "prompt": "{table}에서 {num}이(가) 가장 큰 상위 5개 행을 조회하세요. (모든 컬럼)",
        "sql": 'SELECT * FROM "{table}" ORDER BY "{num}" DESC LIMIT 5',
    },
    {
        "id": "basic_where",
        "difficulty": "초급",
        "requires": {"num": 1},
        "value": {"agg": "AVG", "col": "num", "round": 2},
        "prompt": "{table}에서 {num}이(가) 평균값({value})보다 큰 행을 모두 조회하세요. (모든 컬럼)",
        "sql": 'SELECT * FROM "{table}" WHERE "{num}" > {value}',
    },
    {
        "id": "basic_distinct",
        "difficulty": "초급",
        "requires": {"cat": 1},
        "prompt": "{table}의 {cat} 컬럼에 어떤 고유값들이 있는지 조회하세요.",
        "sql": 'SELECT DISTINCT "{cat}" FROM "{table}"',
    },

    # ---------------- 중급: GROUP BY / HAVING / CASE WHEN ----------------
    {
        "id": "mid_groupby_avg",
        "difficulty": "중급",
        "requires": {"cat": 1, "num": 1},
        "prompt": "{cat}별 {num}의 평균을 구하세요.",
        "sql": 'SELECT "{cat}", AVG("{num}") AS avg_{num} FROM "{table}" GROUP BY "{cat}"',
    },
    {
        "id": "mid_groupby_count",
        "difficulty": "중급",
        "requires": {"cat": 1},
        "prompt": "{cat}별 행의 개수를 구하세요.",
        "sql": 'SELECT "{cat}", COUNT(*) AS cnt FROM "{table}" GROUP BY "{cat}"',
    },
    {
        "id": "mid_groupby_sum",
        "difficulty": "중급",
        "requires": {"cat": 1, "num": 1},
        "prompt": "{cat}별 {num}의 합계를 구하고, 합계가 큰 순으로 정렬하세요.",
        "sql": (
            'SELECT "{cat}", SUM("{num}") AS total_{num} '
            'FROM "{table}" GROUP BY "{cat}" ORDER BY total_{num} DESC'
        ),
    },
    {
        "id": "mid_having",
        "difficulty": "중급",
        "requires": {"cat": 1, "num": 1},
        "value": {"agg": "AVG", "col": "num", "round": 2},
        "prompt": "{cat}별 {num}의 평균이 전체 평균값({value})보다 큰 {cat}만 조회하세요.",
        "sql": (
            'SELECT "{cat}", AVG("{num}") AS avg_{num} FROM "{table}" '
            'GROUP BY "{cat}" HAVING AVG("{num}") > {value}'
        ),
    },

    # ---------------- 고급: WINDOW / CTE / 서브쿼리 / 시계열 ----------------
    {
        "id": "adv_window_rank",
        "difficulty": "고급",
        "requires": {"cat": 1, "num": 1},
        "prompt": (
            "{cat}별로 그룹을 나눈 뒤, 각 그룹 안에서 {num} 기준 순위(RANK)를 매기세요. "
            "({cat}, {num}, 순위 컬럼을 출력)"
        ),
        "sql": (
            'SELECT "{cat}", "{num}", '
            'RANK() OVER (PARTITION BY "{cat}" ORDER BY "{num}" DESC) AS rnk '
            'FROM "{table}"'
        ),
    },
    {
        "id": "adv_cte_above_avg",
        "difficulty": "고급",
        "requires": {"cat": 1, "num": 1},
        "prompt": (
            "CTE(WITH)를 사용해 {cat}별 {num} 평균을 구한 뒤, "
            "전체 {num} 평균보다 높은 {cat}만 조회하세요."
        ),
        "sql": (
            'WITH grp AS ('
            'SELECT "{cat}" AS k, AVG("{num}") AS a FROM "{table}" GROUP BY "{cat}"'
            ') SELECT k, a FROM grp '
            'WHERE a > (SELECT AVG("{num}") FROM "{table}")'
        ),
    },
    {
        "id": "adv_timeseries_month",
        "difficulty": "고급",
        "requires": {"date": 1, "num": 1},
        "prompt": "{date}를 기준으로 월별 {num}의 합계를 구하고 월 순으로 정렬하세요.",
        "sql": (
            "SELECT date_trunc('month', \"{date}\") AS month, "
            'SUM("{num}") AS total_{num} FROM "{table}" '
            'GROUP BY month ORDER BY month'
        ),
    },
]
