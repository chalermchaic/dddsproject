"""
Unit tests สำหรับฟังก์ชันและสูตรคำนวณแกนของ Data Science ทั้ง 4 โมเดล
(RFM Segmentation, Customer Health & Churn, Lead Scoring, Campaign ROI)
ทดสอบความถูกต้องของ logic, boundary values, edge cases และความสอดคล้องของสูตร
"""
import numpy as np
import pandas as pd
import pytest

from analytics.campaign_roi import channel_significance
from analytics.churn_health import WEIGHTS, _norm
from analytics.lead_scoring import grade
from analytics.rfm_segmentation import _label, _score


# =====================================================================
# 1. RFM Segmentation Unit Tests
# =====================================================================
class TestRFMSegmentation:
    def test_rfm_label_boundaries(self):
        """ตรวจสอบการจัดกลุ่มลูกค้าตามคะแนน R, F, M ให้ตรงตามเงื่อนไข if/elif ทุกกรณี"""
        # Champions: r>=4, f>=4, m>=4
        assert _label(5, 5, 5) == "Champions"
        assert _label(4, 4, 4) == "Champions"

        # Loyal Customers: r>=3, f>=3 (แต่ไม่เข้า champions เช่น m < 4)
        assert _label(3, 3, 2) == "Loyal Customers"
        assert _label(4, 4, 3) == "Loyal Customers"
        assert _label(5, 3, 1) == "Loyal Customers"

        # New Customers: r>=4, f<=2
        assert _label(5, 1, 1) == "New Customers"
        assert _label(4, 2, 5) == "New Customers"

        # Potential: r>=3, m>=3 (และ f<=2 ไม่เข้า loyal)
        assert _label(3, 1, 4) == "Potential"
        assert _label(3, 2, 3) == "Potential"

        # At Risk: r<=2, f>=3
        assert _label(1, 3, 1) == "At Risk"
        assert _label(2, 5, 5) == "At Risk"

        # Lost: อื่นๆ ทั้งหมด
        assert _label(1, 1, 1) == "Lost"
        assert _label(2, 2, 2) == "Lost"
        assert _label(1, 2, 5) == "Lost"

    def test_rfm_score_quintile(self):
        """ตรวจสอบการแปลงค่าเป็น Quintile 1-5 และการ reverse คะแนนกรณี Recency"""
        # สร้าง Series 20 ค่า เรียงลำดับจากน้อยไปมาก
        data = pd.Series(range(1, 21))

        scores_forward = _score(data, reverse=False)
        assert set(scores_forward.unique()) == {1, 2, 3, 4, 5}
        assert scores_forward.iloc[0] == 1
        assert scores_forward.iloc[-1] == 5

        scores_reverse = _score(data, reverse=True)
        assert set(scores_reverse.unique()) == {1, 2, 3, 4, 5}
        # กรณี reverse (เช่น Recency ยิ่งน้อยยิ่งดี) ค่าน้อยสุดต้องได้คะแนน 5
        assert scores_reverse.iloc[0] == 5
        assert scores_reverse.iloc[-1] == 1

    def test_rfm_score_edge_case_insufficient_data(self):
        """กรณีข้อมูลมีเพียง 1 ค่า หรือเป็น NaN ทั้งหมดจน qcut โยน ValueError ต้องตกไปที่ fallback score 3 ทุกตัว"""
        single_data = pd.Series([100.0])
        fallback_scores = _score(single_data, reverse=False)
        assert (fallback_scores == 3).all()

        fallback_reverse = _score(single_data, reverse=True)
        # 6 - 3 = 3
        assert (fallback_reverse == 3).all()

        nan_data = pd.Series([np.nan, np.nan, np.nan])
        nan_scores = _score(nan_data, reverse=False)
        assert (nan_scores == 3).all()


