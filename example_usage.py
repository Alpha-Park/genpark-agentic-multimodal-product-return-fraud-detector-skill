from client import AgenticProductReturnFraudDetector

def main():
    detector = AgenticProductReturnFraudDetector()
    claim = {
        "order_id": "ORD-4481",
        "claimed_reason": "did not like color",
        "item_price_usd": 480.0,
        "carrier_weight_kg": 0.3,
        "expected_weight_kg": 1.5,
        "days_held": 29
    }
    history = {"total_orders": 3, "past_returns_count": 2, "past_fraud_disputes": 0}
    res = detector.evaluate_return_request(claim, history)
    print("--- Return Fraud Sentinel Evaluation ---")
    print(f"Order: {res['order_id']} | Risk Score: {res['composite_fraud_risk_score']}/100")
    print(f"Action: {res['enforced_action']}")
    print(f"Restocking Fee: {res['restocking_fee_percentage']}%")

if __name__ == "__main__":
    main()
