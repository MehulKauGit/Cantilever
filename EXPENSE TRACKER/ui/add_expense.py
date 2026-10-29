import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import date

from db.queries import get_categories, add_expense, update_expense, get_expense_by_id
from utils.validators import validate_amount, validate_date, validate_description, validate_category_exists
from db.database import get_connection

class AddExpenseView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.editing_expense_id = None
        self.category_map = {}  # name -> category_id

        # Header Title
        self.title_lbl = ttk.Label(self, text="Add New Expense", font=("Segoe UI", 20, "bold"), bootstyle="primary")
        self.title_lbl.pack(anchor="w", pady=(0, 20))

        # Status / Feedback Message Label
        self.status_lbl = ttk.Label(self, text="", font=("Segoe UI", 12, "bold"))
        self.status_lbl.pack(anchor="w", pady=(0, 10))

        # Form Container Frame
        form_frame = ttk.Labelframe(self, text="Expense Details", padding=25)
        form_frame.pack(fill="x", anchor="n")

        # Amount Field
        self.amount_lbl = ttk.Label(form_frame, text="Amount ($): *", font=("Segoe UI", 12, "bold"))
        self.amount_lbl.grid(row=0, column=0, sticky="w", pady=12, padx=10)
        self.amount_entry = ttk.Entry(form_frame, width=32, font=("Segoe UI", 12))
        self.amount_entry.grid(row=0, column=1, sticky="w", pady=12, padx=10)

        # Category Field
        ttk.Label(form_frame, text="Category: *", font=("Segoe UI", 12, "bold")).grid(row=1, column=0, sticky="w", pady=12, padx=10)
        self.category_cb = ttk.Combobox(form_frame, width=30, state="readonly", font=("Segoe UI", 12))
        self.category_cb.grid(row=1, column=1, sticky="w", pady=12, padx=10)

        # Date Field
        ttk.Label(form_frame, text="Date (YYYY-MM-DD): *", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", pady=12, padx=10)
        self.date_entry = ttk.Entry(form_frame, width=32, font=("Segoe UI", 12))
        self.date_entry.grid(row=2, column=1, sticky="w", pady=12, padx=10)

        # Description Field
        ttk.Label(form_frame, text="Description:", font=("Segoe UI", 12, "bold")).grid(row=3, column=0, sticky="nw", pady=12, padx=10)
        self.desc_entry = ttk.Entry(form_frame, width=32, font=("Segoe UI", 12))
        self.desc_entry.grid(row=3, column=1, sticky="w", pady=12, padx=10)

        # Action Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=1, sticky="e", pady=25)

        self.save_btn = ttk.Button(btn_frame, text="💾 Save Expense", bootstyle="success", command=self.save_expense)
        self.save_btn.pack(side="left", padx=8)

        self.cancel_btn = ttk.Button(btn_frame, text="🔄 Clear / Reset", bootstyle="secondary", command=self.reset_form)
        self.cancel_btn.pack(side="left", padx=8)

        # Initial populate
        self.load_categories()
        self.reset_form()

    def load_categories(self):
        """Fetch categories from DB and update combobox options."""
        categories = get_categories()
        self.category_map = {cat.name: cat.id for cat in categories}
        cat_names = list(self.category_map.keys())
        self.category_cb["values"] = cat_names
        if cat_names:
            self.category_cb.set(cat_names[0])

    def refresh(self):
        """Refresh dynamic currency label and category dropdown."""
        sym = self.controller.get_currency_symbol() if hasattr(self.controller, "get_currency_symbol") else "$"
        self.amount_lbl.configure(text=f"Amount ({sym}): *")
        self.load_categories()

    def set_edit_mode(self, expense_id: int):
        """Pre-fill form for editing an existing expense."""
        expense = get_expense_by_id(expense_id)
        if not expense:
            messagebox.showerror("Error", "Expense record not found.")
            return

        self.editing_expense_id = expense_id
        self.title_lbl.configure(text=f"Edit Expense (ID #{expense_id})")
        self.save_btn.configure(text="💾 Update Expense")

        self.amount_entry.delete(0, 'end')
        self.amount_entry.insert(0, str(expense.amount))

        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, expense.date)

        self.desc_entry.delete(0, 'end')
        self.desc_entry.insert(0, expense.description or "")

        # Select category
        self.load_categories()
        if expense.category_name in self.category_map:
            self.category_cb.set(expense.category_name)

        self.status_lbl.configure(text="", bootstyle="default")

    def save_expense(self):
        """Validate inputs and save to SQLite DB."""
        amount_str = self.amount_entry.get().strip()
        category_name = self.category_cb.get().strip()
        date_str = self.date_entry.get().strip()
        description = self.desc_entry.get().strip()

        # Validations
        is_valid_amt, amount, amt_err = validate_amount(amount_str)
        if not is_valid_amt:
            self.status_lbl.configure(text=f"❌ {amt_err}", bootstyle="danger")
            return

        is_valid_dt, dt_err = validate_date(date_str)
        if not is_valid_dt:
            self.status_lbl.configure(text=f"❌ {dt_err}", bootstyle="danger")
            return

        is_valid_desc, desc_err = validate_description(description)
        if not is_valid_desc:
            self.status_lbl.configure(text=f"❌ {desc_err}", bootstyle="danger")
            return

        category_id = self.category_map.get(category_name)
        conn = get_connection()
        is_valid_cat, cat_err = validate_category_exists(category_id, conn)
        conn.close()
        if not is_valid_cat:
            self.status_lbl.configure(text=f"❌ {cat_err}", bootstyle="danger")
            return

        # Perform Insert or Update
        if self.editing_expense_id:
            updated = update_expense(
                expense_id=self.editing_expense_id,
                amount=amount,
                description=description,
                category_id=category_id,
                date_str=date_str
            )
            if updated:
                self.status_lbl.configure(text="✅ Expense updated successfully!", bootstyle="success")
                messagebox.showinfo("Success", "Expense updated successfully!")
            else:
                self.status_lbl.configure(text="❌ Failed to update expense.", bootstyle="danger")
                return
        else:
            exp_id = add_expense(
                amount=amount,
                description=description,
                category_id=category_id,
                date_str=date_str
            )
            if exp_id:
                self.status_lbl.configure(text="✅ Expense added successfully!", bootstyle="success")
                messagebox.showinfo("Success", "Expense recorded successfully!")

        # Reset & Refresh application views
        self.reset_form()
        self.controller.refresh_all_views()
        self.controller.show_view("dashboard")

    def reset_form(self):
        """Reset form to default Add mode."""
        self.editing_expense_id = None
        self.title_lbl.configure(text="Add New Expense")
        self.save_btn.configure(text="💾 Save Expense")

        self.amount_entry.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.desc_entry.delete(0, 'end')

        self.refresh()
        self.status_lbl.configure(text="", bootstyle="default")
