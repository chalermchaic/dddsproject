"""
Lead Scoring — Binary Classification
Target : Target_Converted (1 = ปิดการขายสำเร็จ, 0 = ไม่สนใจ)
Model  : Logistic Regression (baseline) + Random Forest (main)
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from db.connection import run_query

NUM_FEATURES = ["Discount_Rate", "Activity_Count", "Distinct_Channel_Used",
                "First_Response_Days", "Engagement_Span_Days"]
CAT_FEATURES = ["Source_Channel"]

# แปลชื่อฟีเจอร์เป็นไทย (ใช้ตอนแสดงผล/เขียนรายงาน)
FEATURE_TH = {
    "Activity_Count": "จำนวนครั้งที่ติดตาม",
    "Distinct_Channel_Used": "ความหลากหลายของช่องทางติดตาม",
    "First_Response_Days": "ระยะเวลาตอบกลับครั้งแรก (วัน)",
    "Engagement_Span_Days": "ช่วงเวลาที่ยังมีปฏิสัมพันธ์ (วัน)",
    "Discount_Rate": "ส่วนลดของแคมเปญ (%)",
    "Source_Channel": "ช่องทางที่มา",
}

# ฟีเจอร์ของ "ทุก" lead (ไม่กรอง label) — ใช้ตอนทำนาย lead ที่ยังเปิดอยู่
SQL_ALL_LEADS = """
SELECT  l.Lead_ID,
        l.Full_Name,
        l.Followup_Status,
        l.Source_Channel,
        COALESCE(c.Discount_Rate, 0)                    AS Discount_Rate,
        COUNT(a.Activity_ID)                            AS Activity_Count,
        COUNT(DISTINCT a.Activity_Type)                 AS Distinct_Channel_Used,
        MIN(julianday(a.Activity_Date) - julianday(l.Created_At)) AS First_Response_Days,
        MAX(julianday(a.Activity_Date) - julianday(l.Created_At)) AS Engagement_Span_Days
