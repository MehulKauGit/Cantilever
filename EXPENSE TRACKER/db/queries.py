import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from db.database import get_connection
from models.expense import Expense, Category

# --- CATEGORY QUERIES ---

def get_categories(db_path: Optional[str] = None) -> List[Category]:
    """Fetch all categories ordered by name."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, color, budget FROM categories ORDER BY name ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [
        Category(
            id=row['id'],
            name=row['name'],
            color=row['color'],
            budget=row['budget'] if 'budget' in row.keys() and row['budget'] is not None else 0.0
        )
        for row in rows
    ]

def add_category(name: str, color: str = "#888888", budget: float = 0.0, db_path: Optional[str] = None) -> int:
    """Insert a new category and return its generated ID."""
    try:
        b_val = max(0.0, float(budget))
    except (ValueError, TypeError):
        b_val = 0.0

    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categories (name, color, budget) VALUES (?, ?, ?);",
        (name.strip(), color.strip(), b_val)
    )
    conn.commit()
    cat_id = cursor.lastrowid
    conn.close()
    return cat_id

def update_category(category_id: int, name: Optional[str] = None, color: Optional[str] = None, budget: Optional[float] = None, db_path: Optional[str] = None) -> bool:
    """Update name, color, or budget cap for a category."""
    fields = []
    params = []
    if name is not None:
        fields.append("name = ?")
        params.append(name.strip())
    if color is not None:
        fields.append("color = ?")
        params.append(color.strip())
    if budget is not None:
        fields.append("budget = ?")
        params.append(max(0.0, budget))

    if not fields:
        return False

    params.append(category_id)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE categories SET {', '.join(fields)} WHERE id = ?;", params)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def delete_category(category_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a category by ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = ?;", (category_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# --- EXPENSE QUERIES ---

def add_expense(amount: float, description: str, category_id: Optional[int], date_str: str, db_path: Optional[str] = None) -> int:
    """Insert a new expense record and return its ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (amount, description, category_id, date) VALUES (?, ?, ?, ?);",
        (amount, description.strip() if description else "", category_id, date_str)
    )
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()
    return expense_id

def get_all_expenses(filters: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> List[Expense]:
    """
    Fetch expenses joined with categories.
    Supported filters:
      - 'start_date': YYYY-MM-DD
      - 'end_date': YYYY-MM-DD
      - 'category_id': int
      - 'search': str (matches description or category name)
    """
    query = """
        SELECT e.id, e.amount, e.description, e.category_id, e.date, e.created_at,
               c.name as category_name, c.color as category_color
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE 1=1
    """
    params = []

    if filters:
        if filters.get('start_date'):
            query += " AND e.date >= ?"
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query += " AND e.date <= ?"
            params.append(filters['end_date'])
        if filters.get('category_id') is not None:
            query += " AND e.category_id = ?"
            params.append(filters['category_id'])
        if filters.get('search'):
            query += " AND (e.description LIKE ? OR c.name LIKE ?)"
            term = f"%{filters['search']}%"
            params.extend([term, term])

    query += " ORDER BY e.date DESC, e.id DESC;"

    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        Expense(
            id=row['id'],
            amount=row['amount'],
            description=row['description'],
            category_id=row['category_id'],
            date=row['date'],
            created_at=row['created_at'],
            category_name=row['category_name'] if row['category_name'] else "Uncategorized",
            category_color=row['category_color'] if row['category_color'] else "#888888"
        )
        for row in rows
    ]

def get_expense_by_id(expense_id: int, db_path: Optional[str] = None) -> Optional[Expense]:
    """Fetch a single expense by ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.amount, e.description, e.category_id, e.date, e.created_at,
               c.name as category_name, c.color as category_color
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE e.id = ?;
    """, (expense_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return Expense(
        id=row['id'],
        amount=row['amount'],
        description=row['description'],
        category_id=row['category_id'],
        date=row['date'],
        created_at=row['created_at'],
        category_name=row['category_name'] if row['category_name'] else "Uncategorized",
        category_color=row['category_color'] if row['category_color'] else "#888888"
    )

def update_expense(expense_id: int, amount: Optional[float] = None, description: Optional[str] = None,
                   category_id: Optional[int] = None, date_str: Optional[str] = None, db_path: Optional[str] = None) -> bool:
    """Update expense fields by ID."""
    fields = []
    params = []

    if amount is not None:
        fields.append("amount = ?")
        params.append(amount)
    if description is not None:
        fields.append("description = ?")
        params.append(description.strip())
    if category_id is not None:
        fields.append("category_id = ?")
        params.append(category_id)
    if date_str is not None:
        fields.append("date = ?")
        params.append(date_str)

    if not fields:
        return False

    params.append(expense_id)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?;", params)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def delete_expense(expense_id: int, db_path: Optional[str] = None) -> bool:
    """Delete expense by ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?;", (expense_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# --- REPORT & SUMMARY QUERIES ---

def get_monthly_summary(year: int, month: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get spending breakdown by category for a specific month.
    Returns list of dicts: [{'category': str, 'color': str, 'total': float}]
    """
    month_str = f"{year:04d}-{month:02d}"
    query = """
        SELECT COALESCE(c.name, 'Uncategorized') as category,
               COALESCE(c.color, '#888888') as color,
               SUM(e.amount) as total
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE strftime('%Y-%m', e.date) = ?
        GROUP BY c.id
        ORDER BY total DESC;
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(query, (month_str,))
    rows = cursor.fetchall()
    conn.close()

    return [{'category': row['category'], 'color': row['color'], 'total': row['total']} for row in rows]

def get_category_budget_analysis(year: int, month: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Compares spending vs budget cap for each category for a month.
    """
    month_str = f"{year:04d}-{month:02d}"
    query = """
        SELECT c.id, c.name, c.color, c.budget,
               COALESCE(SUM(e.amount), 0.0) as spent
        FROM categories c
        LEFT JOIN expenses e ON c.id = e.category_id AND strftime('%Y-%m', e.date) = ?
        GROUP BY c.id
        ORDER BY spent DESC;
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(query, (month_str,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            'id': row['id'],
            'name': row['name'],
            'color': row['color'],
            'budget': row['budget'],
            'spent': row['spent'],
            'remaining': row['budget'] - row['spent'] if row['budget'] > 0 else 0.0,
            'percent_used': round((row['spent'] / row['budget'] * 100), 1) if row['budget'] > 0 else 0.0
        }
        for row in rows
    ]

def get_spending_trend(months: int = 6, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get total monthly spending for the past N months.
    Returns list of dicts: [{'month': 'YYYY-MM', 'total': float}]
    """
    query = """
        SELECT strftime('%Y-%m', date) as month,
               SUM(amount) as total
        FROM expenses
        WHERE date >= date('now', '-' || ? || ' month')
        GROUP BY month
        ORDER BY month ASC;
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(query, (months,))
    rows = cursor.fetchall()
    conn.close()

    return [{'month': row['month'], 'total': row['total']} for row in rows]
