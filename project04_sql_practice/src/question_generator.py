"""문제 생성 엔진 (4단계).

스키마 분석 결과(SchemaProfile)와 템플릿(TEMPLATES)을 결합해
실제 컬럼이 대입된 문제 + 모범답안 쿼리를 생성한다.
값이 필요한 템플릿은 DB에서 상수를 계산해 대입한다.
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

# templates 패키지 경로 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from .db_connect import get_engine
    from .schema_analyzer import SchemaProfile, analyze_table
except ImportError:
    from db_connect import get_engine
    from schema_analyzer import SchemaProfile, analyze_table

from templates.question_templates import TEMPLATES


@dataclass
class Question:
    difficulty: str
    prompt: str
    answer_sql: str
    template_id: str


def _compute_value(spec: dict, table: str, col: str, engine: Engine) -> float:
    agg = spec["agg"]
    rnd = spec.get("round", 2)
    with engine.connect() as conn:
        if agg == "PERCENTILE":
            q = f'SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY "{col}") FROM "{table}"'
        else:
            q = f'SELECT {agg}("{col}") FROM "{table}"'
        val = conn.execute(text(q)).scalar()
    return round(float(val), rnd)


def _pick(rng: random.Random, items: list, n: int) -> list | None:
    """items 에서 중복 없이 n개를 뽑는다. 부족하면 None."""
    if len(items) < n:
        return None
    return rng.sample(items, n)


def generate_one(template: dict, profile: SchemaProfile, engine: Engine,
                 rng: random.Random) -> Question | None:
    """단일 템플릿으로 문제를 생성한다. 컬럼이 부족하면 None."""
    req = template.get("requires", {})
    nums = _pick(rng, profile.numeric, req.get("num", 0))
    cats = _pick(rng, profile.good_categoricals(), req.get("cat", 0))
    dates = _pick(rng, profile.date, req.get("date", 0))
    if nums is None or cats is None or dates is None:
        return None

    mapping: dict[str, str] = {"table": profile.table}
    for i, c in enumerate(nums):
        mapping["num" if i == 0 else f"num{i+1}"] = c.name
    for i, c in enumerate(cats):
        mapping["cat" if i == 0 else f"cat{i+1}"] = c.name
    for i, c in enumerate(dates):
        mapping["date" if i == 0 else f"date{i+1}"] = c.name

    # 값 계산 (template 에 value 스펙이 있으면)
    if "value" in template:
        spec = template["value"]
        target_col = mapping[spec["col"]]
        mapping["value"] = _compute_value(spec, profile.table, target_col, engine)

    prompt = template["prompt"].format(**mapping)
    answer_sql = template["sql"].format(**mapping)
    return Question(
        difficulty=template["difficulty"],
        prompt=prompt,
        answer_sql=answer_sql,
        template_id=template["id"],
    )


def generate_questions(table: str, difficulty: str | None = None,
                       n: int | None = None, seed: int | None = None,
                       engine: Engine | None = None) -> list[Question]:
    """테이블에 대해 문제를 생성한다.

    difficulty: "초급"|"중급"|"고급" 중 하나 또는 None(전체)
    n: 생성할 최대 개수 (None=가능한 전부)
    seed: 재현용 난수 시드
    """
    engine = engine or get_engine()
    rng = random.Random(seed)
    profile = analyze_table(table, engine)

    pool = [t for t in TEMPLATES if difficulty is None or t["difficulty"] == difficulty]
    rng.shuffle(pool)

    questions: list[Question] = []
    for t in pool:
        q = generate_one(t, profile, engine, rng)
        if q is not None:
            questions.append(q)
        if n is not None and len(questions) >= n:
            break
    return questions


if __name__ == "__main__":
    qs = generate_questions("superstore", seed=7)
    print(f"생성된 문제: {len(qs)}개\n")
    for i, q in enumerate(qs, 1):
        print(f"[{i}] ({q.difficulty}) {q.prompt}")
        print(f"    정답: {q.answer_sql}\n")
