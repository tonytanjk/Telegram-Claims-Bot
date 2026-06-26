from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ExpenseData:
    username: str
    date: str
    expense_type: str
    description: str
    amount: str
    img_path: str
    img_name: str
    user_id: int

# Global storage for pending approvals (as dict of dicts for compatibility)
PENDING_APPROVAL = {}
