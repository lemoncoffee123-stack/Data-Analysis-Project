# Project 03 — 콘크리트 압축 강도 예측: TabPFN vs LightGBM

## 개요

콘크리트 압축 강도(Concrete Compressive Strength) 데이터셋을 활용하여,  
사전 학습된 Transformer 기반 Zero-shot 모델인 **TabPFN**과  
대표적인 GBDT 모델인 **LightGBM**의 성능을 다각도로 비교한 회귀 분석 프로젝트입니다.

> 핵심 질문: 하이퍼파라미터 튜닝 없이 Zero-shot으로 작동하는 TabPFN이 튜닝된 LightGBM과 경쟁할 수 있는가?

---

## 사용 데이터셋

- **Concrete Compressive Strength Dataset** (UCI Machine Learning Repository)
- 1,030행 × 9열 (피처 8개 + 타겟 1개)
- 결측치 없음

| 피처 | 설명 | 단위 |
|------|------|------|
| Cement | 시멘트 함량 | kg/m³ |
| Blast Furnace Slag | 고로 슬래그 | kg/m³ |
| Fly Ash | 플라이 애시 | kg/m³ |
| Water | 물 함량 | kg/m³ |
| Superplasticizer | 고성능 감수제 | kg/m³ |
| Coarse Aggregate | 굵은 골재 | kg/m³ |
| Fine Aggregate | 잔골재 | kg/m³ |
| Age | 양생 일수 | 일(day) |
| **Compressive Strength** | **압축 강도 (타겟)** | **MPa** |

---

## 비교 모델

### TabPFN (Zero-shot Regressor)
- 대규모 합성 데이터로 사전 학습된 Transformer 기반 모델
- **하이퍼파라미터 튜닝 없이** 즉시 예측 가능 (Zero-shot)
- 분위수 예측(Quantile Prediction)으로 불확실성 정량화 가능
- GPU 가속 지원

### LightGBM Default
- 기본값 그대로 사용한 베이스라인 모델
- 빠른 학습 속도와 낮은 메모리 사용량

### LightGBM + Optuna (Tuned)
- Optuna TPE Sampler로 50 trials 하이퍼파라미터 최적화
- 5-Fold Cross-Validation 기반 RMSE 최소화
- 탐색 파라미터: `n_estimators`, `max_depth`, `learning_rate`, `num_leaves` 등

---

## 분석 단계

### 1단계 — EDA
- 타겟 변수(압축 강도) 분포 시각화 (히스토그램 + 박스플롯)
- 피처 간 상관관계 히트맵
- 주요 피처 vs 타겟 산점도 + 선형 추세선

### 2단계 — 모델 학습 및 평가

| 구분 | 내용 |
|------|------|
| 데이터 분할 | Train 80% / Test 20% (random_state=42) |
| 교차 검증 | 5-Fold Cross-Validation |
| 평가 지표 | MAE, RMSE, R², MAPE |

### 3단계 — 고급 분석

**Learning Curve (학습 곡선)**  
학습 데이터 크기(50 ~ 824행)에 따른 RMSE 변화를 측정하여  
각 모델의 데이터 효율성을 비교했습니다.

**TabPFN 분위수 예측**  
10% / 50% / 90% 분위수 예측으로 예측 불확실성 구간을 시각화했습니다.  
이는 LightGBM에는 없는 TabPFN 고유의 기능입니다.

**SHAP 분석 (LightGBM Tuned)**  
- SHAP Bar Plot: 전체 피처 중요도 순위
- SHAP Summary Plot: 피처 값과 예측 영향 방향 동시 확인

**통계적 유의성 검정 (Paired t-test)**  
TabPFN vs LightGBM Tuned 간 절대 오차 및 제곱 오차를  
대응표본 t-검정으로 통계적 유의성을 검증했습니다.

---

## 핵심 결론

| 항목 | TabPFN | LightGBM Default | LightGBM Tuned |
|------|--------|-----------------|----------------|
| 예측 정확도 (R²) | - | - | 최고 |
| 오차 (RMSE) | - | - | 최소 |
| 튜닝 필요 여부 | 불필요 (Zero-shot) | 불필요 | Optuna 50 trials |
| 학습/추론 속도 | 중간 | 가장 빠름 | Optuna 포함 느림 |
| SHAP 해석 | 제한적 | 가능 | 가능 (권장) |
| 불확실성 정량화 | 가능 (Quantile) | 불가 | 불가 |

**주요 인사이트**
- 튜닝 없이도 TabPFN은 LightGBM Default와 경쟁력 있는 성능을 보임
- LightGBM Tuned가 RMSE / R² 기준 최고 성능이나, Optuna 튜닝 시간 비용이 발생
- TabPFN은 소규모 데이터에서 특히 강점 (Learning Curve에서 확인)
- Cement와 Age가 압축 강도에 가장 큰 영향을 미치는 피처 (SHAP 기준)

---

## 파일 구조

```
project03_concrete_strength/
├── README.md
├── notebook/
│   └── concrete_strength_analysis.ipynb   ← 전체 분석 코드
├── data/
│   ├── README.md                           ← 데이터 출처 안내
│   └── Concrete_Data.csv                  ← 원본 데이터
└── results/
    └── figures/
        ├── 01_target_distribution.png
        ├── 02_correlation_heatmap.png
        ├── 03_feature_vs_target.png
        ├── 04_cv_comparison.png
        ├── 05_pred_vs_actual.png
        ├── 06_residual_distribution.png
        ├── 07_residual_vs_predicted.png
        ├── 08_tabpfn_quantile.png
        ├── 09_metrics_comparison.png
        ├── 10_time_comparison.png
        ├── 11_feature_importance.png
        ├── 12_shap_importance.png
        ├── 13_shap_summary.png
        ├── 14_learning_curve.png
        └── 15_overall_comparison.png
```

---

## 실행 방법

**패키지 설치**

```bash
pip install pandas numpy matplotlib seaborn scikit-learn lightgbm optuna shap
pip install tabpfn torch
```

**노트북 실행**

```bash
cd project03_concrete_strength/notebook
jupyter notebook concrete_strength_analysis.ipynb
```

> TabPFN API 토큰이 필요합니다.  
> [TabPFN 공식 사이트](https://tabpfn.com)에서 발급 후 환경변수에 등록하세요.

---

## 데이터 출처

- Concrete Compressive Strength Dataset : [UCI ML Repository](https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength)
- I-Cheng Yeh, "Modeling of strength of high performance concrete using artificial neural networks," Cement and Concrete Research, 1998.
