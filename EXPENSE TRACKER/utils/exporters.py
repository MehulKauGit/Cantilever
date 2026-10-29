import csv
from typing import List
from models.expense import Expense

def export_expenses_to_csv(expenses: List[Expense], filepath: str) -> bool:
    """
    Exports a list of Expense objects to a CSV file.
    """
    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write Header
            writer.writerow(["ID", "Date", "Category", "Description", "Amount ($)", "Created At"])
            
            # Write Rows
            for exp in expenses:
                writer.writerow([
                    exp.id,
                    exp.date,
                    exp.category_name,
                    exp.description or "",
                    f"{exp.amount:.2f}",
                    exp.created_at or ""
                ])
        return True
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return False