FROM LEAD l
LEFT JOIN CAMPAIGN      c ON c.Campaign_ID = l.Campaign_ID
LEFT JOIN LEAD_ACTIVITY a ON a.Lead_ID     = l.Lead_ID
GROUP BY l.Lead_ID;
"""


@dataclass
class ScoringResult:
    model: Pipeline
    metrics: dict
    importance: pd.DataFrame
    roc: dict
    confusion: np.ndarray
    report: str
    report_df: pd.DataFrame
    test_size: int
    train_size: int
    cv_auc: tuple = field(default=(0.0, 0.0))


def load_training_data() -> pd.DataFrame:
    """ดึงจาก View V_LEAD_FEATURES (มีเฉพาะ lead ที่รู้ผลลัพธ์แล้ว)"""
    return run_query("SELECT * FROM V_LEAD_FEATURES")


def _build_pipeline(algo: str = "rf") -> Pipeline:
    pre = ColumnTransformer([
        ("num", Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sc", StandardScaler()),
        ]), NUM_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_FEATURES),
    ])
    clf = (RandomForestClassifier(
                n_estimators=300, max_depth=8, min_samples_leaf=5,
                class_weight="balanced", random_state=42, n_jobs=-1)
           if algo == "rf" else
           LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))
    return Pipeline([("pre", pre), ("clf", clf)])


def _feature_names(pipe: Pipeline) -> list[str]:
    ohe = pipe.named_steps["pre"].named_transformers_["cat"]
    return NUM_FEATURES + list(ohe.get_feature_names_out(CAT_FEATURES))


def train(algo: str = "rf", test_ratio: float = 0.25) -> ScoringResult:
    df = load_training_data()
    if len(df) < 50:
        raise ValueError(f"ข้อมูลน้อยเกินไป ({len(df)} แถว) — รัน seed_data.py ก่อน")

    X = df[NUM_FEATURES + CAT_FEATURES]
    y = df["Target_Converted"].astype(int)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=test_ratio, stratify=y, random_state=42)

    pipe = _build_pipeline(algo)
    pipe.fit(X_tr, y_tr)

    y_pred = pipe.predict(X_te)
    y_prob = pipe.predict_proba(X_te)[:, 1]

    metrics = {
        "Accuracy":  round(accuracy_score(y_te, y_pred), 4),
        "Precision": round(precision_score(y_te, y_pred, zero_division=0), 4),
        "Recall":    round(recall_score(y_te, y_pred, zero_division=0), 4),
        "F1-Score":  round(f1_score(y_te, y_pred, zero_division=0), 4),
        "ROC-AUC":   round(roc_auc_score(y_te, y_prob), 4),
    }

    cv = cross_val_score(_build_pipeline(algo), X, y, cv=5, scoring="roc_auc")

    # ---- Feature Importance ----
    names = _feature_names(pipe)
    step = pipe.named_steps["clf"]
    vals = (step.feature_importances_ if hasattr(step, "feature_importances_")
            else np.abs(step.coef_[0]))
    imp = (pd.DataFrame({"feature": names, "importance": vals})
             .sort_values("importance", ascending=False)
             .reset_index(drop=True))
    imp["feature_th"] = imp["feature"].map(
        lambda f: FEATURE_TH.get(f, f.replace("Source_Channel_", "ช่องทาง: ")))

    fpr, tpr, _ = roc_curve(y_te, y_prob)

    target_names = ["ไม่สนใจ", "ปิดการขายสำเร็จ"]
    report_dict = classification_report(y_te, y_pred, zero_division=0,
                                        target_names=target_names, output_dict=True)
    rows = []
    for lbl in target_names:
        d = report_dict[lbl]
        rows.append({"": lbl, "precision": d["precision"], "recall": d["recall"],
                     "f1-score": d["f1-score"], "support": int(d["support"])})
    rows.append({"": "accuracy", "precision": None, "recall": None,
                 "f1-score": report_dict["accuracy"],
                 "support": int(report_dict["macro avg"]["support"])})
    for key in ["macro avg", "weighted avg"]:
        d = report_dict[key]
        rows.append({"": key, "precision": d["precision"], "recall": d["recall"],
                     "f1-score": d["f1-score"], "support": int(d["support"])})
    report_df = pd.DataFrame(rows)

    return ScoringResult(
        model=pipe, metrics=metrics, importance=imp,
        roc={"fpr": fpr, "tpr": tpr, "auc": metrics["ROC-AUC"]},
        confusion=confusion_matrix(y_te, y_pred),
        report=classification_report(y_te, y_pred, zero_division=0,
                                     target_names=target_names),
        report_df=report_df,
        train_size=len(X_tr), test_size=len(X_te),
        cv_auc=(round(cv.mean(), 4), round(cv.std(), 4)),
    )


def grade(p: float) -> str:
    if p >= 0.70:  return "🔥 Hot"
    if p >= 0.40:  return "🌤 Warm"
    return "❄️ Cold"


def score_open_leads(pipe: Pipeline) -> pd.DataFrame:
    """ให้คะแนน lead ที่ยังไม่ปิด — ผลลัพธ์นี้คือสิ่งที่ทีมขายเอาไปใช้จริง"""
    df = run_query(SQL_ALL_LEADS)
    df = df[df["Followup_Status"].isin(["รอการติดต่อ", "อยู่ระหว่างเสนอขาย"])].copy()
    if df.empty:
        return df
    df["Score"] = pipe.predict_proba(df[NUM_FEATURES + CAT_FEATURES])[:, 1]
    df["Score_Pct"] = (df["Score"] * 100).round(1)
    df["Priority"] = df["Score"].apply(grade)
    return df.sort_values("Score", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    r = train("rf")
    print(f"Train {r.train_size} / Test {r.test_size}")
    print("Metrics :", r.metrics)
    print(f"CV AUC  : {r.cv_auc[0]} ± {r.cv_auc[1]}\n")
    print(r.report)
    print(r.importance[["feature_th", "importance"]].head(8).to_string(index=False))
    print("\nTop 10 Hot Leads:")
    print(score_open_leads(r.model)
          .head(10)[["Lead_ID", "Full_Name", "Source_Channel",
                     "Activity_Count", "Score_Pct", "Priority"]]
          .to_string(index=False))