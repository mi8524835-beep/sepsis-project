# 🧠 Sepsis Organ Dysfunction Pattern Analysis

## 📌 Overview
Sepsis 환자에서 장기 기능 이상(organ dysfunction)의 개수와 조합(sequence)이 사망률에 미치는 영향을 분석하고,  
이를 기반으로 **설명 가능한 분석 + 예측 모델 + 대시보드**를 구현한 프로젝트입니다.

---

## 🎯 Objectives
- 장기 dysfunction burden과 mortality 관계 분석  
- 장기 악화 sequence별 위험 패턴 탐색  
- explainable 분석 기반 dashboard 구현  

---

## 🛠 Data
- MIMIC-IV 기반 sepsis cohort  
- SOFA score 기반 organ dysfunction  
- Target: hospital_expire_flag  

---

## ⚙️ Method

### 1. Feature Engineering
- organ_count 생성 (악화 장기 수)
- sequence 생성 (SOFA 기반 pseudo-order)

### 2. Exploratory Analysis
- organ count vs mortality
- organ별 mortality
- sequence별 위험도 분석

### 3. Modeling
- XGBoost 기반 mortality prediction
- class imbalance 보정

### 4. Visualization
- Streamlit dashboard 구현

---

## 📊 Key Results

### 🔹 Organ Burden
- 장기 수 증가 → mortality 증가  
  (0개: 16% → 5개: 55%)

### 🔹 High-risk Sequences
- liver → renal → coag → cardio  
- coag → renal → cardio  

👉 특정 장기 조합이 높은 mortality와 연관

### 🔹 Model
- AUROC ≈ 0.62  
- 주요 feature: organ_count, renal, cardiovascular  

---

## 💡 Insights
- 단순 장기 수보다 **장기 조합과 패턴이 중요**
- 일부 rare sequence가 높은 mortality를 보임
- explainable 분석이 임상적으로 의미 있음

---

## 🚀 Dashboard
Streamlit 기반 interactive dashboard:

- organ count vs mortality  
- organ별 위험도  
- sequence 패턴 분석  
- frequency vs mortality  

---

## ⚠️ Limitations
- sequence는 실제 시간 순서가 아닌 pseudo-order  
- 단일 데이터셋 기반  

---

## 🔮 Future Work
- time-series 기반 progression 분석  
- survival analysis  
- real-time risk prediction  

---

## 🧑‍💻 Tech Stack
- Python (pandas, sklearn, xgboost)
- Streamlit
- MIMIC-IV

---

## 📎 Note
Due to data size and access restrictions, raw parquet files are not included.  
Please store data locally under `sepsis_data/`.
