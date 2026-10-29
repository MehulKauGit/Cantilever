import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, colorchooser, filedialog
import os

from db.queries import get_categories, add_category, update_category, delete_category
from utils.backup import backup_database, restore_database
from utils.validators import validate_amount

class SettingsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_color = "#3388FF"
        self.editing_cat_id = None

        # Header
        header = ttk.Label(self, text="Category Management & Database Settings", font=("Segoe UI", 20, "bold"), bootstyle="primary")
        header.pack(anchor="w", pady=(0, 15))

        # Add / Edit Category Frame
        form_frame = ttk.Labelframe(self, text="Category & Budget Details", padding=15)
        form_frame.pack(fill="x", pady=10)

        # Name
        ttk.Label(form_frame, text="Category Name: *", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cat_name_entry = ttk.Entry(form_frame, width=22, font=("Segoe UI", 11))
        self.cat_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Monthly Budget
        self.budget_lbl = ttk.Label(form_frame, text="Monthly Budget ($):", font=("Segoe UI", 11, "bold"))
        self.budget_lbl.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        self.cat_budget_entry = ttk.Entry(form_frame, width=15, font=("Segoe UI", 11))
        self.cat_budget_entry.insert(0, "0.00")
        self.cat_budget_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Color
        ttk.Label(form_frame, text="Color Hex: *", font=("Segoe UI", 11, "bold")).grid(row=0, column=4, sticky="w", padx=10, pady=5)
        color_subframe = ttk.Frame(form_frame)
        color_subframe.grid(row=0, column=5, sticky="w", padx=5, pady=5)

        self.color_preview = ttk.Label(color_subframe, text="  ", width=4, background=self.selected_color, relief="solid")
        self.color_preview.pack(side="left", padx=(0, 5))

        self.cat_color_entry = ttk.Entry(color_subframe, width=10, font=("Segoe UI", 11))
        self.cat_color_entry.insert(0, self.selected_color)
        self.cat_color_entry.pack(side="left", padx=5)

        pick_color_btn = ttk.Button(color_subframe, text="🎨", bootstyle="outline-secondary", command=self.pick_color)
        pick_color_btn.pack(side="left", padx=2)

        self.save_cat_btn = ttk.Button(form_frame, text="💾 Save Category", bootstyle="success", command=self.save_category)
        self.save_cat_btn.grid(row=0, column=6, padx=15, pady=5)

        # Existing Categories Table
        table_frame = ttk.Labelframe(self, text="Configured Categories", padding=15)
        table_frame.pack(fill="both", expand=True, pady=10)

        toolbar = ttk.Frame(table_frame)
        toolbar.pack(fill="x", pady=(0, 10))

        edit_cat_btn = ttk.Button(toolbar, text="✏️ Edit Selected", bootstyle="outline-primary", command=self.edit_selected_category)
        edit_cat_btn.pack(side="left", padx=5)

        delete_cat_btn = ttk.Button(toolbar, text="🗑️ Delete Selected", bootstyle="outline-danger", command=self.delete_selected_category)
        delete_cat_btn.pack(side="left", padx=5)

        columns = ("id", "name", "color", "budget")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6, selectmode="browse")

        self.sym = self.controller.get_currency_symbol() if hasattr(self.controller, "get_currency_symbol") else "$"

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Category Name")
        self.tree.heading("color", text="Hex Color Code")
        self.tree.heading("budget", text=f"Monthly Budget ({self.sym})")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("color", width=150, anchor="center")
        self.tree.column("budget", width=150, anchor="e")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Database Backup & Restore Section Frame
        backup_frame = ttk.Labelframe(self, text="Database Backup & Recovery", padding=15)
        backup_frame.pack(fill="x", pady=10)

        ttk.Label(backup_frame, text="Safeguard your data by creating backups or restoring a previous database file:", font=("Segoe UI", 11)).pack(side="left", padx=5)

        restore_btn = ttk.Button(backup_frame, text="📥 Restore DB File", bootstyle="outline-warning", command=self.handle_restore)
        restore_btn.pack(side="right", padx=5)

        backup_btn = ttk.Button(backup_frame, text="📦 Backup DB File", bootstyle="outline-info", command=self.handle_backup)
        backup_btn.pack(side="right", padx=5)

        self.refresh()

    def pick_color(self):
        """Open native color chooser dialog."""
        color_tuple = colorchooser.askcolor(title="Choose Category Color", initialcolor=self.selected_color)
        if color_tuple and color_tuple[1]:
            self.selected_color = color_tuple[1]
            self.cat_color_entry.delete(0, 'end')
            self.cat_color_entry.insert(0, self.selected_color)
            self.color_preview.configure(background=self.selected_color)

    def edit_selected_category(self):
        """Pre-fill form to edit selected category."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a category row to edit.")
            return

        item = self.tree.item(selected[0])
        self.editing_cat_id = item["values"][0]
        name = item["values"][1]
        color = item["values"][2]
        sym = self.controller.get_currency_symbol() if hasattr(self.controller, "get_currency_symbol") else "$"
        budget_str = str(item["values"][3]).replace(sym, "").replace("$", "").replace(",", "")

        self.cat_name_entry.delete(0, 'end')
        self.cat_name_entry.insert(0, name)

        self.cat_color_entry.delete(0, 'end')
        self.cat_color_entry.insert(0, color)
        self.color_preview.configure(background=color)

        self.cat_budget_entry.delete(0, 'end')
        self.cat_budget_entry.insert(0, budget_str)

        self.save_cat_btn.configure(text="💾 Update Category")

    def save_category(self):
        """Validate and insert or update category in DB."""
        name = self.cat_name_entry.get().strip()
        color = self.cat_color_entry.get().strip()
        budget_str = self.cat_budget_entry.get().strip()

        if not name:
            messagebox.showwarning("Validation Error", "Category name cannot be empty.")
            return

        if not color.startswith("#") or len(color) not in [4, 7]:
            messagebox.showwarning("Validation Error", "Please provide a valid hex color code (e.g. #3388FF).")
            return

        try:
            budget = float(budget_str) if budget_str else 0.0
            if budget < 0:
                messagebox.showwarning("Validation Error", "Budget cannot be negative.")
                return
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid numeric budget amount.")
            return

        try:
            if self.editing_cat_id:
                updated = update_category(self.editing_cat_id, name=name, color=color, budget=budget)
                if updated:
                    messagebox.showinfo("Success", f"Category '{name}' updated successfully.")
            else:
                cat_id = add_category(name, color, budget)
                if cat_id:
                    messagebox.showinfo("Success", f"Category '{name}' created successfully.")

            self.reset_form()
            self.controller.refresh_all_views()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save category: {str(e)}")

    def delete_selected_category(self):
        """Delete selected category record."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a category row to delete.")
            return

        item = self.tree.item(selected[0])
        cat_id = item["values"][0]
        cat_name = item["values"][1]

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete category '{cat_name}'?\nExisting expenses in this category will become Uncategorized."
        )
        if confirm:
            deleted = delete_category(cat_id)
            if deleted:
                messagebox.showinfo("Deleted", f"Category '{cat_name}' deleted successfully.")
                self.reset_form()
                self.controller.refresh_all_views()
            else:
                messagebox.showerror("Error", "Failed to delete category.")

    def handle_backup(self):
        """Backup database file."""
        filepath = filedialog.asksaveasfilename(
            title="Backup Expense Tracker Database",
            defaultextension=".db",
            filetypes=[("SQLite DB Files", "*.db"), ("All Files", "*.*")]
        )
        if filepath:
            if backup_database(filepath):
                messagebox.showinfo("Backup Success", f"Database backed up successfully to:\n{filepath}")
            else:
                messagebox.showerror("Backup Failed", "Failed to backup database file.")

    def handle_restore(self):
        """Restore database file."""
        filepath = filedialog.askopenfilename(
            title="Select Database File to Restore",
            filetypes=[("SQLite DB Files", "*.db"), ("All Files", "*.*")]
        )
        if filepath:
            confirm = messagebox.askyesno(
                "Confirm Restore",
                "Restoring a database backup will replace your current data.\nDo you wish to proceed?"
            )
            if confirm:
                if restore_database(filepath):
                    messagebox.showinfo("Restore Success", "Database restored successfully!")
                    self.controller.refresh_all_views()
                else:
                    messagebox.showerror("Restore Failed", "Failed to restore database file.")

    def reset_form(self):
        self.editing_cat_id = None
        self.save_cat_btn.configure(text="💾 Save Category")
        self.cat_name_entry.delete(0, 'end')
        self.cat_budget_entry.delete(0, 'end')
        self.cat_budget_entry.insert(0, "0.00")

    def refresh(self):
        """Refresh categories table and dynamic currency symbol header."""
        sym = self.controller.get_currency_symbol() if hasattr(self.controller, "get_currency_symbol") else "$"
        self.budget_lbl.configure(text=f"Monthly Budget ({sym}):")
        self.tree.heading("budget", text=f"Monthly Budget ({sym})")

        for item in self.tree.get_children():
            self.tree.delete(item)

        categories = get_categories()
        for cat in categories:
            self.tree.insert("", "end", values=(cat.id, cat.name, cat.color, f"{sym}{cat.budget:,.2f}"))
