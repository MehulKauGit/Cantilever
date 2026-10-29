import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from datetime import datetime, date, timedelta

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from db.queries import get_all_expenses, get_monthly_summary, get_spending_trend
from utils.exporters import export_expenses_to_csv

class ReportsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.figure = None
        self.canvas = None

        # Header Title
        header_lbl = ttk.Label(self, text="Reports & Visualizations", font=("Segoe UI", 20, "bold"), bootstyle="primary")
        header_lbl.pack(anchor="w", pady=(0, 15))

        # Controls & Toolbar Frame
        controls_frame = ttk.Labelframe(self, text="Report Controls & Export", padding=15)
        controls_frame.pack(fill="x", pady=(0, 15))

        # Period Selector
        ttk.Label(controls_frame, text="Time Period:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(5, 5))
        self.period_cb = ttk.Combobox(
            controls_frame,
            values=["This Month", "Last 3 Months", "Last 6 Months", "This Year", "All Time"],
            state="readonly",
            width=15,
            font=("Segoe UI", 11)
        )
        self.period_cb.set("This Month")
        self.period_cb.pack(side="left", padx=(0, 15))
        self.period_cb.bind("<<ComboboxSelected>>", lambda e: self.render_report())

        # Chart Type Selector
        ttk.Label(controls_frame, text="Chart View:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(5, 5))
        self.chart_type_cb = ttk.Combobox(
            controls_frame,
            values=["Category Breakdown (Donut)", "Monthly Spending Trend (Bar)"],
            state="readonly",
            width=25,
            font=("Segoe UI", 11)
        )
        self.chart_type_cb.set("Category Breakdown (Donut)")
        self.chart_type_cb.pack(side="left", padx=(0, 15))
        self.chart_type_cb.bind("<<ComboboxSelected>>", lambda e: self.render_report())

        # Export Buttons
        export_csv_btn = ttk.Button(controls_frame, text="📥 Export CSV", bootstyle="outline-success", command=self.export_csv)
        export_csv_btn.pack(side="right", padx=5)

        export_img_btn = ttk.Button(controls_frame, text="🖼️ Save Chart PNG", bootstyle="outline-info", command=self.export_chart_png)
        export_img_btn.pack(side="right", padx=5)

        # Matplotlib Chart Container Frame
        self.chart_container = ttk.Labelframe(self, text="Visual Analytics", padding=15)
        self.chart_container.pack(fill="both", expand=True)

        self.render_report()

    def _get_date_range(self):
        """Calculate start and end date based on period selection."""
        today = date.today()
        period = self.period_cb.get()

        if period == "This Month":
            start = date(today.year, today.month, 1)
            return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif period == "Last 3 Months":
            start = today - timedelta(days=90)
            return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif period == "Last 6 Months":
            start = today - timedelta(days=180)
            return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif period == "This Year":
            start = date(today.year, 1, 1)
            return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        else:  # All Time
            return None, None

    def render_report(self):
        """Render Matplotlib chart inside canvas container."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        chart_type = self.chart_type_cb.get()
        start_dt, end_dt = self._get_date_range()
        sym = self.controller.get_currency_symbol() if hasattr(self.controller, "get_currency_symbol") else "$"

        # Create Matplotlib Figure
        self.figure = Figure(figsize=(7, 4.5), dpi=100)
        ax = self.figure.add_subplot(111)

        # Background color adaptation
        current_theme = self.controller.style.theme.name if hasattr(self.controller, "style") else "cosmo"
        is_dark = current_theme in ["superhero", "darkly", "cyborg", "solar"]

        bg_color = "#2b3e50" if is_dark else "#ffffff"
        text_color = "#ffffff" if is_dark else "#222222"

        self.figure.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        if "Donut" in chart_type:
            filters = {}
            if start_dt and end_dt:
                filters["start_date"] = start_dt
                filters["end_date"] = end_dt
            
            expenses = get_all_expenses(filters=filters)
            if not expenses:
                ax.text(0.5, 0.5, "No expense data found for selected period.", horizontalalignment='center', verticalalignment='center', color=text_color, fontsize=12)
                ax.axis('off')
            else:
                cat_totals = {}
                cat_colors = {}
                for exp in expenses:
                    cname = exp.category_name or "Uncategorized"
                    cat_totals[cname] = cat_totals.get(cname, 0.0) + exp.amount
                    cat_colors[cname] = exp.category_color or "#888888"

                labels = list(cat_totals.keys())
                sizes = list(cat_totals.values())
                colors = [cat_colors[lbl] for lbl in labels]

                wedges, texts, autotexts = ax.pie(
                    sizes,
                    labels=labels,
                    autopct='%1.1f%%',
                    startangle=140,
                    colors=colors,
                    pctdistance=0.75,
                    textprops=dict(color=text_color, fontsize=10, weight='bold')
                )

                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_weight('bold')

                centre_circle = matplotlib.patches.Circle((0, 0), 0.50, fc=bg_color)
                ax.add_artist(centre_circle)
                ax.set_title(f"Spending Breakdown by Category ({sym})", color=text_color, fontsize=13, weight='bold', pad=15)
        else:
            months_count = 6
            if self.period_cb.get() == "This Year":
                months_count = 12
            elif self.period_cb.get() == "Last 3 Months":
                months_count = 3

            trend_data = get_spending_trend(months=months_count)
            if not trend_data:
                ax.text(0.5, 0.5, "No trend data available.", horizontalalignment='center', verticalalignment='center', color=text_color, fontsize=12)
                ax.axis('off')
            else:
                months = [item["month"] for item in trend_data]
                totals = [item["total"] for item in trend_data]

                bars = ax.bar(months, totals, color="#2196F3", edgecolor="#1976D2", width=0.5)
                ax.set_ylabel(f"Total Spent ({sym})", color=text_color, fontsize=11, weight='bold')
                ax.set_title(f"Monthly Spending Trend (Past {months_count} Months)", color=text_color, fontsize=13, weight='bold', pad=15)
                ax.tick_params(colors=text_color, labelsize=10)

                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{sym}{height:,.0f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', color=text_color, fontsize=9, weight='bold')

        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def export_csv(self):
        """Export expenses for selected period to a CSV file."""
        start_dt, end_dt = self._get_date_range()
        filters = {}
        if start_dt and end_dt:
            filters["start_date"] = start_dt
            filters["end_date"] = end_dt

        expenses = get_all_expenses(filters=filters)
        if not expenses:
            messagebox.showwarning("No Data", "No expense records found to export for the selected period.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Expenses CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if filepath:
            success = export_expenses_to_csv(expenses, filepath)
            if success:
                messagebox.showinfo("Export Successful", f"Exported {len(expenses)} records to:\n{filepath}")
            else:
                messagebox.showerror("Export Failed", "Could not write CSV file.")

    def export_chart_png(self):
        """Save the rendered Matplotlib figure as a PNG image file."""
        if not self.figure:
            messagebox.showwarning("No Chart", "No active chart figure to save.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Chart PNG",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")]
        )

        if filepath:
            try:
                self.figure.savefig(filepath, dpi=300, facecolor=self.figure.get_facecolor())
                messagebox.showinfo("Chart Saved", f"Chart image saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chart image: {str(e)}")

    def refresh(self):
        """Re-render chart on data changes."""
        self.render_report()
