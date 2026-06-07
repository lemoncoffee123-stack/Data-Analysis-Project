"""채점 엔진 (5단계).

핵심 원칙: 쿼리 텍스트가 아니라 '실행 결과'를 비교한다.
사용자 쿼리와 모범답안 쿼리를 각각 실행해 결과 테이블을 얻고,
행 순서/컬럼명에 구애받지 않고 값이 같으면 정답으로 인정한다.

안전장치: 사용자 입력은 SELECT/WITH 로 시작하는 단일 조회문만 허용한다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

try:
    from .db_connect import get_engine
except ImportError:
    from db_connect import get_engine

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy)\b",
    re.IGNORECASE,
)


@dataclass
class GradeResult:
    correct: bool
    message: str
    user_result: pd.DataFrame | None = None
    answer_result: pd.DataFrame | None = None


def is_safe_select(sql: str) -> tuple[bool, str]:
    """단일 SELECT/WITH 조회문인지 검사한다."""
    s = sql.strip().rstrip(";").strip()
    if not s:
        return False, "빈 쿼리입니다."
    if ";" in s:
        return False, "여러 개의 문장은 허용되지 않습니다. (세미콜론 제거)"
    if not re.match(r"(?is)^\s*(select|with)\b", s):
        return False, "SELECT 또는 WITH 로 시작하는 조회문만 허용됩니다."
    if _FORBIDDEN.search(s):
        return False, "데이터를 변경하는 키워드는 사용할 수 없습니다."
    return True, ""


def _run(sql: str, engine: Engine) -> pd.DataFrame:
    """읽기 전용으로 쿼리를 실행하고 DataFrame 을 반환한다 (롤백 보장)."""
    with engine.connect() as conn:
        with conn.begin() as trans:
            df = pd.read_sql(text(sql), conn)
            trans.rollback()
    return df


def _normalize(df: pd.DataFrame, float_round: int = 6) -> list[tuple]:
    """행 순서/컬럼명 무관 비교를 위한 정규화.

    - 부동소수점은 반올림
    - NaN/None 은 공통 토큰으로
    - 각 행을 튜플로 만든 뒤 전체를 정렬
    (컬럼의 '순서'는 의미가 있으므로 유지, 컬럼 '이름'은 무시)
    """
    norm = df.copy()
    for col in norm.columns:
        if pd.api.types.is_float_dtype(norm[col]):
            norm[col] = norm[col].round(float_round)

    def cell(v):
        if pd.isna(v):
            return "<NA>"
        return v

    rows = [tuple(cell(v) for v in row) for row in norm.itertuples(index=False, name=None)]
    rows.sort(key=lambda r: tuple(str(x) for x in r))
    return rows


def grade(user_sql: str, answer_sql: str, engine: Engine | None = None) -> GradeResult:
    """사용자 쿼리와 모범답안을 실행 결과로 비교한다."""
    engine = engine or get_engine()

    ok, reason = is_safe_select(user_sql)
    if not ok:
        return GradeResult(False, f"실행 불가: {reason}")

    try:
        user_df = _run(user_sql, engine)
    except Exception as exc:  # noqa: BLE001 - 사용자에게 원인 표시
        return GradeResult(False, f"쿼리 실행 오류: {type(exc).__name__} - {exc}")

    answer_df = _run(answer_sql, engine)

    # 1) 모양 비교
    if user_df.shape != answer_df.shape:
        return GradeResult(
            False,
            f"오답: 결과 크기가 다릅니다. "
            f"(제출 {user_df.shape[0]}행 {user_df.shape[1]}열 / "
            f"정답 {answer_df.shape[0]}행 {answer_df.shape[1]}열)",
            user_df, answer_df,
        )

    # 2) 값 비교 (행 순서/컬럼명 무관)
    if _normalize(user_df) == _normalize(answer_df):
        return GradeResult(True, "정답입니다! 🎉", user_df, answer_df)

    return GradeResult(
        False,
        "오답: 결과 행/열 수는 같지만 값이 일치하지 않습니다.",
        user_df, answer_df,
    )


if __name__ == "__main__":
    answer = 'SELECT "region", SUM("sales") AS s FROM "superstore" GROUP BY "region"'

    # 1) 작성 방식이 달라도 결과가 같으면 정답
    user_ok = 'SELECT "region", SUM("sales") FROM "superstore" GROUP BY "region" ORDER BY 1'
    r1 = grade(user_ok, answer)
    print("케이스1 (다른 정렬/별칭):", r1.correct, "-", r1.message)

    # 2) 틀린 쿼리
    user_bad = 'SELECT "region", AVG("sales") FROM "superstore" GROUP BY "region"'
    r2 = grade(user_bad, answer)
    print("케이스2 (AVG 오답):", r2.correct, "-", r2.message)

    # 3) 안전장치
    r3 = grade('DROP TABLE superstore', answer)
    print("케이스3 (위험 쿼리):", r3.correct, "-", r3.message)
