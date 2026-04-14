# Hussein
# All Tkinter screens in one file. Main window with navigation, transaction entry/edit/delete screen, budget dashboard, analytics dashboard, monthly report screen.

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database import initialize_database
from models import Transactions, Budget, Categories


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartBudget - AI Personal Finance Manager")
        self.root.geometry("1100x680")
        self.root.configure(bg="#1e1e2e")

        self._build_sidebar()
        self._build_content_area()
        self.show_screen("Transactions")

    def _build_sidebar(self):
        sidebar = tk.Frame(self.root, width=200, bg="#2c2f3f")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="💰 SmartBudget", bg="#2c2f3f", fg="#a9b1d6",
                 font=("Helvetica", 14, "bold"), pady=20).pack(fill="x")

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10)

        nav_items = [
            ("📋  Transactions", "Transactions"),
            ("📊  Budget",       "Budget"),
            ("📈  Analytics",    "Analytics"),
            ("📄  Monthly Report","Report"),
        ]
        for label, screen in nav_items:
            btn = tk.Button(sidebar, text=label, anchor="w", padx=16,
                            bg="#2c2f3f", fg="#c0caf5", activebackground="#3d4166",
                            activeforeground="white", relief="flat",
                            font=("Helvetica", 11), cursor="hand2",
                            command=lambda s=screen: self.show_screen(s))
            btn.pack(fill="x", pady=2)

    def _build_content_area(self):
        self.content = tk.Frame(self.root, bg="#1e1e2e")
        self.content.pack(side="right", fill="both", expand=True)

    def show_screen(self, screen_name):
        for w in self.content.winfo_children():
            w.destroy()
        screens = {
            "Transactions": TransactionScreen,
            "Budget":       BudgetScreen,
            "Analytics":    AnalyticsScreen,
            "Report":       ReportScreen,
        }
        if screen_name in screens:
            screens[screen_name](self.content).pack(fill="both", expand=True)


