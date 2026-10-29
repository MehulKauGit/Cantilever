from datetime import datetime, date
from typing import Tuple, Optional
import sqlite3

def validate_amount(amount_str: str) -> Tuple[bool, float, str]:
    """Validates that amount is a positive float."""
    try:
        val = float(amount_str)
        if val <= 0:
            return False, 0.0, "Amount must be greater than zero."
        if val > 1_000_000_000:
            return False, 0.0, "Amount exceeds maximum allowed limit."
        return True, round(val, 2), ""
    except (ValueError, TypeError):
        return False, 0.0, "Please enter a valid numeric amount."

def validate_date(date_str: str, allow_future: bool = False) -> Tuple[bool, str]:
    """Validates date format (YYYY-MM-DD) and optional future date constraint."""
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if not allow_future and parsed_date > date.today():
            return False, "Expense date cannot be in the future."
        return True, ""
    except (ValueError, TypeError):
        return False, "Date must be in YYYY-MM-DD format."

def validate_description(description: str, max_length: int = 200) -> Tuple[bool, str]:
    """Validates description string length."""
    if description and len(description.strip()) > max_length:
        return False, f"Description cannot exceed {max_length} characters."
    return True, ""

def validate_category_exists(category_id: Optional[int], conn: sqlite3.Connection) -> Tuple[bool, str]:
    """Validates whether category_id exists in the categories table."""
    if category_id is None:
        return True, ""
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM categories WHERE id = ?;", (category_id,))
    if cursor.fetchone() is None:
        return False, f"Category ID {category_id} does not exist."
    return True, ""
