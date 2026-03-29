import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from xgboost import XGBClassifier

# -----------------------------
# 데이터 불러오기
# -----------------------------
df_all = pd.read_parquet("sepsis_data/df_all_dashboard.parquet")

# -----------------------------
# 모델용 feature
# -----------------------------
df_all["sequence_encoded"] = df_all["sequence"].astype("category").cat.codes
df_all["seq_len"] = df_all["sequence"].apply(lambda x: len(x.split("->")))

features = [
    "respiration",
    "coagulation",
    "liver",
    "cardiovascular",
    "cns",
    "renal",
    "organ_count",
    "sequence_encoded",
    "seq_len"
]

X = df_all[features]
y = df_all["hospital_expire_flag"]

# -----------------------------
# train/test split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -----------------------------
# class imbalance 보정
# -----------------------------
scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

# -----------------------------
# 모델 학습
# -----------------------------
model = XGBClassifier(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    eval_metric="logloss",
    random_state=42,
    scale_pos_weight=scale_pos_weight
)

model.fit(X_train, y_train)

# -----------------------------
# 평가
# -----------------------------
y_prob = model.predict_proba(X_test)[:, 1]

y_pred_default = (y_prob >= 0.5).astype(int)
y_pred_03 = (y_prob >= 0.3).astype(int)

print("=== AUROC ===")
print("AUROC:", roc_auc_score(y_test, y_prob))

print("\n=== Classification Report (threshold=0.5) ===")
print(classification_report(y_test, y_pred_default))

print("\n=== Classification Report (threshold=0.3) ===")
print(classification_report(y_test, y_pred_03))

# -----------------------------
# Feature importance
# -----------------------------
importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("\n=== Feature Importance ===")
print(importance)