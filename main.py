import pandas as pd

# -----------------------------
# 데이터 불러오기
# -----------------------------
df_org = pd.read_parquet("sepsis_data/sepsis3.parquet")
df_mort = pd.read_parquet("sepsis_data/fedeaebf612b436f88cb7b7c20bce2b2.snappy.parquet")

df_mort = df_mort[["stay_id", "hospital_expire_flag"]].drop_duplicates()
df_all = df_org.merge(df_mort, on="stay_id", how="left")

# -----------------------------
# 필요한 컬럼 생성
# -----------------------------
df_all["resp_worsening"] = (df_all["respiration"] >= 2).astype(int)
df_all["coag_worsening"] = (df_all["coagulation"] >= 2).astype(int)
df_all["liver_worsening"] = (df_all["liver"] >= 2).astype(int)
df_all["cardio_worsening"] = (df_all["cardiovascular"] >= 2).astype(int)
df_all["cns_worsening"] = (df_all["cns"] >= 2).astype(int)
df_all["renal_worsening"] = (df_all["renal"] >= 2).astype(int)

df_all["organ_count"] = (
    df_all["resp_worsening"]
    + df_all["coag_worsening"]
    + df_all["liver_worsening"]
    + df_all["cardio_worsening"]
    + df_all["cns_worsening"]
    + df_all["renal_worsening"]
)

def get_sequence(row):
    organs = {
        "resp": row["respiration"],
        "coag": row["coagulation"],
        "liver": row["liver"],
        "cardio": row["cardiovascular"],
        "cns": row["cns"],
        "renal": row["renal"]
    }
    organs = {k: v for k, v in organs.items() if v > 0}
    sorted_organs = sorted(organs.items(), key=lambda x: x[1], reverse=True)
    return "->".join([k for k, v in sorted_organs]) if sorted_organs else "none"

df_all["sequence"] = df_all.apply(get_sequence, axis=1)

# -----------------------------
# 간단 결과 확인
# -----------------------------
print("=== Mortality by organ count ===")
print(df_all.groupby("organ_count")["hospital_expire_flag"].mean())

print("\n=== High-risk sequences (count > 100) ===")
seq = df_all.groupby("sequence")["hospital_expire_flag"].agg(["mean", "count"])
seq = seq[seq["count"] > 100].sort_values("mean", ascending=False)
print(seq.head(10))

# -----------------------------
# 저장
# -----------------------------
df_all.to_parquet("sepsis_data/df_all_dashboard.parquet", index=False)
print("\nSaved: sepsis_data/df_all_dashboard.parquet")