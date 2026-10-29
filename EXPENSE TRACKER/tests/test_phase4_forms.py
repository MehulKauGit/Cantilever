import unittest
import time
from unittest.mock import patch
from db.database import init_db
from db.queries import get_all_expenses, get_categories
from ui.app import ExpenseTrackerApp

class TestPhase4Forms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.app = ExpenseTrackerApp()

    def tearDown(self):
        self.app.destroy()

    @patch("tkinter.messagebox.showinfo")
    @patch("tkinter.messagebox.showerror")
    @patch("tkinter.messagebox.showwarning")
    def test_add_expense_form_validation_and_submission(self, mock_warn, mock_err, mock_info):
        add_view = self.app.views["add_expense"]
        
        # Test invalid amount submission
        add_view.amount_entry.delete(0, 'end')
        add_view.amount_entry.insert(0, "-20.00")
        add_view.date_entry.delete(0, 'end')
        add_view.date_entry.insert(0, "2026-08-12")
        add_view.save_expense()
        
        # Status should show validation failure
        self.assertIn("Amount must be greater than zero", add_view.status_lbl.cget("text"))

    def test_dashboard_table_population(self):
        dash_view = self.app.views["dashboard"]
        dash_view.refresh()
        
        # Check Treeview contains rows corresponding to DB expenses
        children = dash_view.tree.get_children()
        all_exp = get_all_expenses()
        self.assertEqual(len(children), len(all_exp))

    @patch("tkinter.messagebox.showinfo")
    @patch("tkinter.messagebox.showerror")
    @patch("tkinter.messagebox.showwarning")
    def test_settings_category_addition(self, mock_warn, mock_err, mock_info):
        settings_view = self.app.views["settings"]
        initial_count = len(get_categories())
        
        unique_name = f"Test Category {time.time_ns()}"
        settings_view.cat_name_entry.delete(0, 'end')
        settings_view.cat_name_entry.insert(0, unique_name)
        settings_view.cat_color_entry.delete(0, 'end')
        settings_view.cat_color_entry.insert(0, "#3388FF")
        settings_view.save_category()
        
        new_count = len(get_categories())
        self.assertEqual(new_count, initial_count + 1)

if __name__ == "__main__":
    unittest.main()
