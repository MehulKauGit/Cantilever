import unittest
import os
import tempfile
from unittest.mock import patch
from db.database import init_db
from models.expense import Expense
from utils.exporters import export_expenses_to_csv
from ui.app import ExpenseTrackerApp

class TestPhase5Reports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.app = ExpenseTrackerApp()

    def tearDown(self):
        self.app.destroy()

    def test_csv_exporter(self):
        # Create dummy expense objects
        sample_expenses = [
            Expense(id=1, amount=15.50, description="Coffee", category_id=1, date="2026-08-10", category_name="Food & Dining"),
            Expense(id=2, amount=45.00, description="Gas", category_id=2, date="2026-08-11", category_name="Transportation")
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            success = export_expenses_to_csv(sample_expenses, tmp_path)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(tmp_path))

            # Read back file content
            with open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Coffee", content)
                self.assertIn("15.50", content)
                self.assertIn("Gas", content)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("tkinter.messagebox.showinfo")
    def test_reports_rendering(self, mock_info, mock_dialog):
        reports_view = self.app.views["reports"]
        
        # Test Donut chart rendering
        reports_view.chart_type_cb.set("Category Breakdown (Donut)")
        reports_view.render_report()
        self.assertIsNotNone(reports_view.figure)

        # Test Bar chart rendering
        reports_view.chart_type_cb.set("Monthly Spending Trend (Bar)")
        reports_view.render_report()
        self.assertIsNotNone(reports_view.figure)

if __name__ == "__main__":
    unittest.main()
