from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Category:
    id: Optional[int]
    name: str
    color: str = "#888888"
    budget: float = 0.0

@dataclass
class Expense:
    id: Optional[int]
    amount: float
    description: str
    category_id: Optional[int]
    date: str  # YYYY-MM-DD format
    created_at: Optional[str] = None
    category_name: Optional[str] = None
    category_color: Optional[str] = None

    def formatted_amount(self, symbol: str = "$") -> str:
        return f"{symbol}{self.amount:,.2f}"

    def date_object(self) -> datetime:
        return datetime.strptime(self.date, "%Y-%m-%d")
