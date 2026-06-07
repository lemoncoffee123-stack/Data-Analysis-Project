# 데이터 분석 포트폴리오

품질 / 반도체 직무를 목표로 진행한 데이터 분석 프로젝트 모음입니다.  
Project 1~3은 **"방법론 검증 → 실무 적용 → 모델 패러다임 탐색"** 이라는 하나의 분석 흐름으로 연결되며,  
Project 4는 분석의 기반이 되는 **SQL 역량을 직접 도구로 구현**하며 다진 작업입니다.

---

## 프로젝트 구성

| # | 프로젝트 | 핵심 주제 | 사용 기술 |
|---|---------|----------|----------|
| 1 | [결측치 처리 방법에 따른 결과 분석](./project01_missing_value/) | Median / RF / MICE 세 가지 대치 방법이 ML 모델 성능에 미치는 영향 실증 비교 | Python, LightGBM, Optuna, MICE, SHAP |
| 2 | [SPC 기반 반도체 공정 품질 분석](./project02_spc_analysis/) | 실제 반도체 공정 데이터에 SPC 관리도를 적용한 이상 탐지 및 원인 분석 | Python, SPC, LightGBM, SHAP, Isolation Forest |
| 3 | [콘크리트 압축 강도 예측: TabPFN vs LightGBM](./project03_ml_models/) | Zero-shot Transformer 모델 TabPFN과 LightGBM의 회귀 성능 다각도 비교 | Python, TabPFN, LightGBM, Optuna, SHAP |
| 4 | [Schema-Aware SQL 문제 생성기](./project04_sql_practice/) | 어떤 테이블이든 스키마를 자동 분석해 난이도별 문제를 만들고, 쿼리 텍스트가 아닌 **실행 결과**로 채점하는 SQL 학습 도구 | PostgreSQL, Python, SQLAlchemy, Streamlit |

---

## 포트폴리오 스토리

```
Project 1                   Project 2                   Project 3
───────────────────────     ───────────────────────     ───────────────────────
결측치 처리 방법론 검증 ──→  검증된 방법을 실제 공정에  ──→  새로운 모델 패러다임 탐색
Median / RF / MICE 비교      적용 (SPC + ML + SHAP)          TabPFN vs LightGBM
방법론 연구                   실무 적용 연구                   모델 비교 연구
```

Project 1에서 **MICE + LightGBM** 조합이 대부분의 상황에서 유효함을 검증하고,  
Project 2에서 해당 결론을 실제 반도체 공정 데이터에 적용했습니다.  
Project 3에서는 Zero-shot Transformer(TabPFN)라는 새로운 모델 패러다임을 탐색했습니다.

그리고 이 모든 분석의 출발점인 **데이터 추출·가공 역량(SQL)** 을, Project 4에서  
단순 문제 풀이가 아니라 **학습 도구를 직접 설계·구현**하는 방식으로 증명했습니다.

```
Project 4
───────────────────────
분석의 기반 = SQL 역량
스키마 자동 분석 · 결과 기반 채점
도구를 만들며 깊이 학습
```

---

## 기술 스택

```
언어        Python 3.x
ML 모델     LightGBM, RandomForest, LogisticRegression, MLP, TabPFN
튜닝        Optuna, GridSearch
해석        SHAP
통계        SPC (Xbar-R, CUSUM, EWMA), Nelson 8규칙, Cp/Cpk, Paired t-test
이상 탐지   Isolation Forest
시각화      Matplotlib, Seaborn
딥러닝      PyTorch (TabPFN 기반)
데이터베이스 PostgreSQL, SQLAlchemy, psycopg2
웹/앱       Streamlit
```

---

## 실행 환경

```bash
pip install pandas numpy matplotlib seaborn scikit-learn lightgbm optuna shap
pip install tabpfn torch                              # Project 3 추가 필요
pip install streamlit sqlalchemy psycopg2-binary python-dotenv  # Project 4 추가 필요
```

> Project 4는 PostgreSQL 인스턴스가 필요하며, 세부 설정·실행 방법은
> [project04_sql_practice/README.md](./project04_sql_practice/) 를 참고하세요.

---

## 연락처

- GitHub : 이종원 — [github.com/lemoncoffee123-stack](https://github.com/lemoncoffee123-stack)
- Email  : lemoncoffee123@gmail.com
