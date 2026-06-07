"""CSV -> PostgreSQL 적재 모듈 (2단계).

어떤 CSV든 받아서:
  1) 컬럼명을 SQL 친화적으로 정규화 (공백/특수문자 -> _, 소문자)
  2) 날짜처럼 보이는 컬럼을 자동으로 날짜 타입으로 변환
  3) pandas.to_sql 로 테이블 적재
하는 범용 적재기.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

try:  # 패키지/스크립트 양쪽에서 import 되도록
    from .db_connect import get_engine
except ImportError:  # 직접 실행 시
    from db_connect import get_engine


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """컬럼명을 소문자 snake_case 로 정규화한다."""

    def clean(name: str) -> str:
        name = name.strip().lower()
        name = re.sub(r"[^\w가-힣]+", "_", name)  # 영숫자/한글 외 -> _
        name = re.sub(r"_+", "_", name).strip("_")
        return name or "col"

    df = df.copy()
    df.columns = [clean(c) for c in df.columns]
    return df


def auto_parse_dates(df: pd.DataFrame, sample_size: int = 200) -> pd.DataFrame:
    """object 컬럼 중 날짜로 파싱 가능한 것을 datetime 으로 변환한다."""
    df = df.copy()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        sample = df[col].dropna().head(sample_size)
        if sample.empty:
            continue
        parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
        # 표본의 90% 이상이 날짜로 파싱되면 날짜 컬럼으로 간주
        if parsed.notna().mean() >= 0.9:
            df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")
    return df


def load_csv_to_db(
    csv_path: str | Path,
    table_name: str,
    if_exists: str = "replace",
    parse_dates: bool = True,
) -> int:
    """CSV를 읽어 정규화 후 PostgreSQL 테이블로 적재한다. 적재 행 수를 반환."""
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    df = normalize_columns(df)
    if parse_dates:
        df = auto_parse_dates(df)

    engine = get_engine()
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    return len(df)


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent
    csv = base / "data" / "superstore.csv"
    table = "superstore"

    print(f"[적재 시작] {csv} -> 테이블 '{table}'")
    n = load_csv_to_db(csv, table)
    print(f"[적재 완료] {n} 행")

    # 적재 결과 확인
    from sqlalchemy import text

    engine = get_engine()
    with engine.connect() as conn:
        cols = conn.execute(
            text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = :t ORDER BY ordinal_position"
            ),
            {"t": table},
        ).fetchall()
    print(f"[스키마] {table} ({len(cols)} 컬럼)")
    for name, dtype in cols:
        print(f"  - {name}: {dtype}")
