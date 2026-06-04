# Project 01 — 결측치 처리 방법에 따른 결과 분석

## 개요

결측치 처리 방법(Median / RF / MICE)이 ML 모델 성능에 미치는 영향을 4개 데이터셋, 5개 모델에 걸쳐 체계적으로 비교한 프로젝트입니다.

> 핵심 질문: 어떤 대치 방법을 쓰느냐에 따라 ML 모델의 성능이 실질적으로 달라지는가?

---

## 사용 데이터셋

| 데이터셋 | 행 수 | 주요 결측 피처 | 목적 |
|---------|------|--------------|------|
| Titanic | 891 | Age (20%) | 중간 결측률 대표 케이스 |
| Pima Indians | 768 | Insulin (49%), SkinThickness (30%) | 고결측률 집중 검증 |
| Telco Churn | 7,043 | TotalCharges (소수) | 대용량 처리 속도 비교 |
| Credit Card Fraud | 284,807 | 없음 | 클래스 불균형 한계 확인 |

---

## 비교 방법

**대치 방법 3가지**
- `Median` : 열별 중앙값으로 대치 (가장 빠름)
- `RF` : RandomForest로 결측값 예측 (비선형 관계 반영)
- `MICE` : BayesianRidge 체인 예측 (피처 간 상관관계 반영)

**ML 모델 5가지**
- LightGBM (Default / GridSearch / Optuna)
- RandomForest
- LogisticRegression
- MLP
- LLM (Qwen2.5-3B, 비교용)

**평가 지표** : AUC-ROC, F1, Recall

---

## 핵심 결론

| 상황 | 권장 대치 방법 |
|------|-------------|
| 결측률 5% 미만 | Median — 속도 최우선, 성능 차이 없음 |
| 결측률 20~40% | 소규모 → MICE, 중대규모 → RF |
| 결측률 40% 이상 | RF 또는 MICE 필수 — Median은 분포 왜곡 심각 |
| 클래스 불균형 심각 | 대치 방법보다 하이퍼파라미터 튜닝이 성능 결정 |

**분포 왜곡 실증**  
Pima Insulin(결측 49%)에서 Median 적용 시 표준편차가 118.6 → 86.3으로 26.8% 감소.  
RF/MICE는 원본 분포를 자연스럽게 유지.

**LLM 한계 확인**  
Qwen2.5-3B는 익명 PCA 피처(Credit V1~V28)에서 AUC 0.531로 급락.  
숫자를 텍스트 토큰으로 분해하는 구조적 한계 확인.

---

## 파일 구조

```
project01_missing_value/
├── README.md
├── notebook/
│   └── missing_value_analysis.ipynb   ← 전체 분석 코드
├── data/
│   └── README.md                      ← 데이터 출처 안내
└── presentation/
    └── 결측치_처리_비교_발표.pptx
```

---

## 실행 방법

```bash
cd project01_missing_value/notebook
jupyter notebook missing_value_analysis.ipynb
```

---

## 데이터 출처

- Titanic : [Kaggle](https://www.kaggle.com/c/titanic)
- Pima Indians : [Kaggle](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)
- Telco Churn : [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
- Credit Card Fraud : [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
