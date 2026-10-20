import os
import tkinter as tk
from tkinter import messagebox, ttk

from User_profile import (
    create_database, create_household_profile, create_user_profile,
    get_linked_profiles, get_user_profile, inflation_adjustment,
    required_monthly_savings, tax,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

BG = "#eeeeee"
PANEL = "#b8b8b8"
DARK = "#444444"
MID = "#777777"
WHITE = "#ffffff"

TEST_STOCKS = [
    {"ticker": "TEST_HIGH", "company_name": "High Growth Company", "sector": "Technology", "dividend_yield": 5.0, "market_cap": 3, "risk": 1, "growth": 7},
    {"ticker": "TEST_MEDIUM", "company_name": "Medium Growth Strong Match Company", "sector": "Technology", "dividend_yield": 5.0, "market_cap": 1, "risk": 3, "growth": 5},
    {"ticker": "TEST_LOW", "company_name": "Low Growth Company", "sector": "Financial Services", "dividend_yield": 1.0, "market_cap": 1, "risk": 3, "growth": 3},
]


def money(value):
    return f"฿{value:,.2f}"


def calculate_monthly_investment(main_profile, linked_profiles):
    after_tax_income = main_profile[8] - tax(main_profile[8])
    expenses = main_profile[9]
    for linked in linked_profiles:
        after_tax_income += linked[8] - tax(linked[8])
        expenses += linked[9]
    return max(((after_tax_income - expenses) / 12) * (main_profile[16] / 100), 0)


def calculate_projected_value(assets, monthly, months, annual_growth):
    value = assets
    monthly_rate = ((1 + annual_growth / 100) ** (1 / 12)) - 1
    for _ in range(months):
        value = (value + monthly) * (1 + monthly_rate)
    return value


def calculate_preference_match(household, stock):
    score = 0
    risk_difference = abs(household["risk_tolerance"] - stock["risk"])
    score += 40 if risk_difference == 0 else 20 if risk_difference == 1 else 0
    score += 10 if household["interested_sector"].strip().lower() == stock["sector"].lower() else 0
    score += 40 if stock["dividend_yield"] >= household["interested_dividend"] else 20 if stock["dividend_yield"] >= household["interested_dividend"] - 1 else 0
    cap_difference = abs(household["market_cap_preference"] - stock["market_cap"])
    score += 10 if cap_difference == 0 else 5 if cap_difference == 1 else 0
    return score


def recommendation_reasons(household, stock):
    reasons = []
    if household["risk_tolerance"] == stock["risk"]:
        reasons.append("Matches your risk tolerance")
    if household["interested_sector"].strip().lower() == stock["sector"].lower():
        reasons.append("Matches your sector preference")
    if stock["dividend_yield"] >= household["interested_dividend"]:
        reasons.append("Matches your dividend preference")
    if household["market_cap_preference"] == stock["market_cap"]:
        reasons.append("Matches your market-cap preference")
    return reasons or ["Limited preference match"]


def build_recommendations(profile, linked, household):
    monthly = calculate_monthly_investment(profile, linked)
    adjusted_goal = inflation_adjustment(household["money_by_retirement"], household["age"], household["retirement_age"], 0.03)
    required, remaining, months = required_monthly_savings(adjusted_goal, household["current_assets"], household["age"], household["retirement_age"])
    stocks = []
    for item in TEST_STOCKS:
        stock = item.copy()
        preference = calculate_preference_match(household, stock)
        projected = calculate_projected_value(household["current_assets"], monthly, months, stock["growth"])
        growth_match = 100 if adjusted_goal <= 0 else max(0, min(projected / adjusted_goal * 100, 100))
        stock.update({
            "preference_match": preference,
            "projected_value": projected,
            "growth_match": growth_match,
            "final_score": preference * 0.60 + growth_match * 0.40,
            "reasons": recommendation_reasons(household, stock),
        })
        stocks.append(stock)
    stocks.sort(key=lambda stock: stock["final_score"], reverse=True)
    total = sum(stock["final_score"] for stock in stocks)
    for stock in stocks:
        stock["allocation"] = stock["final_score"] / total * 100 if total else 0
        stock["monthly_amount"] = monthly * stock["allocation"] / 100
    calculations = {"monthly": monthly, "adjusted_goal": adjusted_goal, "required": required, "remaining": remaining, "months": months}
    return stocks, calculations


class FinancialPlannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Household Financial Planner")
        self.geometry("1180x760")
        self.minsize(1000, 680)
        self.configure(bg=BG)
        self.profile = None
        self.linked = []
        self.household = None
        self.stocks = []
        self.calculations = {}
        self.profile_id = tk.StringVar(value="1")
        self.content = None
        self._configure_styles()
        self._build_header()
        self.show_profiles()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=DARK, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", foreground=MID)
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=9, background=DARK, foreground=WHITE)
        style.map("TButton", background=[("active", "#222222")])
        style.configure("TEntry", padding=7)
        style.configure("TCombobox", padding=6)

    def _build_header(self):
        header = ttk.Frame(self, padding=(24, 18, 24, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Household Financial Planner", style="Title.TLabel").grid(row=0, column=0, columnspan=6, sticky="w")
        ttk.Label(header, text="Retirement planning and educational stock recommendations", style="Subtitle.TLabel").grid(row=1, column=0, columnspan=6, sticky="w", pady=(0, 12))
        ttk.Label(header, text="Profile ID").grid(row=2, column=0, sticky="w")
        ttk.Entry(header, textvariable=self.profile_id, width=10).grid(row=2, column=1, padx=(6, 8))
        ttk.Button(header, text="Load Profile", command=self.load_profile).grid(row=2, column=2, padx=(0, 20))
        for column, (text, command) in enumerate([
            ("Profiles", self.show_profiles),
            ("Stock Picks", self.show_stock_picks),
            ("Portfolio Dashboard", self.show_dashboard),
            ("Add Member", self.show_profile_form),
        ], 3):
            ttk.Button(header, text=text, command=command).grid(row=2, column=column, padx=4)
        header.columnconfigure(7, weight=1)
        tk.Frame(self, bg=DARK, height=2).pack(fill="x", padx=24)

    def _new_content(self):
        if self.content is not None:
            self.content.destroy()
        self.content = ttk.Frame(self, padding=24)
        self.content.pack(fill="both", expand=True)
        return self.content

    def load_profile(self):
        try:
            profile_id = int(self.profile_id.get())
        except ValueError:
            messagebox.showerror("Invalid profile", "Profile ID must be a whole number.")
            return False
        connect, cursor = create_database()
        try:
            profile = get_user_profile(cursor, profile_id)
            if profile is None:
                messagebox.showerror("Profile not found", f"No profile exists with ID {profile_id}.")
                return False
            linked = get_linked_profiles(cursor, profile_id)
            self.profile = profile
            self.linked = linked
            self.household = create_household_profile(profile, linked)
            self.stocks, self.calculations = build_recommendations(profile, linked, self.household)
        finally:
            connect.close()
        messagebox.showinfo("Profile loaded", f"Loaded {self.profile[1]} and {len(self.linked)} linked profile(s).")
        self.show_profiles()
        return True

    def _ensure_profile(self):
        if self.profile is not None:
            return True
        return self.load_profile()

    def _profile_card(self, parent, title, person, column):
        card = tk.Frame(parent, bg=PANEL, highlightbackground=DARK, highlightthickness=1, padx=16, pady=12)
        card.grid(row=0, column=column, padx=10, sticky="nsew")
        tk.Label(card, text=title, bg=PANEL, fg=DARK, font=("Segoe UI", 17)).pack(anchor="w")
        tk.Label(card, text="●", bg=PANEL, fg=DARK, font=("Segoe UI", 72)).pack(pady=(0, 4))
        for value in [person[1], f"Age: {person[4]}", f"Retirement Age: {person[5]}", f"Yearly Costs: {money(person[9])}", f"Salary: {money(person[8])}", f"Future Financial Goal: {money(person[13])}"]:
            tk.Label(card, text=value, bg=WHITE, fg=DARK, relief="solid", bd=1, font=("Segoe UI", 10), pady=5).pack(fill="x", pady=4)
        parent.columnconfigure(column, weight=1)

    def show_profiles(self):
        page = self._new_content()
        if not self._ensure_profile():
            ttk.Label(page, text="Load a profile to display the profile wireframe.", font=("Segoe UI", 14)).pack(pady=80)
            return
        people = [("User Profile", self.profile)] + [(f"Family Member {i}", member) for i, member in enumerate(self.linked, 1)]
        cards = ttk.Frame(page)
        cards.pack(fill="both", expand=True)
        for column, (title, person) in enumerate(people[:3]):
            self._profile_card(cards, title, person, column)
        if len(people) < 3:
            add = tk.Frame(cards, bg=BG, padx=30, pady=20)
            add.grid(row=0, column=len(people), sticky="n")
            ttk.Button(add, text="Add Member", command=self.show_profile_form).pack(pady=20)

    def show_stock_picks(self):
        if not self._ensure_profile():
            return
        page = self._new_content()
        filters = ttk.Frame(page)
        filters.pack(fill="x", pady=(0, 12))
        values = [
            ("Risk", {1: "Low", 2: "Medium", 3: "High"}[self.household["risk_tolerance"]]),
            ("Expected Growth", "Calculated from goal"),
            ("Expected Dividend", f'{self.household["interested_dividend"]}%'),
            ("Sector", self.household["interested_sector"]),
        ]
        for column, (label, value) in enumerate(values):
            box = ttk.Frame(filters)
            box.grid(row=0, column=column, padx=5, sticky="ew")
            ttk.Label(box, text=label).pack(anchor="w")
            ttk.Combobox(box, values=[value], state="readonly", width=23).pack(fill="x")
            filters.columnconfigure(column, weight=1)
        ttk.Button(page, text="Generate Stock Picks", command=self._display_stock_results).pack(fill="x", pady=(0, 15))
        self.results_frame = tk.Frame(page, bg=WHITE, highlightbackground=MID, highlightthickness=1, padx=14, pady=12)
        self.results_frame.pack(fill="both", expand=True)
        tk.Label(self.results_frame, text="Select Generate Stock Picks to display recommendations.", bg=WHITE, fg=MID, font=("Segoe UI", 12)).pack(pady=80)

    def _display_stock_results(self):
        for child in self.results_frame.winfo_children():
            child.destroy()
        tk.Label(self.results_frame, text="Recommended Stocks", bg=WHITE, fg=DARK, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))
        for rank, stock in enumerate(self.stocks, 1):
            text = (f"{rank}. {stock['company_name']}\n"
                    f"Match: {stock['final_score']:.2f}%     Recommended monthly amount: {money(stock['monthly_amount'])}\n"
                    f"{' | '.join(stock['reasons'])}")
            tk.Label(self.results_frame, text=text, justify="left", anchor="w", bg="#f5f5f5", fg=DARK, relief="solid", bd=1, padx=12, pady=8).pack(fill="x", pady=5)
        tk.Label(self.results_frame, text="Educational demonstration only. Markets can lose value; this is not financial advice.", bg=WHITE, fg=DARK, font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=10)

    def show_dashboard(self):
        if not self._ensure_profile():
            return
        page = self._new_content()
        left = tk.Frame(page, bg=PANEL, highlightbackground=MID, highlightthickness=1, padx=18, pady=16)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(page, bg=PANEL, highlightbackground=MID, highlightthickness=1, padx=18, pady=16)
        right.pack(side="right", fill="both", expand=True)
        tk.Label(left, text="Companies     Amount", bg=PANEL, fg=DARK, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        for stock in self.stocks:
            tk.Label(left, text=f"{stock['company_name']}\n{money(stock['monthly_amount'])}  ({stock['allocation']:.2f}%)", bg=PANEL, fg=DARK, justify="left", font=("Segoe UI", 11)).pack(anchor="w", pady=9)
        tk.Label(left, text=f"Household members: {self.household['members']}\nCurrent assets: {money(self.household['current_assets'])}\nChosen monthly investment: {money(self.calculations['monthly'])}", bg=PANEL, fg=DARK, justify="left", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=18)
        self._performance_chart(right)
        self._allocation_chart(right)
        self._progress_panel(right)

    def _performance_chart(self, parent):
        canvas = tk.Canvas(parent, height=155, bg=WHITE, highlightbackground=MID, highlightthickness=1)
        canvas.pack(fill="x", pady=(0, 10))
        canvas.create_text(12, 12, text="Performance", anchor="nw", fill=DARK, font=("Segoe UI", 13, "bold"))
        maximum = max(stock["projected_value"] for stock in self.stocks) or 1
        for index, stock in enumerate(self.stocks):
            x1 = 85 + index * 105
            height = 90 * stock["projected_value"] / maximum
            canvas.create_rectangle(x1, 125 - height, x1 + 45, 125, fill=DARK, outline=DARK)
            canvas.create_text(x1 + 22, 140, text=stock["ticker"].replace("TEST_", ""), fill=DARK, font=("Segoe UI", 8))

    def _allocation_chart(self, parent):
        canvas = tk.Canvas(parent, height=185, bg=WHITE, highlightbackground=MID, highlightthickness=1)
        canvas.pack(fill="x", pady=(0, 10))
        canvas.create_text(12, 12, text="Portfolio Diversification", anchor="nw", fill=DARK, font=("Segoe UI", 13, "bold"))
        colors = ["#333333", "#777777", "#bbbbbb"]
        start = 0
        for stock, color in zip(self.stocks, colors):
            extent = stock["allocation"] * 3.6
            canvas.create_arc(25, 45, 155, 175, start=start, extent=extent, fill=color, outline=WHITE)
            start += extent
        canvas.create_oval(57, 77, 123, 143, fill=WHITE, outline=WHITE)
        for index, stock in enumerate(self.stocks):
            canvas.create_rectangle(190, 55 + index * 34, 210, 75 + index * 34, fill=colors[index], outline=colors[index])
            canvas.create_text(220, 65 + index * 34, text=f"{stock['ticker'].replace('TEST_', '')}: {stock['allocation']:.2f}%", anchor="w", fill=DARK, font=("Segoe UI", 9))

    def _progress_panel(self, parent):
        box = tk.Frame(parent, bg=WHITE, highlightbackground=MID, highlightthickness=1, padx=12, pady=10)
        box.pack(fill="x")
        tk.Label(box, text="Progress Overview", bg=WHITE, fg=DARK, font=("Segoe UI", 13, "bold")).pack(anchor="w")
        goal = max(self.calculations["adjusted_goal"], 1)
        progress = min(self.household["current_assets"] / goal * 100, 100)
        ttk.Progressbar(box, maximum=100, value=progress).pack(fill="x", pady=8)
        tk.Label(box, text=f"{progress:.2f}% of inflation-adjusted goal\nRemaining amount: {money(self.calculations['remaining'])}\nRequired monthly saving: {money(self.calculations['required'])}", bg=WHITE, fg=DARK, justify="left").pack(anchor="w")

    def show_profile_form(self):
        page = self._new_content()
        ttk.Label(page, text="Add Main User or Linked Family Member", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))
        form = ttk.Frame(page)
        form.pack(fill="both", expand=True)
        fields = [
            ("Name", ""), ("Age", "18"), ("Retirement age", "60"),
            ("Annual income", "0"), ("Annual expenses", "0"), ("Current assets", "0"),
            ("Interested sector", "Technology"), ("Risk tolerance (1-3)", "2"),
            ("Retirement goal", "1000000"), ("Dividend target (%)", "3"),
            ("Market-cap preference (1-3)", "1"), ("Disposable income to invest (%)", "50"),
            ("Main profile ID (linked only)", self.profile_id.get()),
        ]
        self.form_entries = {}
        for index, (label, default) in enumerate(fields):
            row, column = divmod(index, 2)
            cell = ttk.Frame(form, padding=(0, 0, 18, 8))
            cell.grid(row=row, column=column, sticky="ew")
            ttk.Label(cell, text=label).pack(anchor="w")
            entry = ttk.Entry(cell)
            entry.insert(0, default)
            entry.pack(fill="x")
            self.form_entries[label] = entry
            form.columnconfigure(column, weight=1)
        choices = ttk.Frame(form)
        choices.grid(row=7, column=0, columnspan=2, sticky="ew", pady=8)
        self.relationship_var = tk.StringVar(value="Main User")
        self.marital_var = tk.StringVar(value="single")
        self.parent_var = tk.StringVar(value="non-parent")
        for label, variable, values in [
            ("Profile type", self.relationship_var, ["Main User", "spouse", "child", "family"]),
            ("Marital status", self.marital_var, ["single", "married", "divorced"]),
            ("Parental status", self.parent_var, ["non-parent", "parent"]),
        ]:
            block = ttk.Frame(choices, padding=(0, 0, 18, 0))
            block.pack(side="left", fill="x", expand=True)
            ttk.Label(block, text=label).pack(anchor="w")
            ttk.Combobox(block, textvariable=variable, values=values, state="readonly").pack(fill="x")
        ttk.Button(form, text="Save", command=self.save_profile).grid(row=8, column=0, columnspan=2, sticky="ew", pady=12)

    def save_profile(self):
        try:
            value = lambda key: self.form_entries[key].get().strip()
            name = value("Name")
            age = int(value("Age"))
            retirement = int(value("Retirement age"))
            income = int(value("Annual income"))
            expenses = int(value("Annual expenses"))
            assets = int(value("Current assets"))
            sector = value("Interested sector")
            risk = int(value("Risk tolerance (1-3)"))
            goal = int(value("Retirement goal"))
            dividend = int(value("Dividend target (%)"))
            cap = int(value("Market-cap preference (1-3)"))
            percentage = float(value("Disposable income to invest (%)"))
            main_id = int(value("Main profile ID (linked only)"))
        except ValueError:
            messagebox.showerror("Invalid input", "Number fields must contain numbers only.")
            return
        if not name or retirement <= age or risk not in (1, 2, 3) or cap not in (1, 2, 3) or not 0 <= percentage <= 100:
            messagebox.showerror("Invalid input", "Check the name, ages, risk, market cap and percentage values.")
            return
        relationship = self.relationship_var.get()
        parent_id = None if relationship == "Main User" else main_id
        connect, cursor = create_database()
        try:
            if parent_id is not None and get_user_profile(cursor, parent_id) is None:
                messagebox.showerror("Invalid main profile", f"Profile ID {parent_id} does not exist.")
                return
            create_user_profile(cursor, connect, relationship, parent_id, name, age, retirement, income, expenses, assets, sector, risk, goal, self.marital_var.get(), self.parent_var.get(), dividend, cap, percentage)
            new_id = cursor.lastrowid
        finally:
            connect.close()
        if relationship == "Main User":
            self.profile_id.set(str(new_id))
        messagebox.showinfo("Saved", f"Profile saved with ID {new_id}.")
        self.profile = None
        self.load_profile()


def main():
    app = FinancialPlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