#  TRANSACTION SCREEN
class TransactionScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self.selected_id = None
        self.categories  = Categories.get_all_categories()
        self.cat_names   = [c.name for c in self.categories]
        self._build_form()
        self._build_table()
        self._load_transactions()

    def _build_form(self):
        form = tk.Frame(self, bg="#2c2f3f", pady=10)
        form.pack(fill="x", padx=20, pady=(20, 0))

        tk.Label(form, text="Transactions", bg="#2c2f3f", fg="#a9b1d6",
                 font=("Helvetica", 15, "bold")).grid(row=0, column=0, columnspan=6,
                 sticky="w", padx=10, pady=(0,10))

        labels = ["Date (YYYY-MM-DD)", "Amount ($)", "Type", "Category",
                  "Payment Method", "Description"]
        self.entries = {}

        for col, lbl in enumerate(labels):
            tk.Label(form, text=lbl, bg="#2c2f3f", fg="#7aa2f7",
                     font=("Helvetica", 9)).grid(row=1, column=col, padx=8, sticky="w")

        # Date
        self.entries["date"] = tk.Entry(form, width=14, bg="#3d4166", fg="white",
                                         insertbackground="white")
        self.entries["date"].insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.entries["date"].grid(row=2, column=0, padx=8, pady=4)

        # Amount
        self.entries["amount"] = tk.Entry(form, width=10, bg="#3d4166", fg="white",
                                           insertbackground="white")
        self.entries["amount"].grid(row=2, column=1, padx=8)

        # Type dropdown
        self.type_var = tk.StringVar(value="expense")
        ttk.Combobox(form, textvariable=self.type_var, values=["expense", "income"],
                     width=10, state="readonly").grid(row=2, column=2, padx=8)

        # Category dropdown
        self.cat_var = tk.StringVar(value=self.cat_names[0] if self.cat_names else "")
        ttk.Combobox(form, textvariable=self.cat_var, values=self.cat_names,
                     width=14, state="readonly").grid(row=2, column=3, padx=8)

        # Payment method
        self.pay_var = tk.StringVar(value="Cash")
        ttk.Combobox(form, textvariable=self.pay_var,
                     values=["Cash", "Credit Card", "Debit Card", "Bank Transfer"],
                     width=14, state="readonly").grid(row=2, column=4, padx=8)

        # Description
        self.entries["description"] = tk.Entry(form, width=20, bg="#3d4166", fg="white",
                                                insertbackground="white")
        self.entries["description"].grid(row=2, column=5, padx=8)

        # Buttons
        btn_frame = tk.Frame(form, bg="#2c2f3f")
        btn_frame.grid(row=3, column=0, columnspan=6, pady=10, sticky="w", padx=8)

        tk.Button(btn_frame, text="➕ Add", bg="#7aa2f7", fg="black", relief="flat",
                  font=("Helvetica", 10, "bold"), padx=12, command=self._add).pack(side="left", padx=4)
        tk.Button(btn_frame, text="✏️ Update", bg="#e0af68", fg="black", relief="flat",
                  font=("Helvetica", 10), padx=12, command=self._update).pack(side="left", padx=4)
        tk.Button(btn_frame, text="🗑️ Delete", bg="#f7768e", fg="black", relief="flat",
                  font=("Helvetica", 10), padx=12, command=self._delete).pack(side="left", padx=4)
        tk.Button(btn_frame, text="🔄 Clear", bg="#565f89", fg="white", relief="flat",
                  font=("Helvetica", 10), padx=12, command=self._clear).pack(side="left", padx=4)

    def _build_table(self):
        cols = ("ID", "Date", "Amount", "Type", "Category", "Payment", "Description")
        frame = tk.Frame(self, bg="#1e1e2e")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(frame, orient="vertical")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                  yscrollcommand=scrollbar.set, height=18)
        scrollbar.config(command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")

        widths = [40, 100, 80, 80, 110, 110, 200]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2c2f3f", foreground="#c0caf5",
                         rowheight=28, fieldbackground="#2c2f3f")
        style.configure("Treeview.Heading", background="#3d4166", foreground="#7aa2f7",
                         font=("Helvetica", 10, "bold"))

    def _load_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in Transactions.get_all_transactions():
            cat = Categories.get_by_category_id(t.category_id)
            cat_name = cat.name if cat else "—"
            self.tree.insert("", "end", iid=t.id,
                             values=(t.id, t.date, f"${t.amount:.2f}", t.type,
                                     cat_name, t.payment_method, t.description))

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]
        self.entries["date"].delete(0, "end");        self.entries["date"].insert(0, vals[1])
        self.entries["amount"].delete(0, "end");      self.entries["amount"].insert(0, str(vals[2]).replace("$",""))
        self.type_var.set(vals[3])
        self.cat_var.set(vals[4])
        self.pay_var.set(vals[5])
        self.entries["description"].delete(0, "end"); self.entries["description"].insert(0, vals[6])

    def _get_category_id(self):
        cat = Categories.get_by_name(self.cat_var.get())
        return cat.id if cat else None

    def _add(self):
        try:
            t = Transactions(None, float(self.entries["amount"].get()),
                             self.entries["date"].get(),
                             self.entries["description"].get(),
                             self._get_category_id(),
                             self.pay_var.get(), self.type_var.get())
            t.save()
            self._load_transactions()
            self._clear()
            messagebox.showinfo("Success", "Transaction added!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update(self):
        if not self.selected_id:
            messagebox.showwarning("Select a row", "Click a transaction to edit first.")
            return
        try:
            t = Transactions(self.selected_id, float(self.entries["amount"].get()),
                             self.entries["date"].get(),
                             self.entries["description"].get(),
                             self._get_category_id(),
                             self.pay_var.get(), self.type_var.get())
            t.save()
            self._load_transactions()
            self._clear()
            messagebox.showinfo("Updated", "Transaction updated!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete(self):
        if not self.selected_id:
            messagebox.showwarning("Select a row", "Click a transaction to delete first.")
            return
        if messagebox.askyesno("Confirm", "Delete this transaction?"):
            t = Transactions(self.selected_id, 0, "", "", None, "", "")
            t.delete()
            self._load_transactions()
            self._clear()

    def _clear(self):
        self.selected_id = None
        self.entries["amount"].delete(0, "end")
        self.entries["description"].delete(0, "end")
        self.entries["date"].delete(0, "end")
        self.entries["date"].insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.type_var.set("expense")
        self.pay_var.set("Cash")


#  BUDGET SCREEN
class BudgetScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Budget Dashboard", bg="#1e1e2e", fg="#a9b1d6",
                 font=("Helvetica", 16, "bold")).pack(pady=(20, 5), anchor="w", padx=30)

        form = tk.Frame(self, bg="#2c2f3f", pady=10)
        form.pack(fill="x", padx=30, pady=(0, 10))

        self.categories = Categories.get_all_categories()
        self.cat_names = [c.name for c in self.categories]

        tk.Label(form, text="Category", bg="#2c2f3f", fg="#7aa2f7",
                 font=("Helvetica", 9)).grid(row=0, column=0, padx=8, sticky="w")
        tk.Label(form, text="Monthly Limit ($)", bg="#2c2f3f", fg="#7aa2f7",
                 font=("Helvetica", 9)).grid(row=0, column=1, padx=8, sticky="w")

        self.cat_var = tk.StringVar(value=self.cat_names[0] if self.cat_names else "")
        ttk.Combobox(form, textvariable=self.cat_var, values=self.cat_names,
                     width=14, state="readonly").grid(row=1, column=0, padx=8, pady=4)

        self.limit_entry = tk.Entry(form, width=14, bg="#3d4166", fg="white",
                                    insertbackground="white")
        self.limit_entry.grid(row=1, column=1, padx=8, pady=4)

        tk.Button(form, text="➕ Set Budget", bg="#7aa2f7", fg="black", relief="flat",
                  font=("Helvetica", 10, "bold"), padx=12,
                  command=self._add_budget).grid(row=1, column=2, padx=8)

        self.list_frame = tk.Frame(self, bg="#1e1e2e")
        self.list_frame.pack(fill="both", expand=True, padx=30)

        self._load_budgets()

    def _add_budget(self):
        try:
            cat = Categories.get_by_name(self.cat_var.get())
            if not cat:
                messagebox.showerror("Error", "Category not found.")
                return
            b = Budget(None, cat.id, float(self.limit_entry.get()), "monthly")
            b.save()
            self.limit_entry.delete(0, "end")
            self._load_budgets()
            messagebox.showinfo("Success", "Budget set!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_budgets(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        budgets = Budget.get_all_budget()
        if not budgets:
            tk.Label(self.list_frame, text="No budgets set yet.", bg="#1e1e2e",
                     fg="#565f89", font=("Helvetica", 12)).pack(pady=40)
            return

        for b in budgets:
            cat = Categories.get_by_category_id(b.category_id)
            name = cat.name if cat else f"Category {b.category_id}"
            spent = b.get_spent()
            limit = b.amount
            pct = min((spent / limit * 100) if limit > 0 else 0, 100)
            color = "#9ece6a" if pct < 75 else ("#e0af68" if pct < 100 else "#f7768e")

            row = tk.Frame(self.list_frame, bg="#2c2f3f", pady=8, padx=16)
            row.pack(fill="x", pady=6, ipady=4)

            tk.Label(row, text=name, bg="#2c2f3f", fg="#c0caf5",
                     font=("Helvetica", 11, "bold"), width=16, anchor="w").grid(row=0, column=0, padx=(0,10))

            bar = ttk.Progressbar(row, length=400, maximum=100, value=pct)
            style = ttk.Style()
            style.configure("green.Horizontal.TProgressbar", troughcolor="#3d4166", background="#9ece6a")
            style.configure("yellow.Horizontal.TProgressbar", troughcolor="#3d4166", background="#e0af68")
            style.configure("red.Horizontal.TProgressbar", troughcolor="#3d4166", background="#f7768e")
            bar_style = "green" if pct < 75 else ("yellow" if pct < 100 else "red")
            bar.configure(style=f"{bar_style}.Horizontal.TProgressbar")
            bar.grid(row=0, column=1, padx=10)

            status = "✅ OK" if pct < 75 else ("⚠️ Near Limit" if pct < 100 else "🚨 Over Budget!")
            tk.Label(row, text=f"${spent:.2f} / ${limit:.2f}  ({pct:.0f}%)  {status}",
                     bg="#2c2f3f", fg=color,
                     font=("Helvetica", 10)).grid(row=0, column=2, padx=10)
#  ANALYTICS SCREEN
class AnalyticsScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Analytics Dashboard", bg="#1e1e2e", fg="#a9b1d6",
                 font=("Helvetica", 16, "bold")).pack(pady=(20, 5), anchor="w", padx=30)

        transactions = Transactions.get_all_transactions()
        expenses     = [t for t in transactions if t.type == "expense"]

        if not expenses:
            tk.Label(self, text="No expense data yet.", bg="#1e1e2e", fg="#565f89",
                     font=("Helvetica", 12)).pack(pady=40)
            return

        # Build category totals
        cat_totals = {}
        for t in expenses:
            cat = Categories.get_by_category_id(t.category_id)
            name = cat.name if cat else "Other"
            cat_totals[name] = cat_totals.get(name, 0) + t.amount

        # Build monthly totals
        monthly = {}
        for t in expenses:
            month = t.date[:7]
            monthly[month] = monthly.get(month, 0) + t.amount
        months = sorted(monthly.keys())
        month_vals = [monthly[m] for m in months]

        # Build budget vs actual
        budgets   = Budget.get_all_budget()
        b_names   = []
        b_limits  = []
        b_actuals = []
        for b in budgets:
            cat = Categories.get_by_category_id(b.category_id)
            b_names.append(cat.name if cat else "?")
            b_limits.append(b.amount)
            b_actuals.append(b.get_spent())

        fig = Figure(figsize=(13, 4), facecolor="#1e1e2e")
        fig.subplots_adjust(wspace=0.4)

        colors = ["#7aa2f7","#9ece6a","#e0af68","#f7768e","#bb9af7","#2ac3de","#ff9e64"]

        # Pie chart
        ax1 = fig.add_subplot(131)
        ax1.set_facecolor("#2c2f3f")
        ax1.pie(list(cat_totals.values()), labels=list(cat_totals.keys()),
                autopct="%1.0f%%", colors=colors[:len(cat_totals)],
                textprops={"color":"#c0caf5", "fontsize":8})
        ax1.set_title("Spending by Category", color="#a9b1d6", fontsize=10)

        # Line chart
        ax2 = fig.add_subplot(132)
        ax2.set_facecolor("#2c2f3f")
        if months:
            ax2.plot(months, month_vals, color="#7aa2f7", marker="o", linewidth=2)
            ax2.fill_between(months, month_vals, alpha=0.2, color="#7aa2f7")
        ax2.set_title("Monthly Spending Trend", color="#a9b1d6", fontsize=10)
        ax2.tick_params(colors="#565f89", labelsize=7)
        ax2.spines[:].set_color("#3d4166")
        for label in ax2.get_xticklabels():
            label.set_rotation(30)

        # Bar chart
        ax3 = fig.add_subplot(133)
        ax3.set_facecolor("#2c2f3f")
        if b_names:
            x = range(len(b_names))
            ax3.bar([i - 0.2 for i in x], b_limits,  width=0.4, label="Budget",  color="#7aa2f7")
            ax3.bar([i + 0.2 for i in x], b_actuals, width=0.4, label="Actual",  color="#f7768e")
            ax3.set_xticks(list(x))
            ax3.set_xticklabels(b_names, rotation=30, fontsize=7, color="#c0caf5")
            ax3.legend(facecolor="#2c2f3f", labelcolor="#c0caf5", fontsize=8)
        ax3.set_title("Budget vs Actual", color="#a9b1d6", fontsize=10)
        ax3.tick_params(colors="#565f89", labelsize=7)
        ax3.spines[:].set_color("#3d4166")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)


