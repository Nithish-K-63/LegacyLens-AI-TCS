"""Authorization and permission policy checks."""

class PermissionMap:
    def __init__(self):
        self.roles = {
            "STANDARD_USER": 1000.0,
            "STORE_MANAGER": 5000.0,
            "FINANCE_ADMIN": 25000.0
        }

    def verify_order_approval(self, user_role: str, order_amount: float, audit_reason: str = None) -> bool:
        """
        Business Rule BR-021:
        ADMIN_OVERRIDE grants approval above configured order limit,
        requiring an explicit non-empty audit reason.
        """
        if user_role == "ADMIN_OVERRIDE":
            if not audit_reason or len(audit_reason.strip()) == 0:
                raise ValueError("ADMIN_OVERRIDE requires an explicit audit reason.")
            return True

        limit = self.roles.get(user_role, 0.0)
        return order_amount <= limit

