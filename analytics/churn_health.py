"""
Customer Health Score (0–100) + Churn Risk
วิธี: Weighted Scoring จาก 5 มิติ แล้วตรวจสอบด้วย Logistic Regression
นิยาม Churn = ไม่มีคำสั่งซื้อยืนยันเกิน CHURN_DAYS วัน
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from db.connection import run_query

CHURN_DAYS = 180

# น้ำหนักแต่ละมิติ (รวม = 100)
WEIGHTS = {
    "recency":    35,   # ซื้อล่าสุดเมื่อไร
    "frequency":  20,   # ซื้อบ่อยแค่ไหน
    "monetary":   15,   # มูลค่ารวม
    "service":    20,   # ภาระปัญหา (ticket)
    "resolution": 10,   # ความเร็วในการแก้ปัญหา
}

SQL = """
SELECT  r.Customer_ID, r.Customer_Type, r.Recency_Days, r.Frequency, r.Monetary,
        COALESCE(h.Ticket_Count, 0)       AS Ticket_Count,
        COALESCE(h.Critical_Tickets, 0)   AS Critical_Tickets,
        h.Avg_Resolution_Days,
        COALESCE(h.Total_Messages, 0)     AS Total_Messages,
        cu.Company_Name,
        CAST(julianday('now') - julianday(cu.Membership_Date) AS INTEGER) AS Tenure_Days
FROM V_CUSTOMER_RFM r
JOIN CUSTOMER cu       ON cu.Customer_ID = r.Customer_ID
LEFT JOIN V_SERVICE_HEALTH h ON h.Customer_ID = r.Customer_ID;
"""


def _norm(s: pd.Series, invert: bool = False, cap: float | None = None) -> pd.Series:
    """ปรับค่าให้อยู่ในช่วง 0–1 (invert=True → ค่ามากคือแย่)"""
    x = s.fillna(s.median() if s.notna().any() else 0).astype(float)
    if cap is not None:
        x = x.clip(upper=cap)
    lo, hi = x.min(), x.max()
    n = pd.Series(0.5, index=x.index) if hi == lo else (x - lo) / (hi - lo)
    return 1 - n if invert else n


def build_health() -> pd.DataFrame:
    df = run_query(SQL)
    if df.empty:
        return df

    df["Monetary"] = df["Monetary"].fillna(0)
    df["Tickets_Per_Year"] = (df["Ticket_Count"] /
                              (df["Tenure_Days"].clip(lower=30) / 365)).round(2)

    parts = {
        "recency":    _norm(df["Recency_Days"], invert=True, cap=540),
        "frequency":  _norm(df["Frequency"], cap=6),
        "monetary":   _norm(np.log1p(df["Monetary"])),
        "service":    _norm(df["Tickets_Per_Year"] + df["Critical_Tickets"] * 0.5,
                            invert=True, cap=12),
        "resolution": _norm(df["Avg_Resolution_Days"], invert=True, cap=21),
    }
    df["Health_Score"] = sum(parts[k] * w for k, w in WEIGHTS.items()).round(1)

    # เก็บคะแนนย่อยไว้อธิบายผล (ใช้ทำ radar chart บนแดชบอร์ด)
    for k, v in parts.items():
        df[f"sub_{k}"] = (v * WEIGHTS[k]).round(1)

    df["Risk_Level"] = pd.cut(
        df["Health_Score"], bins=[-1, 40, 65, 101],
        labels=["🔴 เสี่ยงสูง", "🟡 เฝ้าระวัง", "🟢 แข็งแรง"])
    df["Is_Churn"] = (df["Recency_Days"] > CHURN_DAYS).astype(int)
    df["Churn_Prob_Pct"] = (100 - df["Health_Score"]).round(1)
    return df.sort_values("Health_Score").reset_index(drop=True)


def validate_with_model(df: pd.DataFrame) -> dict:
    """ตรวจว่า Health Score สอดคล้องกับ Churn จริงไหม (สำหรับเขียนรายงาน)"""
    feats = ["Frequency", "Monetary", "Ticket_Count",
             "Critical_Tickets", "Tickets_Per_Year", "Tenure_Days"]
    X = df[feats].fillna(0)
    y = df["Is_Churn"]
    if y.nunique() < 2 or len(df) < 40:
        return {"note": "ข้อมูลไม่พอสำหรับตรวจสอบด้วยโมเดล"}

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42)
    m = make_pipeline(StandardScaler(),
                      LogisticRegression(max_iter=1000, class_weight="balanced"))
    m.fit(X_tr, y_tr)

    auc_model = roc_auc_score(y_te, m.predict_proba(X_te)[:, 1])
    auc_rule = roc_auc_score(y, 100 - df["Health_Score"])   # กฎถ่วงน้ำหนักล้วน
    coef = pd.Series(m[-1].coef_[0], index=feats).sort_values(key=abs, ascending=False)
    return {
        "AUC_LogReg": round(auc_model, 4),
        "AUC_HealthScore_Rule": round(auc_rule, 4),
        "Churn_Rate_%": round(100 * y.mean(), 2),
        "Top_Drivers": coef.round(3).to_dict(),
    }


def risk_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("Risk_Level", observed=True)
              .agg(Customers=("Customer_ID", "count"),
                   Avg_Health=("Health_Score", "mean"),
                   Avg_Recency=("Recency_Days", "mean"),
                   Revenue_At_Stake=("Monetary", "sum"))
              .round(1).reset_index())


if __name__ == "__main__":
    h = build_health()
    print(risk_summary(h).to_string(index=False))
    print("\nValidation:", validate_with_model(h))
    print("\n🔴 10 ลูกค้าที่ควรติดตามด่วนที่สุด:")
    print(h.head(10)[["Customer_ID", "Company_Name", "Recency_Days",
                      "Ticket_Count", "Health_Score", "Risk_Level"]]
          .to_string(index=False))