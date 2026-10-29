import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ui.dashboard import DashboardView
from ui.add_expense import AddExpenseView
from ui.reports import ReportsView
from ui.settings import SettingsView
from utils.config import load_settings, save_settings, CURRENCY_OPTIONS

class ExpenseTrackerApp(ttk.Window):
    def __init__(self, theme_name: str = None):
        self.settings = load_settings()
        if theme_name is None:
            theme_name = self.settings.get("theme_name", "cosmo")

        super().__init__(
            title="Expense Tracker Desktop",
            themename=theme_name,
            size=(1180, 740),
            resizable=(True, True)
        )

        # Min size limit
        self.minsize(980, 640)

        # Apply global style enhancements for high text visibility
        self._configure_styles()

        # Main Layout: Top Header + Body (Sidebar + Content)
        self._create_header()
        self._create_body()

        # Dictionary of Views
        self.views = {}
        self._init_views()

        # Active view tracker
        self.active_view_key = None

        # Show initial view
        self.show_view("dashboard")

    def get_currency_symbol(self) -> str:
        return self.settings.get("currency_symbol", "$")

    def _configure_styles(self):
        """Configure font sizes and element height for high text visibility."""
        style = self.style
        
        # Configure Treeview table fonts and row height
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=32)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        # Configure LabelFrame font
        style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("TEntry", font=("Segoe UI", 11))
        style.configure("TCombobox", font=("Segoe UI", 11))

    def _create_header(self):
        header_frame = ttk.Frame(self, bootstyle="primary", padding=15)
        header_frame.pack(fill="x", side="top")

        title_lbl = ttk.Label(
            header_frame,
            text="🏦 Expense Tracker",
            font=("Segoe UI", 18, "bold"),
            bootstyle="inverse-primary"
        )
        title_lbl.pack(side="left", padx=10)

        # Controls Container on Right
        controls_hdr = ttk.Frame(header_frame, bootstyle="primary")
        controls_hdr.pack(side="right", padx=10)

        # Currency Selector
        ttk.Label(
            controls_hdr,
            text="Currency:",
            font=("Segoe UI", 11, "bold"),
            bootstyle="inverse-primary"
        ).pack(side="left", padx=(0, 6))

        curr_names = list(CURRENCY_OPTIONS.keys())
        current_curr_name = self.settings.get("currency_name", "USD ($)")

        self.currency_cb = ttk.Combobox(
            controls_hdr,
            values=curr_names,
            state="readonly",
            width=10,
            font=("Segoe UI", 10, "bold")
        )
        self.currency_cb.set(current_curr_name)
        self.currency_cb.pack(side="left", padx=(0, 15))
        self.currency_cb.bind("<<ComboboxSelected>>", self._on_currency_changed)

        # Theme toggle button
        theme_btn = ttk.Button(
            controls_hdr,
            text="🌓 Toggle Theme",
            bootstyle="outline-light",
            command=self.toggle_theme
        )
        theme_btn.pack(side="left", padx=5)

    def _on_currency_changed(self, event=None):
        """Update selected currency symbol and refresh all views."""
        selected_name = self.currency_cb.get()
        symbol = CURRENCY_OPTIONS.get(selected_name, "$")
        
        self.settings["currency_name"] = selected_name
        self.settings["currency_symbol"] = symbol
        save_settings(self.settings)

        self.refresh_all_views()

    def _create_body(self):
        body_frame = ttk.Frame(self)
        body_frame.pack(fill="both", expand=True)

        # Sidebar navigation frame
        self.sidebar = ttk.Frame(body_frame, bootstyle="secondary", padding=15, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Navigation Label
        ttk.Label(
            self.sidebar,
            text="NAVIGATION",
            font=("Segoe UI", 11, "bold"),
            bootstyle="inverse-secondary"
        ).pack(anchor="w", pady=(0, 15))

        # Nav Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("add_expense", "➕  Add Expense"),
            ("reports", "📈  Reports"),
            ("settings", "⚙️  Settings")
        ]

        for view_key, label_text in nav_items:
            btn = ttk.Button(
                self.sidebar,
                text=label_text,
                bootstyle="light-outline",
                command=lambda vk=view_key: self.show_view(vk)
            )
            btn.pack(fill="x", pady=6)
            self.nav_buttons[view_key] = btn

        # Main Content Container Frame
        self.content_container = ttk.Frame(body_frame, padding=25)
        self.content_container.pack(side="right", fill="both", expand=True)

    def _init_views(self):
        # Instantiate each view frame inside content container
        for ViewClass, key in [
            (DashboardView, "dashboard"),
            (AddExpenseView, "add_expense"),
            (ReportsView, "reports"),
            (SettingsView, "settings")
        ]:
            view_instance = ViewClass(self.content_container, self)
            self.views[key] = view_instance
            view_instance.grid(row=0, column=0, sticky="nsew")

        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

    def show_view(self, view_key: str):
        """Switch active view frame and highlight sidebar navigation button."""
        if view_key in self.views:
            # Raise selected view
            view = self.views[view_key]
            if hasattr(view, "refresh"):
                view.refresh()
            view.tkraise()
            self.active_view_key = view_key

            # Update button styles
            for vk, btn in self.nav_buttons.items():
                if vk == view_key:
                    btn.configure(bootstyle="primary")
                else:
                    btn.configure(bootstyle="light-outline")

    def refresh_all_views(self):
        """Trigger data refresh across all child views."""
        for view_key, view_instance in self.views.items():
            if hasattr(view_instance, "refresh"):
                view_instance.refresh()
            elif hasattr(view_instance, "load_categories"):
                view_instance.load_categories()

    def toggle_theme(self):
        """Toggle between light and dark theme with contrast adjustment."""
        current_theme = self.style.theme.name
        new_theme = "superhero" if current_theme in ["cosmo", "flatly", "journal", "litera"] else "cosmo"
        self.style.theme_use(new_theme)
        
        self.settings["theme_name"] = new_theme
        save_settings(self.settings)

        self._configure_styles()
        self.refresh_all_views()

if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()
