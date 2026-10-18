#!/usr/bin/env python3
import json
import sys
from client import AgenticProductReturnFraudDetector

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        detector = AgenticProductReturnFraudDetector()
        claim = {"order_id": "ORD-9912", "claimed_reason": "wrong size", "item_price_usd": 350.0, "carrier_weight_kg": 0.2, "expected_weight_kg": 1.2, "days_held": 28}
        history = {"total_orders": 4, "past_returns_count": 3, "past_fraud_disputes": 1}
        res = detector.evaluate_return_request(claim, history)
        assert res["composite_fraud_risk_score"] > 60.0
        assert res["enforced_action"] == "FLAG_FOR_MANUAL_INSPECTION_HOLD_REFUND"
        print(f"[TEST PASS] Return Fraud Detector Score: {res['composite_fraud_risk_score']}/100")
        sys.exit(0)

    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            if method == "initialize":
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"serverInfo": {"name": "genpark-return-fraud-detector", "version": "1.0.0"}}}))
            elif method == "tools/list":
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": [{"name": "evaluate_return_request", "description": "Evaluate return fraud risk and enforce restocking policy"}]}}))
            elif method == "tools/call":
                args = req.get("params", {}).get("arguments", {})
                detector = AgenticProductReturnFraudDetector()
                out = detector.evaluate_return_request(args.get("return_claim", {}), args.get("customer_history", {}))
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(out)}]}}))
            else:
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
