import unittest
import os
import tempfile
from db.database import init_db
from db.queries import (
    add_category, get_categories, update_category,
    get_category_budget_analysis, add_expense
)
from utils.backup import backup_database, restore_database

class TestPhase6Advanced(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        init_db(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_category_budget_crud_and_analysis(self):
        cat_id = add_category("Entertainment Pass", "#880088", budget=300.0, db_path=self.db_path)
        self.assertIsNotNone(cat_id)

        # Verify budget was stored
        cats = get_categories(self.db_path)
        target = next((c for c in cats if c.id == cat_id), None)
        self.assertIsNotNone(target)
        self.assertEqual(target.budget, 300.0)

        # Update budget
        updated = update_category(cat_id, budget=450.0, db_path=self.db_path)
        self.assertTrue(updated)

        # Add expense under category
        add_expense(150.0, "Concert Ticket", cat_id, "2026-08-12", self.db_path)

        # Analyze budget
        analysis = get_category_budget_analysis(2026, 8, self.db_path)
        target_analysis = next((item for item in analysis if item['id'] == cat_id), None)
        self.assertIsNotNone(target_analysis)
        self.assertEqual(target_analysis['spent'], 150.0)
        self.assertEqual(target_analysis['remaining'], 300.0)
        self.assertEqual(target_analysis['percent_used'], 33.3)

    def test_database_backup_and_restore(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as backup_tmp:
            backup_path = backup_tmp.name

        try:
            # Backup
            backed_up = backup_database(backup_path, source_path=self.db_path)
            self.assertTrue(backed_up)
            self.assertTrue(os.path.exists(backup_path))

            # Restore
            restored = restore_database(backup_path, target_path=self.db_path)
            self.assertTrue(restored)
        finally:
            if os.path.exists(backup_path):
                os.remove(backup_path)

if __name__ == "__main__":
    unittest.main()