#  MONTHLY REPORT SCREEN
class ReportScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Monthly Report", bg="#1e1e2e", fg="#a9b1d6",
                 font=("Helvetica", 16, "bold")).pack(pady=(20, 5), anchor="w", padx=30)

        # Month selector
        ctrl = tk.Frame(self, bg="#1e1e2e")
        ctrl.pack(anchor="w", padx=30, pady=5)

        now = datetime.today()
        months = [f"{now.year}-{m:02d}" for m in range(1, 13)]
        self.month_var = tk.StringVar(value=now.strftime("%Y-%m"))

        tk.Label(ctrl, text="Select Month:", bg="#1e1e2e", fg="#7aa2f7",
                 font=("Helvetica", 11)).pack(side="left")
        ttk.Combobox(ctrl, textvariable=self.month_var, values=months,
                     width=12, state="readonly").pack(side="left", padx=8)
        tk.Button(ctrl, text="Generate Report", bg="#7aa2f7", fg="black",
                  font=("Helvetica", 10, "bold"), relief="flat", padx=10,
                  command=self._generate).pack(side="left", padx=4)

        # Report output area
        self.report_frame = tk.Frame(self, bg="#1e1e2e")
        self.report_frame.pack(fill="both", expand=True, padx=30, pady=10)

        self._generate()

    def _generate(self):
        for w in self.report_frame.winfo_children():
            w.destroy()

        month_str = self.month_var.get()
        year, month = int(month_str[:4]), int(month_str[5:7])
        transactions = Transactions.get_by_month(year, month)

        expenses = [t for t in transactions if t.type == "expense"]
        income   = [t for t in transactions if t.type == "income"]

        total_exp = sum(t.amount for t in expenses)
        total_inc = sum(t.amount for t in income)
        savings   = total_inc - total_exp
        savings_rate = (savings / total_inc * 100) if total_inc > 0 else 0

        # Summary cards
        cards = tk.Frame(self.report_frame, bg="#1e1e2e")
        cards.pack(fill="x", pady=10)

        metrics = [
            ("💰 Income",    f"${total_inc:.2f}",  "#9ece6a"),
            ("💸 Expenses",  f"${total_exp:.2f}",  "#f7768e"),
            ("🏦 Savings",   f"${savings:.2f}",    "#7aa2f7"),
            ("📊 Savings %", f"{savings_rate:.1f}%","#e0af68"),
        ]
        for label, value, color in metrics:
            card = tk.Frame(cards, bg="#2c2f3f", padx=20, pady=12)
            card.pack(side="left", expand=True, fill="x", padx=8)
            tk.Label(card, text=label, bg="#2c2f3f", fg="#7aa2f7",
                     font=("Helvetica", 10)).pack()
            tk.Label(card, text=value, bg="#2c2f3f", fg=color,
                     font=("Helvetica", 18, "bold")).pack()

        if not expenses:
            tk.Label(self.report_frame, text="No expense data for this month.",
                     bg="#1e1e2e", fg="#565f89", font=("Helvetica", 11)).pack(pady=20)
            return

        # Pie chart
        cat_totals = {}
        for t in expenses:
            cat = Categories.get_by_category_id(t.category_id)
            name = cat.name if cat else "Other"
            cat_totals[name] = cat_totals.get(name, 0) + t.amount

        fig = Figure(figsize=(5, 3.5), facecolor="#1e1e2e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#2c2f3f")
        colors = ["#7aa2f7","#9ece6a","#e0af68","#f7768e","#bb9af7","#2ac3de","#ff9e64"]
        ax.pie(list(cat_totals.values()), labels=list(cat_totals.keys()),
               autopct="%1.0f%%", colors=colors[:len(cat_totals)],
               textprops={"color":"#c0caf5", "fontsize":9})
        ax.set_title(f"Spending Breakdown — {month_str}", color="#a9b1d6", fontsize=11)

        canvas = FigureCanvasTkAgg(fig, master=self.report_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5)

        # Top categories text
        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
        info = tk.Frame(self.report_frame, bg="#2c2f3f", padx=16, pady=10)
        info.pack(fill="x", pady=5)
        tk.Label(info, text="Top Spending Categories", bg="#2c2f3f", fg="#a9b1d6",
                 font=("Helvetica", 11, "bold")).pack(anchor="w")
        for i, (cat, amt) in enumerate(sorted_cats[:5], 1):
            tk.Label(info, text=f"  {i}. {cat}: ${amt:.2f}",
                     bg="#2c2f3f", fg="#c0caf5", font=("Helvetica", 10)).pack(anchor="w")


#  ENTRY POINT
if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app  = MainWindow(root)
    root.mainloop()