import unittest
import os
import tempfile
import sqlite3
from db.database import init_db, get_connection
from db.queries import (
    add_category, get_categories, update_category, delete_category,
    add_expense, get_all_expenses, get_expense_by_id, update_expense, delete_expense,
    get_monthly_summary, get_spending_trend
)
from utils.validators import (
    validate_amount, validate_date, validate_description, validate_category_exists
)

class TestExpenseTrackerCRUD(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for isolated testing
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        init_db(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --- CATEGORY TESTS ---
    def test_categories(self):
        cats = get_categories(self.db_path)
        self.assertGreater(len(cats), 0, "Default categories should be seeded.")

        new_cat_id = add_category("Subscriptions", "#FF00FF", db_path=self.db_path)
        self.assertIsNotNone(new_cat_id)

        updated = update_category(new_cat_id, name="Digital Subscriptions", color="#AA00AA", db_path=self.db_path)
        self.assertTrue(updated)

        all_cats = get_categories(self.db_path)
        names = [c.name for c in all_cats]
        self.assertIn("Digital Subscriptions", names)

        deleted = delete_category(new_cat_id, self.db_path)
        self.assertTrue(deleted)

    # --- EXPENSE CRUD TESTS ---
    def test_expense_crud(self):
        cats = get_categories(self.db_path)
        cat_id = cats[0].id

        # Add expense
        exp_id = add_expense(45.50, "Lunch with team", cat_id, "2026-08-10", self.db_path)
        self.assertIsNotNone(exp_id)

        # Get by ID
        exp = get_expense_by_id(exp_id, self.db_path)
        self.assertIsNotNone(exp)
        self.assertEqual(exp.amount, 45.50)
        self.assertEqual(exp.description, "Lunch with team")
        self.assertEqual(exp.category_id, cat_id)

        # Update expense
        updated = update_expense(exp_id, amount=50.00, description="Fancy Lunch", db_path=self.db_path)
        self.assertTrue(updated)

        exp_updated = get_expense_by_id(exp_id, self.db_path)
        self.assertEqual(exp_updated.amount, 50.00)
        self.assertEqual(exp_updated.description, "Fancy Lunch")

        # Get all expenses with filter
        expenses = get_all_expenses(filters={"search": "Fancy"}, db_path=self.db_path)
        self.assertEqual(len(expenses), 1)

        # Delete expense
        deleted = delete_expense(exp_id, self.db_path)
        self.assertTrue(deleted)
        self.assertIsNone(get_expense_by_id(exp_id, self.db_path))

    # --- REPORT & SUMMARY TESTS ---
    def test_monthly_summary_and_trend(self):
        cats = get_categories(self.db_path)
        cat1 = cats[0].id
        cat2 = cats[1].id

        add_expense(100.0, "Grocery", cat1, "2026-08-01", self.db_path)
        add_expense(50.0, "Snacks", cat1, "2026-08-05", self.db_path)
        add_expense(200.0, "Bus Pass", cat2, "2026-08-02", self.db_path)

        summary = get_monthly_summary(2026, 8, self.db_path)
        self.assertEqual(len(summary), 2)
        total_spent = sum(item['total'] for item in summary)
        self.assertEqual(total_spent, 350.0)

        trend = get_spending_trend(months=3, db_path=self.db_path)
        self.assertGreater(len(trend), 0)

    # --- VALIDATORS TESTS ---
    def test_validators(self):
        # Validate amount
        ok, val, err = validate_amount("12.50")
        self.assertTrue(ok)
        self.assertEqual(val, 12.50)

        ok, val, err = validate_amount("-5")
        self.assertFalse(ok)

        ok, val, err = validate_amount("abc")
        self.assertFalse(ok)

        # Validate date
        ok, err = validate_date("2026-08-12")
        self.assertTrue(ok)

        ok, err = validate_date("12-08-2026")
        self.assertFalse(ok)

        # Validate description
        ok, err = validate_description("Valid text")
        self.assertTrue(ok)

        ok, err = validate_description("x" * 201, max_length=200)
        self.assertFalse(ok)

        # Validate category exists
        conn = get_connection(self.db_path)
        cats = get_categories(self.db_path)
        ok, err = validate_category_exists(cats[0].id, conn)
        self.assertTrue(ok)

        ok, err = validate_category_exists(99999, conn)
        self.assertFalse(ok)
        conn.close()

if __name__ == "__main__":
    unittest.main()
