"""
AI Multimodal Product Return Fraud Detector (Pure Stdlib)
Official Website: https://www.genpark.ai | LinkedIn: https://www.llinkedin.com/company/92955550
"""
from typing import Dict, Any, List, Optional

class AgenticProductReturnFraudDetector:
    def __init__(self, detector_name: str = "GenPark-Return-Fraud-Sentinel"):
        self.detector_name = detector_name

    def calculate_weight_discrepancy_score(self, carrier_weight: float, expected_weight: float) -> float:
        if expected_weight <= 0:
            return 0.0
        delta = abs(carrier_weight - expected_weight) / expected_weight
        # Over 40% weight discrepancy indicates empty-box or wrong-item fraud
        return min(1.0, delta * 2.5) if delta > 0.15 else 0.0

    def evaluate_return_request(self, return_claim: Dict[str, Any], customer_history: Dict[str, Any]) -> Dict[str, Any]:
        total_orders = int(customer_history.get("total_orders", 1))
        past_returns = int(customer_history.get("past_returns_count", 0))
        past_disputes = int(customer_history.get("past_fraud_disputes", 0))
        
        return_rate = past_returns / max(1, total_orders)
        carrier_w = float(return_claim.get("carrier_weight_kg", 1.0))
        expected_w = float(return_claim.get("expected_weight_kg", 1.0))
        days_held = int(return_claim.get("days_held", 5))
        price = float(return_claim.get("item_price_usd", 100.0))
        reason = return_claim.get("claimed_reason", "defective").lower()
        
        weight_risk = self.calculate_weight_discrepancy_score(carrier_w, expected_w)
        
        # Wardrobing indicator: luxury item returned on day 28-30 with 'size fit' reason
        wardrobing_risk = 0.0
        if price > 200.0 and days_held >= 25 and ("fit" in reason or "size" in reason):
            wardrobing_risk = 0.45
            
        history_risk = min(1.0, (return_rate * 0.5) + (past_disputes * 0.3))
        
        composite_risk_score = round(min(1.0, (weight_risk * 0.4) + (wardrobing_risk * 0.3) + (history_risk * 0.3)) * 100.0, 1)
        
        if composite_risk_score >= 70.0:
            action = "FLAG_FOR_MANUAL_INSPECTION_HOLD_REFUND"
            restocking_fee_pct = 25.0
        elif composite_risk_score >= 40.0:
            action = "REQUIRE_PHYSICAL_WAREHOUSE_SCAN_BEFORE_REFUND"
            restocking_fee_pct = 15.0
        else:
            action = "APPROVE_AUTONOMOUS_INSTANT_REFUND"
            restocking_fee_pct = 0.0
            
        return {
            "detector": self.detector_name,
            "order_id": return_claim.get("order_id", "ORD-000"),
            "composite_fraud_risk_score": composite_risk_score,
            "risk_factors": {
                "weight_discrepancy_risk": round(weight_risk, 2),
                "wardrobing_risk": round(wardrobing_risk, 2),
                "customer_history_return_rate": round(return_rate, 2)
            },
            "enforced_action": action,
            "restocking_fee_percentage": restocking_fee_pct,
            "verdict": "FRAUD_AUDIT_COMPLETED"
        }
