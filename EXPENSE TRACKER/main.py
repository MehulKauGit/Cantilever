import sys
from db.database import init_db
from ui.app import ExpenseTrackerApp

def main():
    # 1. Initialize SQLite Database Schema & Default Seed Data
    init_db()
    
    # 2. Launch Desktop GUI Application
    app = ExpenseTrackerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
