"""
Campaign Performance & ROI
ตัวชี้วัด: Conversion Rate, CPL, CAC, ROAS, ROI + วิเคราะห์รายช่องทาง
"""
import numpy as np
import pandas as pd
from scipy import stats

from db.connection import run_query


def campaign_overview() -> pd.DataFrame:
    df = run_query("SELECT * FROM V_CAMPAIGN_ROI ORDER BY ROI DESC")
    if df.empty:
        return df
    df["CAC"] = np.where(
        df["Converted_Leads"] > 0,
        (df["Budget_Cost"] / df["Converted_Leads"]).round(2),
        np.nan,
    )
    df["ROAS"] = np.where(
        df["Budget_Cost"] > 0,
        (df["Revenue"] / df["Budget_Cost"]).round(2),
        np.nan,
    )
    df["ROI_%"] = (df["ROI"] * 100).round(2)
    df["Avg_Deal_Size"] = np.where(
        df["Converted_Leads"] > 0,
        (df["Revenue"] / df["Converted_Leads"]).round(2),
        np.nan,
    )
    df["Verdict"] = pd.cut(df["ROI_%"], bins=[-1e9, 0, 100, 1e9],
                           labels=["❌ ขาดทุน", "⚠️ พอไปได้", "✅ คุ้มค่า"])
    return df


SQL_CHANNEL = """
SELECT  l.Source_Channel,
        COUNT(DISTINCT l.Lead_ID) AS Total_Leads,
        COUNT(DISTINCT CASE WHEN l.Followup_Status='ปิดการขายสำเร็จ'
                            THEN l.Lead_ID END) AS Converted,
        COALESCE(SUM(CASE WHEN s.Sale_Status='ปิดการขายสำเร็จ'
                          THEN s.Total_Amount END), 0) AS Revenue
FROM LEAD l
LEFT JOIN SALE s ON s.Lead_ID = l.Lead_ID
GROUP BY l.Source_Channel;
"""

SQL_MONTHLY = """
SELECT  strftime('%Y-%m', s.Confirmed_At) AS Month,
        c.Campaign_Name,
        COUNT(DISTINCT s.Sale_ID) AS Orders,
        SUM(s.Total_Amount)       AS Revenue
FROM SALE s
JOIN LEAD l     ON l.Lead_ID = s.Lead_ID
LEFT JOIN CAMPAIGN c ON c.Campaign_ID = l.Campaign_ID
WHERE s.Sale_Status = 'ปิดการขายสำเร็จ' AND s.Confirmed_At IS NOT NULL
GROUP BY Month, c.Campaign_Name
ORDER BY Month;
"""

SQL_FUNNEL = """
SELECT  'ผู้สนใจทั้งหมด' AS Stage, COUNT(*) AS N, 1 AS ord FROM LEAD
UNION ALL SELECT 'ได้รับการติดตาม', COUNT(DISTINCT Lead_ID), 2 FROM LEAD_ACTIVITY
UNION ALL SELECT 'ออกใบเสนอราคา',  COUNT(DISTINCT Lead_ID), 3 FROM SALE
UNION ALL SELECT 'ปิดการขายสำเร็จ', COUNT(DISTINCT Lead_ID), 4
          FROM SALE WHERE Sale_Status='ปิดการขายสำเร็จ'
ORDER BY ord;
"""

SQL_TOP_PRODUCT = """
SELECT  p.Product_Name, p.Product_Category,
        SUM(d.Quantity) AS Units, ROUND(SUM(d.Subtotal),2) AS Revenue
FROM SALE_DETAIL d
JOIN SALE s    ON s.Sale_ID = d.Sale_ID AND s.Sale_Status='ปิดการขายสำเร็จ'
JOIN PRODUCT p ON p.Product_ID = d.Product_ID
GROUP BY p.Product_ID
ORDER BY Revenue DESC;
"""


def channel_performance() -> pd.DataFrame:
    df = run_query(SQL_CHANNEL)
    df["Conversion_Rate_%"] = (100 * df["Converted"] /
                               df["Total_Leads"].replace(0, pd.NA)).round(2)
    df["Revenue_Per_Lead"] = (df["Revenue"] /
                              df["Total_Leads"].replace(0, pd.NA)).round(2)
    return df.sort_values("Conversion_Rate_%", ascending=False)


def monthly_trend() -> pd.DataFrame:
    return run_query(SQL_MONTHLY)


def funnel() -> pd.DataFrame:
    df = run_query(SQL_FUNNEL)
    top = df["N"].iloc[0]
    df["Pct_of_Total"] = (100 * df["N"] / top).round(1)
    df["Drop_Off_%"] = (100 * (1 - df["N"] / df["N"].shift(1))).round(1).fillna(0)
    return df


def top_products(n: int = 10) -> pd.DataFrame:
    return run_query(SQL_TOP_PRODUCT).head(n)


def channel_significance() -> dict:
    """Chi-square: ช่องทางที่มาส่งผลต่ออัตราปิดการขายอย่างมีนัยสำคัญหรือไม่"""
    df = channel_performance()
    table = df[["Converted"]].copy()
    table["Not_Converted"] = df["Total_Leads"] - df["Converted"]
    chi2, p, dof, _ = stats.chi2_contingency(table.values)
    return {
        "chi2": round(chi2, 3), "p_value": round(p, 5), "dof": dof,
        "conclusion": ("ช่องทางที่มามีผลต่อการปิดการขายอย่างมีนัยสำคัญ (p < 0.05)"
                       if p < 0.05 else "ยังไม่พบความแตกต่างอย่างมีนัยสำคัญ"),
    }


if __name__ == "__main__":
    print("=== Campaign ROI ===")
    print(campaign_overview()[["Campaign_Name", "Total_Leads", "Conversion_Rate",
                               "Cost_Per_Lead", "ROI_%", "Verdict"]].to_string(index=False))
    print("\n=== Channel ===")
    print(channel_performance().to_string(index=False))
    print("\n=== Funnel ===")
    print(funnel().to_string(index=False))
    print("\n=== Chi-square ===", channel_significance())