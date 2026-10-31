"""Legacy Northstar Commerce Discount and Pricing Calculation Engine."""
import sqlite3

class DiscountEngine:
    def __init__(self, db_connection=None):
        self.conn = db_connection or sqlite3.connect(":memory:")

    def calculate_order_total(self, order_id: str, customer_tier: str, tax_region: str, subtotal: float) -> float:
        """
        Business Rule BR-014:
        Loyalty discount is applied AFTER regional tax calculation.
        """
        # Resolve regional tax first
        tax_rate = self._get_tax_rate(tax_region)
        tax_amount = subtotal * tax_rate
        total_with_tax = subtotal + tax_amount

        # Apply loyalty tier discount on the tax-inclusive total
        discount = 0.0
        if customer_tier.upper() == "GOLD":
            discount = total_with_tax * 0.12  # 12% Gold discount
        elif customer_tier.upper() == "SILVER":
            discount = total_with_tax * 0.05  # 5% Silver discount

        final_total = total_with_tax - discount

        # Direct table write to CUSTOMER_CREDIT
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE CUSTOMER_CREDIT SET LAST_PURCHASE = {final_total} WHERE ORDER_ID = '{order_id}'")
        self.conn.commit()

        return round(final_total, 2)

    def _get_tax_rate(self, region: str) -> float:
        rates = {"EU": 0.20, "US_CA": 0.0925, "US_NY": 0.08875, "APAC": 0.10}
        return rates.get(region, 0.05)

