import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sepsis Mortality Dashboard", layout="wide")

st.title("Sepsis Mortality Dashboard")
st.markdown("Sepsis 환자에서 장기 dysfunction burden과 sequence별 mortality를 탐색하는 대시보드")

# -----------------------------
# 데이터 불러오기
# -----------------------------
df_all = pd.read_parquet("sepsis_data/df_all_dashboard.parquet")

# -----------------------------
# 상단 요약
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Patients", f"{len(df_all):,}")
col2.metric("Mortality Rate", f"{df_all['hospital_expire_flag'].mean():.2%}")
col3.metric("Mean Organ Count", f"{df_all['organ_count'].mean():.2f}")

st.divider()

# -----------------------------
# 1. Organ Count vs Mortality
# -----------------------------
st.subheader("1. Mortality by Organ Count")

result = df_all.groupby("organ_count")["hospital_expire_flag"].mean()

fig1, ax1 = plt.subplots(figsize=(7, 4))
ax1.plot(result.index, result.values, marker="o")
ax1.set_xlabel("Number of Dysfunctional Organs")
ax1.set_ylabel("Mortality Rate")
ax1.set_title("Mortality by Organ Count")
st.pyplot(fig1)

st.dataframe(result.reset_index().rename(columns={"hospital_expire_flag": "mortality_rate"}))

st.divider()

# -----------------------------
# 2. Organ-specific Mortality
# -----------------------------
st.subheader("2. Mortality by Organ Dysfunction")

organs = [
    "resp_worsening",
    "coag_worsening",
    "liver_worsening",
    "cardio_worsening",
    "cns_worsening",
    "renal_worsening"
]

organ_df = []
for o in organs:
    rate = df_all.groupby(o)["hospital_expire_flag"].mean().get(1, None)
    organ_df.append((o, rate))

organ_df = pd.DataFrame(organ_df, columns=["organ", "mortality"]).sort_values(
    "mortality", ascending=False
)

fig2, ax2 = plt.subplots(figsize=(7, 4))
ax2.bar(organ_df["organ"], organ_df["mortality"])
ax2.set_ylabel("Mortality Rate")
ax2.set_title("Mortality by Organ")
plt.xticks(rotation=45)
st.pyplot(fig2)

st.dataframe(organ_df)

st.divider()

# -----------------------------
# 3. High-risk Sequences
# -----------------------------
st.subheader("3. High-risk Sequences")

seq = df_all.groupby("sequence")["hospital_expire_flag"].agg(["mean", "count"])
seq = seq[seq["count"] > 100].sort_values("mean", ascending=False)

st.dataframe(seq.head(10))

st.divider()

# -----------------------------
# 4. Most Frequent Sequences
# -----------------------------
st.subheader("4. Most Frequent Sequences")

common_seq = (
    df_all.groupby("sequence")["hospital_expire_flag"]
    .agg(["mean", "count"])
    .sort_values("count", ascending=False)
)

st.dataframe(common_seq.head(10))

st.divider()

# -----------------------------
# 5. Frequency vs Mortality
# -----------------------------
st.subheader("5. Frequency vs Mortality")

scatter_df = (
    df_all.groupby("sequence")["hospital_expire_flag"]
    .agg(["mean", "count"])
    .reset_index()
)

scatter_df = scatter_df[scatter_df["count"] >= 30]

colors = []
for _, row in scatter_df.iterrows():
    if row["mean"] > 0.35 and row["count"] >= 50:
        colors.append("red")
    elif row["count"] > 300:
        colors.append("blue")
    else:
        colors.append("gray")

fig3, ax3 = plt.subplots(figsize=(8, 6))
ax3.scatter(
    scatter_df["count"],
    scatter_df["mean"],
    c=colors,
    alpha=0.7
)
ax3.set_xlabel("Frequency (count)")
ax3.set_ylabel("Mortality Rate")
ax3.set_title("Sequence Frequency vs Mortality")

st.pyplot(fig3)

st.markdown("**Top 3 High-risk Sequences**")
top3 = scatter_df[
    (scatter_df["mean"] > 0.35) & (scatter_df["count"] >= 50)
].sort_values(["mean", "count"], ascending=[False, False]).head(3).copy()

top3_display = top3.reset_index(drop=True)[["sequence", "mean", "count"]]
top3_display.index = top3_display.index + 1
st.dataframe(top3_display)

st.markdown("""
### 🔎 그래프 해석 방법

- **X축 (Frequency)**: 해당 sequence를 가진 환자 수  
- **Y축 (Mortality Rate)**: 해당 sequence에서의 사망률  
- 🔴 **빨간 점**: 드물지만 위험한 패턴  
- 🔵 **파란 점**: 자주 발생하는 패턴  
- ⚪ **회색 점**: 일반적인 패턴  

👉 빈도가 높다고 해서 반드시 사망률이 높은 것은 아니며,  
일부 드문 sequence가 높은 mortality를 보일 수 있음
""")

st.divider()

# -----------------------------
# 6. Filter by Organ Dysfunction
# -----------------------------
st.subheader("6. Filter by Organ Dysfunction")

selected_organ = st.selectbox(
    "Choose organ",
    [
        "all",
        "resp_worsening",
        "coag_worsening",
        "liver_worsening",
        "cardio_worsening",
        "cns_worsening",
        "renal_worsening"
    ]
)

filtered = df_all.copy()
if selected_organ != "all":
    filtered = filtered[filtered[selected_organ] == 1]

col4, col5 = st.columns(2)
col4.metric("Filtered Patients", f"{len(filtered):,}")
col5.metric("Filtered Mortality", f"{filtered['hospital_expire_flag'].mean():.2%}")

filtered_seq = (
    filtered.groupby("sequence")["hospital_expire_flag"]
    .agg(["mean", "count"])
    .sort_values("mean", ascending=False)
)

filtered_seq = filtered_seq[filtered_seq["count"] >= 30]

st.dataframe(filtered_seq.head(10))

st.divider()

# -----------------------------
# 7. Interpretation Guide
# -----------------------------
st.subheader("7. Interpretation Guide")

st.markdown("""
- **count**: 해당 sequence를 가진 환자 수  
- **mean**: 해당 sequence에서의 사망률  
- 따라서 **count가 많다고 mean이 커지는 것은 아님**
- 드물지만 위험한 sequence와, 흔하지만 상대적으로 덜 위험한 sequence를 구분해서 볼 수 있음

**Note:**  
현재 sequence는 실제 시간 순서가 아니라, SOFA severity 기반 **pseudo-sequence**입니다.
""")