# CantiLever Python Programming Virtual Internship

## Executive Summary

The primary objective of this internship program was to build robust, maintainable, and user-centric desktop software applications using core Python libraries, graphical user interface (GUI) frameworks, embedded relational database engines, and data visualization tools. 

To satisfy the requirements of the CantiLever Python Programming curriculum, two comprehensive financial management systems were engineered:

1. **Expense Tracker**: A desktop expense management system featuring localized SQLite storage, category budget tracking, dynamic currency formatting, embedded Matplotlib analytics, and database backup capabilities.
2. **Personal Finance System**: An advanced financial dashboard built with CustomTkinter for comprehensive personal asset, income, and expense management.

---

## Portfolio Projects

### 1. Expense Tracker (`/EXPENSE TRACKER`)

The Expense Tracker application provides users with an intuitive interface for recording daily financial transactions, managing category budgets, analyzing spending distributions, and exporting financial statements.

#### Key Engineering Capabilities
* **Data Access & Schema Persistence**: Powered by SQLite3 with foreign key enforcement and automated schema migrations for category budget allocations.
* **Input Validation & Integrity**: Comprehensive input validation logic enforcing date formats (`YYYY-MM-DD`), numeric bounds, and relational entity existence.
* **Embedded Analytics**: Embedded Matplotlib figures (`FigureCanvasTkAgg`) rendering donut chart category breakdowns and historical monthly trend bar charts.
* **Data Portability & Security**: Integrated utilities for exporting transaction records to CSV, saving chart visualizations as high-resolution PNG images, and performing full database backup and restoration (`.db`).
* **UI/UX & Localization**: Built using `ttkbootstrap` with dual light/dark theme support and a real-time multi-currency converter supporting USD, EUR, GBP, INR, JPY, CAD, AUD, and BRL.

---

### 2. Personal Finance System (`/Personal Finance System`)

The Personal Finance System is an expanded desktop platform designed for broader personal financial tracking, asset portfolio overview, and structured report generation.

#### Key Engineering Capabilities
* **CustomTkinter GUI Engine**: Modernized high-DPI desktop layout utilizing CustomTkinter components.
* **Modular Project Architecture**: Separated into decoupled data access layers, service controllers, view components, and unit test suites.
* **Automated Packaging**: Configured with PyInstaller specification files (`.spec`) for building standalone executable binaries.
* **Automated Testing**: Integrated `pytest` test suite ensuring core financial calculations remain consistent across updates.

---

## Repository Structure

```
CantiLever/
├── EXPENSE TRACKER/                   # Expense Tracker Application
│   ├── .venv/                         # Isolated Virtual Environment
│   ├── assets/                        # Application Screenshot Artifacts
│   ├── db/                            # SQLite Connection & CRUD Query Engine
│   ├── models/                        # Dataclass Business Models (Category, Expense)
│   ├── ui/                            # View Frames (Dashboard, AddExpense, Reports, Settings)
│   ├── utils/                         # Validators, Formatters, Exporters & Backup Helpers
│   ├── tests/                         # Automated Unit Test Suite (14 Test Cases)
│   ├── main.py                        # Application Entry Point
│   ├── requirements.txt               # Dependency Requirements
│   ├── user_settings.json             # Persisted User Configuration (Currency & Theme)
│   └── readme.md                      # Detailed Project Documentation
│
├── Personal Finance System/           # Personal Finance System Application
│   ├── .venv/                         # Isolated Virtual Environment
│   ├── src/                           # Source Code Architecture (GUI, Database, Services)
│   ├── tests/                         # Pytest Automated Test Suite
│   ├── build.bat                      # Executable Build Automation Script
│   ├── requirements.txt               # Dependency Requirements
│   └── readme.md                      # Detailed Project Documentation
│
└── README.md                          # Root Internship Repository Documentation
```

---

## Environment Setup and Execution

Each project maintains its own isolated virtual environment (`.venv`) to ensure dependency separation and clean execution.

### Prerequisites
* **Python 3.9** or higher installed.
* PowerShell or Command Prompt (Windows) / Terminal (Linux/macOS).

---

### Running the Expense Tracker

1. Navigate to the Expense Tracker directory:
   ```powershell
   cd "EXPENSE TRACKER"
   ```

2. Activate the dedicated virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install requirements (if not already installed):
   ```powershell
   pip install -r requirements.txt
   ```

4. Launch the application:
   ```powershell
   python main.py
   ```

5. Run the test suite:
   ```powershell
   python -m unittest discover -s tests
   ```

---

### Running the Personal Finance System

1. Navigate to the Personal Finance System directory:
   ```powershell
   cd "Personal Finance System"
   ```

2. Activate the dedicated virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install requirements (if not already installed):
   ```powershell
   pip install -r requirements.txt
   ```

4. Launch the application:
   ```powershell
   python src/main.py
   ```

5. Run the test suite:
   ```powershell
   pytest
   ```

---

## Verification and Quality Assurance

Both project implementations adhere to modern Python software engineering principles:
* **Separation of Concerns**: Business logic is isolated from UI presentation layers.
* **Automated Unit Testing**: Both projects feature automated test suites verifying data integrity, calculations, and GUI component routing.
* **Error Handling**: Graceful error recovery mechanisms prevent application crashes on invalid input or database errors.



