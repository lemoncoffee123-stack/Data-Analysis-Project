"""스키마 자동 분석기 (3단계 — 프로젝트 핵심).

들어온 테이블의 컬럼을 information_schema 로 조회한 뒤
숫자형 / 범주형 / 날짜형으로 분류한다.
이 분류 결과가 문제 생성 엔진의 입력이 된다.

추가로 범주형 컬럼은 '카디널리티(고유값 수)'를 함께 조사해
GROUP BY 문제에 적합한 컬럼(고유값이 적당히 적은 것)을 우선 추천한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import text
from sqlalchemy.engine import Engine

try:
    from .db_connect import get_engine
except ImportError:
    from db_connect import get_engine

# PostgreSQL data_type -> 우리 분류 매핑
NUMERIC_TYPES = {
    "smallint", "integer", "bigint", "decimal", "numeric",
    "real", "double precision", "money",
}
DATE_TYPES = {
    "date", "timestamp without time zone", "timestamp with time zone",
    "time without time zone", "time with time zone",
}
# 그 외 text/varchar/char/boolean 등은 범주형으로 취급


@dataclass
class ColumnInfo:
    name: str
    data_type: str
    kind: str  # "numeric" | "categorical" | "date"
    distinct: int | None = None  # 범주형일 때 고유값 수


@dataclass
class SchemaProfile:
    table: str
    columns: list[ColumnInfo] = field(default_factory=list)

    @property
    def numeric(self) -> list[ColumnInfo]:
        return [c for c in self.columns if c.kind == "numeric"]

    @property
    def categorical(self) -> list[ColumnInfo]:
        return [c for c in self.columns if c.kind == "categorical"]

    @property
    def date(self) -> list[ColumnInfo]:
        return [c for c in self.columns if c.kind == "date"]

    def good_categoricals(self, max_distinct: int = 50) -> list[ColumnInfo]:
        """GROUP BY 에 적합한 범주형(고유값이 적당히 적은) 컬럼."""
        cats = [c for c in self.categorical if c.distinct and 1 < c.distinct <= max_distinct]
        return sorted(cats, key=lambda c: c.distinct or 0)


def _classify(data_type: str) -> str:
    if data_type in NUMERIC_TYPES:
        return "numeric"
    if data_type in DATE_TYPES:
        return "date"
    return "categorical"


def analyze_table(table: str, engine: Engine | None = None,
                  probe_cardinality: bool = True) -> SchemaProfile:
    """테이블을 분석해 SchemaProfile 을 반환한다."""
    engine = engine or get_engine()
    profile = SchemaProfile(table=table)

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = :t ORDER BY ordinal_position"
            ),
            {"t": table},
        ).fetchall()

        if not rows:
            raise ValueError(f"테이블 '{table}' 을(를) 찾을 수 없습니다.")

        for name, dtype in rows:
            kind = _classify(dtype)
            col = ColumnInfo(name=name, data_type=dtype, kind=kind)
            if kind == "categorical" and probe_cardinality:
                # 식별자성 컬럼(고유값이 너무 많은 것)을 걸러내기 위한 카디널리티 조사
                col.distinct = conn.execute(
                    text(f'SELECT COUNT(DISTINCT "{name}") FROM "{table}"')
                ).scalar()
            profile.columns.append(col)

    return profile


def print_profile(profile: SchemaProfile) -> None:
    print(f"=== 스키마 분석: {profile.table} ===")
    print(f"숫자형 ({len(profile.numeric)}): " +
          ", ".join(c.name for c in profile.numeric))
    print(f"날짜형 ({len(profile.date)}): " +
          ", ".join(c.name for c in profile.date))
    print(f"범주형 ({len(profile.categorical)}):")
    for c in profile.categorical:
        d = f"{c.distinct} 고유값" if c.distinct is not None else "?"
        print(f"  - {c.name} ({d})")
    print("\nGROUP BY 추천 범주형:",
          ", ".join(c.name for c in profile.good_categoricals()))


if __name__ == "__main__":
    profile = analyze_table("superstore")
    print_profile(profile)
