import unittest
from db.database import init_db
from ui.app import ExpenseTrackerApp

class TestGUIShell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.app = ExpenseTrackerApp()

    def tearDown(self):
        self.app.destroy()

    def test_window_properties(self):
        self.assertEqual(self.app.title(), "Expense Tracker Desktop")

    def test_view_switching(self):
        # Check initial view is dashboard
        self.assertIn("dashboard", self.app.views)
        self.assertEqual(self.app.active_view_key, "dashboard")

        # Test switching to all views
        for view_key in ["dashboard", "add_expense", "reports", "settings"]:
            self.app.show_view(view_key)
            self.assertEqual(self.app.active_view_key, view_key)

    def test_theme_toggle(self):
        initial_theme = self.app.style.theme.name
        self.app.toggle_theme()
        new_theme = self.app.style.theme.name
        self.assertNotEqual(initial_theme, new_theme)

if __name__ == "__main__":
    unittest.main()
