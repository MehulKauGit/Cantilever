import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime

from db.queries import get_all_expenses, get_categories, delete_expense, get_monthly_summary, get_category_budget_analysis
from utils.formatters import format_currency, format_date_display

class DashboardView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.category_filter_map = {}  # name -> category_id

        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 15))

        header_lbl = ttk.Label(header_frame, text="Dashboard & Expense History", font=("Segoe UI", 20, "bold"), bootstyle="primary")
        header_lbl.pack(side="left")

        add_btn = ttk.Button(header_frame, text="➕ Add New Expense", bootstyle="success", command=lambda: controller.show_view("add_expense"))
        add_btn.pack(side="right")

        # Metric Cards Container Frame
        self.cards_frame = ttk.Frame(self)
        self.cards_frame.pack(fill="x", pady=10)

        # Card 1: Total Spent (This Month)
        c1 = ttk.Labelframe(self.cards_frame, text="Total Spent (This Month)", padding=12, bootstyle="info")
        c1.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.lbl_total_month = ttk.Label(c1, text="$0.00", font=("Segoe UI", 18, "bold"), bootstyle="info")
        self.lbl_total_month.pack()

        # Card 2: Total Transactions
        c2 = ttk.Labelframe(self.cards_frame, text="Total Transactions", padding=12, bootstyle="success")
        c2.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.lbl_total_tx = ttk.Label(c2, text="0", font=("Segoe UI", 18, "bold"), bootstyle="success")
        self.lbl_total_tx.pack()

        # Card 3: Top Category
        c3 = ttk.Labelframe(self.cards_frame, text="Top Category", padding=12, bootstyle="warning")
        c3.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.lbl_top_cat = ttk.Label(c3, text="N/A", font=("Segoe UI", 18, "bold"), bootstyle="warning")
        self.lbl_top_cat.pack()

        # Card 4: Budget Utilization
        c4 = ttk.Labelframe(self.cards_frame, text="Budget Utilization", padding=12, bootstyle="danger")
        c4.pack(side="left", fill="both", expand=True)
        self.lbl_budget_util = ttk.Label(c4, text="0%", font=("Segoe UI", 18, "bold"), bootstyle="danger")
        self.lbl_budget_util.pack()

        # Filter & Search Bar
        filter_frame = ttk.Labelframe(self, text="Filter & Search Expenses", padding=12)
        filter_frame.pack(fill="x", pady=10)

        ttk.Label(filter_frame, text="Category:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(5, 5))
        self.category_cb = ttk.Combobox(filter_frame, state="readonly", width=20, font=("Segoe UI", 11))
        self.category_cb.pack(side="left", padx=(0, 15))
        self.category_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(filter_frame, text="Search (Desc/Category):", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(5, 5))
        self.search_entry = ttk.Entry(filter_frame, width=25, font=("Segoe UI", 11))
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        clear_filter_btn = ttk.Button(filter_frame, text="Reset Filters", bootstyle="outline-secondary", command=self.reset_filters)
        clear_filter_btn.pack(side="right", padx=5)

        # Table & Action Toolbar Frame
        table_container = ttk.Labelframe(self, text="Expense Records", padding=12)
        table_container.pack(fill="both", expand=True, pady=10)

        # Toolbar
        toolbar = ttk.Frame(table_container)
        toolbar.pack(fill="x", pady=(0, 10))

        edit_btn = ttk.Button(toolbar, text="✏️ Edit Selected", bootstyle="outline-primary", command=self.edit_selected_expense)
        edit_btn.pack(side="left", padx=5)

        delete_btn = ttk.Button(toolbar, text="🗑️ Delete Selected", bootstyle="outline-danger", command=self.delete_selected_expense)
        delete_btn.pack(side="left", padx=5)

        # Treeview Table
        self.sym = self.controller.get_currency_symbol() if hasattr(self.controller, "get_currency_symbol") else "$"
        columns = ("id", "date", "category", "description", "amount")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=10, selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.heading("amount", text=f"Amount ({self.sym})")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("category", width=160, anchor="w")
        self.tree.column("description", width=360, anchor="w")
        self.tree.column("amount", width=130, anchor="e")

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Double click to edit shortcut
        self.tree.bind("<Double-1>", lambda e: self.edit_selected_expense())

        # Load data initially
        self.load_category_filter_options()
        self.refresh()

    def load_category_filter_options(self):
        """Populate category filter dropdown."""
        categories = get_categories()
        self.category_filter_map = {"All Categories": None}
        for cat in categories:
            self.category_filter_map[cat.name] = cat.id

        options = list(self.category_filter_map.keys())
        self.category_cb["values"] = options
        self.category_cb.set("All Categories")

    def reset_filters(self):
        """Reset search and category filter controls."""
        self.category_cb.set("All Categories")
        self.search_entry.delete(0, 'end')
        self.apply_filters()

    def apply_filters(self):
        """Query DB with current search and category filters."""
        selected_cat_name = self.category_cb.get()
        category_id = self.category_filter_map.get(selected_cat_name)
        search_text = self.search_entry.get().strip()

        filters = {}
        if category_id is not None:
            filters["category_id"] = category_id
        if search_text:
            filters["search"] = search_text

        self.populate_expenses_table(filters)

    def populate_expenses_table(self, filters=None):
        """Fetch expenses from DB and populate Treeview rows."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        sym = self.controller.get_currency_symbol() if hasattr(self.controller, "get_currency_symbol") else "$"
        self.tree.heading("amount", text=f"Amount ({sym})")

        expenses = get_all_expenses(filters=filters)
        for exp in expenses:
            self.tree.insert(
                "",
                "end",
                values=(
                    exp.id,
                    format_date_display(exp.date),
                    exp.category_name,
                    exp.description or "-",
                    f"{sym}{exp.amount:,.2f}"
                )
            )

        # Update metrics cards
        self.update_metrics_cards()

    def update_metrics_cards(self):
        """Calculate and render summary card metrics including budget utilization."""
        now = datetime.now()
        monthly_data = get_monthly_summary(now.year, now.month)
        sym = self.controller.get_currency_symbol() if hasattr(self.controller, "get_currency_symbol") else "$"

        total_monthly = sum(item["total"] for item in monthly_data)
        self.lbl_total_month.configure(text=f"{sym}{total_monthly:,.2f}")

        all_expenses = get_all_expenses()
        self.lbl_total_tx.configure(text=str(len(all_expenses)))

        if monthly_data:
            top_cat = monthly_data[0]["category"]
            self.lbl_top_cat.configure(text=top_cat)
        else:
            self.lbl_top_cat.configure(text="N/A")

        # Calculate total monthly budget vs spending
        budget_analysis = get_category_budget_analysis(now.year, now.month)
        total_budget = sum(item["budget"] for item in budget_analysis)
        if total_budget > 0:
            pct_used = (total_monthly / total_budget) * 100
            self.lbl_budget_util.configure(text=f"{pct_used:.1f}% ({sym}{total_monthly:,.0f}/{sym}{total_budget:,.0f})")
            if pct_used > 100:
                self.lbl_budget_util.configure(bootstyle="danger")
            elif pct_used > 80:
                self.lbl_budget_util.configure(bootstyle="warning")
            else:
                self.lbl_budget_util.configure(bootstyle="success")
        else:
            self.lbl_budget_util.configure(text="No Budget Set", font=("Segoe UI", 13, "bold"), bootstyle="secondary")

    def edit_selected_expense(self):
        """Switch to Add/Edit view for selected row."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an expense row to edit.")
            return

        item = self.tree.item(selected[0])
        expense_id = item["values"][0]

        # Call controller method to switch to add_expense in Edit mode
        self.controller.views["add_expense"].set_edit_mode(expense_id)
        self.controller.show_view("add_expense")

    def delete_selected_expense(self):
        """Delete selected expense with confirmation."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an expense row to delete.")
            return

        item = self.tree.item(selected[0])
        expense_id = item["values"][0]
        desc = item["values"][3]
        amt = item["values"][4]

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete Expense #{expense_id} ({desc} - {amt})?"
        )
        if confirm:
            deleted = delete_expense(expense_id)
            if deleted:
                messagebox.showinfo("Deleted", f"Expense #{expense_id} deleted successfully.")
                self.controller.refresh_all_views()
            else:
                messagebox.showerror("Error", "Failed to delete expense record.")

    def refresh(self):
        """Refresh categories and table data."""
        self.load_category_filter_options()
        self.apply_filters()
