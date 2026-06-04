# Project 02 — SPC 기반 반도체 공정 품질 분석

## 개요

실제 반도체 공정 센서 데이터에 SPC(Statistical Process Control) 관리도를 적용하여 공정 이상을 탐지하고, ML + SHAP으로 원인 피처를 분석한 프로젝트입니다.

> 핵심 메시지: ML은 패턴을 학습해서 예측하고, SPC는 공정을 실시간으로 감시한다. 두 도구는 역할이 다르기 때문에 함께 써야 한다.

---

## 사용 데이터셋

- **Semiconductor Quality Control Dataset** (2025)
- 4,219행 × 16열
- 결측치 없음 / Timestamp 포함 → SPC 시계열 적용 가능
- 타겟 : `Defect` (정상 85.4% / 불량 14.6%)

| 피처 | 설명 |
|------|------|
| Chamber_Temperature | 챔버 온도 (°C) |
| Gas_Flow_Rate | 가스 유량 |
| RF_Power | RF 전력 |
| Etch_Depth | 식각 깊이 |
| Rotation_Speed | 회전 속도 |
| Vacuum_Pressure | 진공 압력 |
| Stage_Alignment_Error | 스테이지 정렬 오차 |
| Vibration_Level | 진동 수준 |
| UV_Exposure_Intensity | UV 노광 강도 |
| Particle_Count | 파티클 수 |

---

## 분석 단계

### 1단계 — EDA
- 피처별 분포 시각화 (정상 vs 불량 비교)
- Tool_Type별 불량률 비교
- 시간에 따른 불량률 추이 확인
- 피처 간 상관관계 히트맵 → 모든 피처와 Defect 간 상관계수 ±0.04 이내 확인

### 2단계 — SPC 관리도

| 관리도 | 탐지 대상 | 챔버 온도 탐지 건수 | 진공 압력 탐지 건수 |
|--------|---------|-----------------|-----------------|
| Xbar-R | 큰 이탈 (±3σ) | 1건 | 0건 |
| CUSUM (누적합) | 소규모 드리프트 누적 | 34건 | 44건 |
| EWMA (가중평균) | 서서히 변하는 추세 | 18건 | 9건 |

> Xbar-R만 사용했다면 진공 압력 이상 0건 → 실제로 44건 존재.  
> 세 관리도를 병행해야 하는 이유를 실데이터로 증명.

**공정 능력 지수 (Cpk)**  
전 피처 Cpk = 1.0 (양호 기준 1.33 미달) → 공정 자체가 취약한 상태

**Nelson 8규칙**  
파티클 수 × R6 규칙 위반 66건으로 최다 → 구조적 패턴 이상 탐지

### 3단계 — ML + SHAP

- LightGBM + Optuna : AUC 0.51 → 예측 실패
- 실패 원인 : 피처-타겟 상관관계 전무, 정상/불량 분포 완전 중첩
- SHAP 피처 중요도 (참고용) : 스테이지 정렬 오차 > UV 노광 강도 > 식각 깊이 순

> ML 성능이 낮은 것 자체가 인사이트.  
> 이 공정의 불량은 정적 패턴이 아닌 시간 흐름 속 복합 변동에서 발생 → SPC가 더 적합한 도구임을 실증.

---

## 핵심 결론

```
SPC   : 언제 이상이 발생했는가  → 실시간 감시, 이번 데이터에서 유효
ML    : 어떤 피처가 원인인가    → 예측 실패, SHAP은 참고용으로만 활용
LLM   : 왜, 어떻게 조치할 것인가 → 미래 방향 (SPC+ML 결과를 자연어로 번역)
```

---

## 파일 구조

```
project02_spc_analysis/
├── README.md
├── notebook/
│   ├── 01_EDA.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_SPC_charts.ipynb
│   ├── 04_modeling.ipynb
│   └── 05_anomaly_detection.ipynb
├── src/
│   └── spc_utils.py               ← SPC 관리도 함수 모음
├── data/
│   └── README.md                  ← 데이터 출처 안내
└── presentation/
    └── SPC_관리도의_역할.pptx
```

---

## 실행 방법

```bash
cd project02_spc_analysis/notebook
jupyter notebook 01_EDA.ipynb
```

---

## 데이터 출처

- Semiconductor Quality Control Dataset : [Kaggle](https://www.kaggle.com/datasets/programmer3/semiconductor-sensor-data-for-predictive-quality)
