"""DB 연결 모듈.

.env에서 접속 정보를 읽어 SQLAlchemy 엔진을 만든다.
비밀번호 등 민감 정보는 코드에 직접 쓰지 않고 .env에서 불러온다.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# 프로젝트 루트의 .env 를 로드 (src/ 기준 한 단계 위)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)


def get_engine() -> Engine:
    """환경변수 기반으로 SQLAlchemy 엔진을 생성한다."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "postgres")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")

    if not password or password.startswith("여기에"):
        raise RuntimeError(
            ".env 파일의 DB_PASSWORD가 설정되지 않았습니다. "
            f"({_ENV_PATH}) 에서 비밀번호를 입력하세요."
        )

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    return create_engine(url)


def test_connection() -> str:
    """연결을 테스트하고 PostgreSQL 버전 문자열을 반환한다."""
    engine = get_engine()
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version();")).fetchone()[0]
    return version


if __name__ == "__main__":
    try:
        print("[연결 시도]")
        print("[성공]", test_connection())
    except Exception as exc:  # noqa: BLE001 - CLI에서 원인 그대로 보여주기 위함
        print("[실패]", type(exc).__name__, "-", exc)
