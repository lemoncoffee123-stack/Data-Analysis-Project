# 🧩 SQL 문제 생성기 (Schema-Aware SQL Quiz Generator)

> 어떤 테이블을 넣어도 **스키마를 자동 분석**해 난이도별 SQL 문제를 만들고,
> **쿼리 텍스트가 아닌 실행 결과**로 채점하는 PostgreSQL 기반 학습 도구.

SQL 학습 도구를 직접 설계·구현하며 SQL 역량을 키운 포트폴리오 프로젝트입니다.

---

## ✨ 핵심 특징

- **스키마 자동 분석** — `information_schema` 로 컬럼 타입을 조회하고
  숫자형 / 범주형 / 날짜형으로 분류. 범주형은 카디널리티(고유값 수)까지 조사해
  식별자 컬럼(예: `order_id`)을 걸러내고 GROUP BY 에 적합한 컬럼을 추천.
- **범용성** — 특정 데이터에 종속되지 않음. 어떤 CSV/테이블이든 넣으면 작동.
- **데이터 기반 문제 생성** — 난이도별 템플릿에 실제 컬럼과
  DB에서 계산한 상수(평균 등)를 대입해 문제 + 모범답안을 생성.
- **결과 기반 채점** — 사용자 쿼리와 모범답안을 각각 실행해
  행 순서·컬럼명·작성 방식이 달라도 **결과 값이 같으면 정답** 인정.
- **스키마 인식 자동완성** — 코드 에디터가 선택된 테이블의 실제 컬럼명과
  SQL 키워드를 자동완성 후보로 제시.
- **SQL 함수 사전 페이지** — RANK/CTE/date_trunc 등 고급 함수를 난이도별로 정리하고
  샘플 테이블로 즉시 실행해볼 수 있는 학습 보조 페이지 제공.
- **안전장치** — 사용자 입력은 단일 `SELECT`/`WITH` 조회문만 허용(DDL/DML 차단),
  읽기 전용 트랜잭션으로 실행 후 롤백.

---

## 🏗️ 아키텍처

```
CSV ──► load_data ──► PostgreSQL
                          │
                          ▼
                   schema_analyzer  (숫자/범주/날짜 분류 + 카디널리티)
                          │
                          ▼
              question_generator × templates  (난이도별 문제 + 모범답안)
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
       사용자 쿼리 실행            모범답안 쿼리 실행
            └──────────► grader (결과 비교) ◄──────────┘
```

---

## 📂 파일 구조

```
project04_sql_generator/
├── app.py                       # Streamlit 인터페이스
├── requirements.txt
├── .env.example                 # 연결 정보 템플릿 (.env는 git 제외)
├── src/
│   ├── db_connect.py            # .env 기반 DB 연결
│   ├── load_data.py             # 범용 CSV 적재 (컬럼 정규화·날짜 자동 변환)
│   ├── schema_analyzer.py       # ★ 스키마 자동 분석 (프로젝트 핵심)
│   ├── question_generator.py    # 문제 생성 엔진
│   └── grader.py                # 결과 기반 채점 엔진
├── pages/
│   └── 1_📘_SQL_함수_사전.py      # SQL 함수 치트시트 (예제 실행 가능)
├── templates/
│   └── question_templates.py    # 난이도별 문제 템플릿 (선언형)
└── data/
    └── superstore.csv           # 샘플 데이터 (Sample Superstore)
```

---

## 🚀 실행 방법

### 1. 환경 준비 (Python 3.12 권장)

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
```

### 2. DB 접속 정보 설정

`.env.example` 을 복사해 `.env` 를 만들고 비밀번호를 입력합니다.

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 3. 샘플 데이터 적재

```bash
python src/load_data.py
```

### 4. 실행

```bash
# 웹 인터페이스
streamlit run app.py

# 또는 CLI 로 각 단계 확인
python src/schema_analyzer.py      # 스키마 분석 결과
python src/question_generator.py   # 문제 생성 결과
python src/grader.py               # 채점 데모
```

---

## 📝 난이도 구성

| 난이도 | 다루는 SQL |
|--------|-----------|
| 초급 | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT` |
| 중급 | `GROUP BY`, `HAVING`, 집계함수, 정렬 |
| 고급 | `WINDOW`(RANK/PARTITION), `CTE`(WITH), 서브쿼리, 시계열(`date_trunc`) |

---

## 🔍 채점 방식 예시

```sql
-- 모범답안
SELECT region, SUM(sales) FROM superstore GROUP BY region;

-- 사용자가 정렬·별칭을 다르게 써도 결과가 같으면 정답 인정
SELECT region, SUM(sales) AS s FROM superstore GROUP BY region ORDER BY 1;
```

채점기는 두 쿼리를 실행한 뒤 행 순서와 컬럼명을 무시하고 값만 비교합니다.

---

## 🛠️ 기술 스택

`PostgreSQL` · `Python 3.12` · `SQLAlchemy` · `psycopg2` · `pandas` · `Streamlit`

---

## 📌 알려진 한계 / 개선 아이디어

- 의미 없는 숫자형 컬럼(예: `postal_code`)도 집계 문제에 선택될 수 있음
  → 컬럼명 휴리스틱으로 제외 예정.
- 현재 단일 테이블 대상 → 다중 테이블 `JOIN` 문제로 확장 가능.
- 사용자 정답률 기반 적응형 난이도 조절 기능 추가 가능.
