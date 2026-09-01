"""
RFM Segmentation + K-Means (unsupervised)
R = Recency (ยิ่งน้อยยิ่งดี) | F = Frequency | M = Monetary
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from db.connection import run_query

SEGMENT_COLOR = {
    "Champions":       "#2E7D32",
    "Loyal Customers": "#66BB6A",
    "Potential":       "#42A5F5",
    "New Customers":   "#AB47BC",
    "At Risk":         "#FFA726",
    "Lost":            "#EF5350",
}


def load_rfm() -> pd.DataFrame:
    df = run_query("SELECT * FROM V_CUSTOMER_RFM")
    df["Monetary"] = df["Monetary"].fillna(0.0)
    return df


def _score(series: pd.Series, reverse: bool = False) -> pd.Series:
    """ให้คะแนน 1–5 ด้วย quintile — reverse=True สำหรับ Recency (น้อย=ดี)"""
    try:
        q = pd.qcut(series.rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    except ValueError:                       # ข้อมูลกระจุกเกินไป
        q = pd.Series(3, index=series.index)
    q = q.astype(int)
    return 6 - q if reverse else q


def _label(r: int, f: int, m: int) -> str:
    if r >= 4 and f >= 4 and m >= 4:  return "Champions"
    if r >= 3 and f >= 3:             return "Loyal Customers"
    if r >= 4 and f <= 2:             return "New Customers"
    if r >= 3 and m >= 3:             return "Potential"
    if r <= 2 and f >= 3:             return "At Risk"
    return "Lost"


def build_rfm() -> pd.DataFrame:
    df = load_rfm()
    if df.empty:
        return df
    df["R_Score"] = _score(df["Recency_Days"], reverse=True)
    df["F_Score"] = _score(df["Frequency"])
    df["M_Score"] = _score(df["Monetary"])
    df["RFM_Cell"] = (df["R_Score"].astype(str) + df["F_Score"].astype(str)
                      + df["M_Score"].astype(str))
    df["RFM_Total"] = df[["R_Score", "F_Score", "M_Score"]].sum(axis=1)
    df["Segment"] = df.apply(
        lambda x: _label(x["R_Score"], x["F_Score"], x["M_Score"]), axis=1)
    return df.sort_values("RFM_Total", ascending=False).reset_index(drop=True)


def add_kmeans(df: pd.DataFrame, k: int = 4) -> tuple[pd.DataFrame, float]:
    """จัดกลุ่มด้วย K-Means (log-transform เพื่อลด skew) → คืน silhouette score"""
    if len(df) < k * 3:
        df["Cluster"] = 0
        return df, 0.0
    X = np.column_stack([
        np.log1p(df["Recency_Days"].clip(lower=0)),
        np.log1p(df["Frequency"]),
        np.log1p(df["Monetary"]),
    ])
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xs)
    df = df.copy()
    df["Cluster"] = km.labels_
    return df, round(silhouette_score(Xs, km.labels_), 4)


def elbow_data(df: pd.DataFrame, k_max: int = 8) -> pd.DataFrame:
    X = StandardScaler().fit_transform(np.column_stack([
        np.log1p(df["Recency_Days"].clip(lower=0)),
        np.log1p(df["Frequency"]), np.log1p(df["Monetary"])]))
    rows = []
    for k in range(2, k_max + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
        rows.append({"k": k, "inertia": km.inertia_,
                     "silhouette": round(silhouette_score(X, km.labels_), 4)})
    return pd.DataFrame(rows)


def segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    s = (df.groupby("Segment")
           .agg(Customers=("Customer_ID", "count"),
                Avg_Recency=("Recency_Days", "mean"),
                Avg_Frequency=("Frequency", "mean"),
                Avg_Monetary=("Monetary", "mean"),
                Total_Revenue=("Monetary", "sum"))
           .round(1).reset_index())
    s["Revenue_Share_%"] = (100 * s["Total_Revenue"] / s["Total_Revenue"].sum()).round(1)
    return s.sort_values("Total_Revenue", ascending=False)


ACTION = {
    "Champions":       "เสนอสิทธิ์ VIP / ขอรีวิว / Upsell แพ็กเกจระดับสูง",
    "Loyal Customers": "โปรแกรมสะสมแต้ม / แนะนำสินค้าเสริม (Cross-sell)",
    "Potential":       "ส่งโปรโมชันกระตุ้นการซื้อซ้ำภายใน 30 วัน",
    "New Customers":   "Onboarding + ติดตามความพึงพอใจหลังใช้งาน",
    "At Risk":         "โทรติดตามด่วน + เสนอส่วนลดพิเศษดึงกลับ",
    "Lost":            "แคมเปญ Win-back ต้นทุนต่ำ / สำรวจเหตุผลที่เลิกใช้",
}


if __name__ == "__main__":
    rfm = build_rfm()
    rfm, sil = add_kmeans(rfm, k=4)
    print(segment_summary(rfm).to_string(index=False))
    print(f"\nSilhouette Score (k=4): {sil}")
    print("\nTop 10 Champions:")
    print(rfm[rfm.Segment == "Champions"]
          .head(10)[["Customer_ID", "Recency_Days", "Frequency", "Monetary", "RFM_Cell"]]
          .to_string(index=False))