# =====================================================================
# 2. Churn & Customer Health Score Unit Tests
# =====================================================================
class TestChurnHealth:
    def test_churn_weights_sum_100(self):
        """น้ำหนักรวมของ Health Score ทั้ง 5 มิติ ต้องเท่ากับ 100 พอดี"""
        assert sum(WEIGHTS.values()) == 100
        assert set(WEIGHTS.keys()) == {"recency", "frequency", "monetary", "service", "resolution"}
        for k, v in WEIGHTS.items():
            assert v > 0, f"น้ำหนักมิติ {k} ต้องมากกว่า 0"

    def test_churn_norm_range_and_direction(self):
        """ทดสอบการ normalization ให้อยู่ในช่วง [0, 1] และการกลับทิศ (invert)"""
        s = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])

        norm_normal = _norm(s, invert=False)
        assert (norm_normal >= 0.0).all() and (norm_normal <= 1.0).all()
        assert norm_normal.iloc[0] == 0.0
        assert norm_normal.iloc[-1] == 1.0

        norm_inverted = _norm(s, invert=True)
        assert (norm_inverted >= 0.0).all() and (norm_inverted <= 1.0).all()
        # เมื่อ invert=True ค่าน้อยที่สุดควรได้ 1.0 และค่ามากที่สุดควรได้ 0.0
        assert norm_inverted.iloc[0] == 1.0
        assert norm_inverted.iloc[-1] == 0.0

    def test_churn_norm_edge_cases(self):
        """ทดสอบ edge case: ค่าเท่ากันหมด (hi == lo), cap clip, และค่า missing (NaN)"""
        # กรณี hi == lo ทุกค่าต้องได้ 0.5
        same_s = pd.Series([5.0, 5.0, 5.0])
        assert (_norm(same_s, invert=False) == 0.5).all()
        assert (_norm(same_s, invert=True) == 0.5).all()

        # กรณี cap: ค่าที่เกิน cap ต้องถูกตัดลงมาเท่ากับ cap
        s_with_high = pd.Series([0.0, 50.0, 200.0])
        capped_norm = _norm(s_with_high, invert=False, cap=100.0)
        # หลัง cap: [0, 50, 100] -> normalized: [0.0, 0.5, 1.0]
        assert capped_norm.iloc[2] == 1.0
        assert capped_norm.iloc[1] == 0.5

        # กรณี NaN: ต้อง fillna ด้วย median แล้วไม่ error
        s_with_nan = pd.Series([10.0, np.nan, 30.0])
        norm_nan = _norm(s_with_nan)
        assert not norm_nan.isna().any()
        assert norm_nan.iloc[1] == 0.5  # median คือ 20.0 ซึ่งอยู่ตรงกลางระหว่าง 10 และ 30


# =====================================================================
# 3. Lead Scoring Unit Tests
# =====================================================================
class TestLeadScoring:
    def test_lead_scoring_grade_boundaries(self):
        """ตรวจสอบฟังก์ชัน grade(p) ตาม threshold: Hot (>=0.70), Warm (>=0.40), Cold (<0.40)"""
        # Hot zone (>= 0.70)
        assert grade(1.0) == "🔥 Hot"
        assert grade(0.70) == "🔥 Hot"
        assert grade(0.85) == "🔥 Hot"

        # Warm zone (0.40 <= p < 0.70)
        assert grade(0.6999) == "🌤 Warm"
        assert grade(0.40) == "🌤 Warm"
        assert grade(0.55) == "🌤 Warm"

        # Cold zone (< 0.40)
        assert grade(0.3999) == "❄️ Cold"
        assert grade(0.10) == "❄️ Cold"
        assert grade(0.0) == "❄️ Cold"

    def test_lead_scoring_grade_edge_values(self):
        """ทดสอบ boundary edges ระหว่าง 0.70 และ 0.40"""
        assert grade(0.70) != grade(0.69)
        assert grade(0.40) != grade(0.39)


# =====================================================================
# 4. Campaign ROI Unit Tests
# =====================================================================
class TestCampaignROI:
    def test_campaign_roi_chi_square_shape(self, db):
        """ทดสอบฟังก์ชัน channel_significance() กับฐานข้อมูลจริง"""
        result = channel_significance()

        assert isinstance(result, dict)
        assert "chi2" in result and "p_value" in result and "dof" in result and "conclusion" in result

        # ตรวจสอบขอบเขตค่าทางสถิติ
        assert result["chi2"] >= 0.0
        assert 0.0 <= result["p_value"] <= 1.0
        assert result["dof"] >= 1
        assert isinstance(result["conclusion"], str)
        assert len(result["conclusion"]) > 0

        # ตรวจสอบตรรกะของ conclusion เทียบกับ p-value
        if result["p_value"] < 0.05:
            assert "อย่างมีนัยสำคัญ" in result["conclusion"]
        else:
            assert "ยังไม่พบความแตกต่างอย่างมีนัยสำคัญ" in result["conclusion"]
