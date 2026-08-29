import duckdb
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from src.config import settings

class RetailTools:
    """Deterministic policy tools invoked by the AI Agent."""
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (settings.PROCESSED_DIR / "northstar_analytics.duckdb")

    def lookup_order(self, order_id: str) -> Dict[str, Any]:
        """Look up order and line items from the analytics warehouse."""
        clean_id = order_id.strip().upper()
        if not self.db_path.exists():
            # Fallback to cleaned CSV if duckdb file not yet created
            csv_path = settings.PROCESSED_DIR / "stg_orders_cleaned.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                match = df[df["order_id"] == clean_id]
                if not match.empty:
                    row = match.iloc[0].to_dict()
                    return {"found": True, "order": row}
            return {"found": False, "error": f"Order {clean_id} not found."}

        con = duckdb.connect(str(self.db_path))
        try:
            res = con.execute("SELECT * FROM stg_orders_cleaned WHERE order_id = ?", [clean_id]).df()
            if not res.empty:
                return {"found": True, "order": res.iloc[0].to_dict()}
            return {"found": False, "error": f"Order {clean_id} not found."}
        finally:
            con.close()

    def evaluate_return_eligibility(
        self,
        order_id: str,
        days_since_delivery: int = 10,
        item_condition: str = "like_new_with_packaging",
        country: str = "US"
    ) -> Dict[str, Any]:
        """Evaluates return eligibility based on NSR-POL-RET-014 rules."""
        order_data = self.lookup_order(order_id)
        if not order_data.get("found"):
            return {
                "eligible": False,
                "reason": f"Order {order_id} could not be verified in database.",
                "policy_citation": "NSR-POL-RET-014, Section 2.130"
            }
        
        order = order_data["order"]
        category = str(order.get("category", "")).lower()
        product_name = order.get("product_name", "")
        unit_price = float(order.get("unit_price", 0.0))
        quantity = abs(int(order.get("quantity", 1)))
        gross_value = round(unit_price * quantity, 2)

        # Rule 1: Grocery / Final Sale Exclusion (Section 4.1)
        if category == "grocery":
            return {
                "eligible": False,
                "order_id": order_id,
                "product_name": product_name,
                "category": order.get("category"),
                "reason": "Grocery items are strictly non-returnable as they are perishable food items.",
                "policy_citation": "NSR-POL-RET-014, Section 4.1",
                "refund_amount": 0.0
            }

        # Rule 2: 30-day Return Window (Section 3)
        if days_since_delivery > 30:
            return {
                "eligible": False,
                "order_id": order_id,
                "product_name": product_name,
                "days_since_delivery": days_since_delivery,
                "reason": f"The return request ({days_since_delivery} days) exceeds the standard 30-day return window.",
                "policy_citation": "NSR-POL-RET-014, Section 3",
                "refund_amount": 0.0
            }

        # Rule 3: Condition and Restocking Fee (Section 3.1)
        restocking_fee_rate = 0.0
        if "missing_packaging" in item_condition.lower() or "used" in item_condition.lower() or "opened" in item_condition.lower():
            restocking_fee_rate = 0.10  # 10% restocking fee

        restocking_fee = round(gross_value * restocking_fee_rate, 2)
        final_refund = round(gross_value - restocking_fee, 2)

        # Rule 4: India jurisdiction note
        india_rider = (country.upper() == "IN" or country.upper() == "INDIA")

        return {
            "eligible": True,
            "order_id": order_id,
            "product_name": product_name,
            "category": order.get("category"),
            "original_amount": gross_value,
            "restocking_fee_applied": restocking_fee,
            "final_refund_amount": final_refund,
            "return_shipping_paid_by": "Company (if defective) / Customer (if change of mind)",
            "policy_citation": "NSR-POL-RET-014, Section 3.1 & Section 6.1",
            "india_consumer_protection_applicable": india_rider
        }

    def get_sizing_guideline(self, product_name: str) -> Dict[str, Any]:
        """Provides sizing recommendations from NSR-DOC-SIZ-001."""
        p_lower = product_name.lower()
        if "denim jacket" in p_lower:
            return {
                "product": product_name,
                "sizing_note": "Denim Jackets run 1 size small. Customers between sizes should size up.",
                "free_exchange_allowed": True,
                "policy_citation": "NSR-DOC-SIZ-001, Section 1 & 2"
            }
        return {
            "product": product_name,
            "sizing_note": "True to size. Check product page centimeter chest/waist measurements.",
            "free_exchange_allowed": True,
            "policy_citation": "NSR-DOC-SIZ-001, Section 1"
        }
