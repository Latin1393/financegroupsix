#!/usr/bin/env python3
"""
Rent vs. Buy Financial Simulation
MBA-Level NPV / IRR / Opportunity-Cost / Comps Analysis

Dependencies:  python3 -m pip install numpy numpy-financial matplotlib
Run:           python3 rent_vs_buy.py
"""

import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
import numpy as np
import numpy_financial as npf
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ──────────────────────────────────────────────
# Colour palette
# ──────────────────────────────────────────────
BG       = "#1e1e2e"
SURFACE  = "#2a2a3c"
CARD     = "#33334a"
ACCENT   = "#7aa2f7"
GREEN    = "#9ece6a"
RED      = "#f7768e"
ORANGE   = "#e0af68"
TEXT     = "#c0caf5"
SUBTEXT  = "#8b95b0"
ENTRY_BG = "#3b3b54"
CHART_BG   = "#2a2a3c"
CHART_FACE = "#1e1e2e"

# ──────────────────────────────────────────────
# Financial engine
# ──────────────────────────────────────────────

def run_simulation(params: dict) -> dict:
    home_price       = params["home_price"]
    sqft             = params["sqft"]
    down_pct         = params["down_pct"] / 100
    rate_annual      = params["mortgage_rate"] / 100
    term_years       = params["mortgage_term"]
    prop_tax_pct     = params["prop_tax"] / 100
    insurance_annual = params["insurance"]
    maint_pct        = params["maintenance"] / 100
    appr_annual      = params["appreciation"] / 100
    closing_buy_pct  = params["closing_buy"] / 100
    closing_sell_pct = params["closing_sell"] / 100
    marginal_tax     = params["marginal_tax"] / 100
    hold_years       = params["hold_years"]
    monthly_rent     = params["monthly_rent"]
    rent_growth      = params["rent_growth"] / 100
    renter_ins       = params["renter_ins"]
    invest_return    = params["invest_return"] / 100
    discount_rate    = params["discount_rate"] / 100

    months = int(hold_years * 12)
    r_mo   = rate_annual / 12
    n_pmt  = int(term_years * 12)

    down_payment = home_price * down_pct
    loan_amount  = home_price - down_payment
    closing_buy  = home_price * closing_buy_pct

    if loan_amount > 0 and r_mo > 0:
        monthly_pmt = npf.pmt(r_mo, n_pmt, -loan_amount)
    elif loan_amount > 0:
        monthly_pmt = loan_amount / n_pmt
    else:
        monthly_pmt = 0.0

    buy_cf    = [0.0] * (months + 1)
    buy_cf[0] = -(down_payment + closing_buy)

    balance         = loan_amount
    total_interest  = 0.0
    total_principal = 0.0
    total_prop_tax  = 0.0
    total_insurance = 0.0
    total_maint     = 0.0

    buyer_equity_ts   = [0.0]
    buyer_monthly_out = []
    home_value_ts     = [home_price]

    for m in range(1, months + 1):
        interest_pmt  = balance * r_mo if balance > 0 else 0
        principal_pmt = monthly_pmt - interest_pmt if balance > 0 else 0
        if principal_pmt > balance:
            principal_pmt = balance
        balance -= principal_pmt

        prop_tax_mo = (home_price * (1 + appr_annual) ** ((m - 1) / 12)) * prop_tax_pct / 12
        ins_mo      = insurance_annual / 12
        maint_mo    = (home_price * (1 + appr_annual) ** ((m - 1) / 12)) * maint_pct / 12
        tax_shield  = interest_pmt * marginal_tax

        outflow = monthly_pmt + prop_tax_mo + ins_mo + maint_mo - tax_shield
        buy_cf[m] = -outflow

        total_interest  += interest_pmt
        total_principal += principal_pmt
        total_prop_tax  += prop_tax_mo
        total_insurance += ins_mo
        total_maint     += maint_mo

        curr_home_val = home_price * (1 + appr_annual) ** (m / 12)
        home_value_ts.append(curr_home_val)
        buyer_equity_ts.append(curr_home_val - balance)
        buyer_monthly_out.append(outflow)

    future_home_value = home_price * (1 + appr_annual) ** hold_years
    remaining_balance = balance
    closing_sell      = future_home_value * closing_sell_pct
    net_sale_proceeds = future_home_value - remaining_balance - closing_sell
    buy_cf[months]   += net_sale_proceeds
    total_buy_outflows = abs(sum(cf for cf in buy_cf if cf < 0))

    # ── RENT ────────────────────────────────
    rent_cf         = [0.0] * (months + 1)
    total_rent_paid = 0.0
    renter_monthly_out = []

    for m in range(1, months + 1):
        year_idx      = (m - 1) // 12
        current_rent  = monthly_rent * (1 + rent_growth) ** year_idx
        renter_ins_mo = renter_ins / 12
        outflow       = current_rent + renter_ins_mo
        rent_cf[m]    = -outflow
        total_rent_paid += current_rent
        renter_monthly_out.append(outflow)

    total_rent_outflows = abs(sum(cf for cf in rent_cf if cf < 0))

    # ── Opportunity cost ────────────────────
    invest_r_mo  = invest_return / 12
    portfolio    = down_payment + closing_buy
    portfolio_ts = [portfolio]

    for m in range(1, months + 1):
        buy_outflow  = abs(buy_cf[m]) if buy_cf[m] < 0 else 0
        rent_outflow = abs(rent_cf[m])
        diff = buy_outflow - rent_outflow
        portfolio = portfolio * (1 + invest_r_mo) + max(diff, 0)
        if diff < 0:
            portfolio = portfolio + diff
        portfolio_ts.append(max(portfolio, 0))

    renter_terminal_wealth = max(portfolio, 0)

    # ── NPV ─────────────────────────────────
    d_mo     = discount_rate / 12
    buy_npv  = npf.npv(d_mo, buy_cf)
    rent_npv = npf.npv(d_mo, rent_cf)
    rent_npv_with_invest = rent_npv + renter_terminal_wealth / (1 + d_mo) ** months

    # ── IRR ─────────────────────────────────
    try:
        buy_irr_mo  = npf.irr(buy_cf)
        buy_irr_ann = (1 + buy_irr_mo) ** 12 - 1 if buy_irr_mo and not np.isnan(buy_irr_mo) else None
    except Exception:
        buy_irr_ann = None

    rent_invest_cf     = [-(down_payment + closing_buy)] + [0.0] * months
    rent_invest_cf[-1] = renter_terminal_wealth
    try:
        rent_irr_mo  = npf.irr(rent_invest_cf)
        rent_irr_ann = (1 + rent_irr_mo) ** 12 - 1 if rent_irr_mo and not np.isnan(rent_irr_mo) else None
    except Exception:
        rent_irr_ann = None

    buyer_net_wealth  = net_sale_proceeds
    renter_net_wealth = renter_terminal_wealth

    price_per_sqft    = home_price / sqft if sqft > 0 else 0
    rent_per_sqft     = monthly_rent / sqft if sqft > 0 else 0
    future_price_sqft = future_home_value / sqft if sqft > 0 else 0

    buy_yearly_avg  = []
    rent_yearly_avg = []
    for y in range(int(hold_years)):
        s, e = y * 12, min(y * 12 + 12, months)
        buy_yearly_avg.append(np.mean(buyer_monthly_out[s:e]))
        rent_yearly_avg.append(np.mean(renter_monthly_out[s:e]))

    return {
        "months": months, "hold_years": hold_years, "sqft": sqft,
        "down_payment": down_payment, "loan_amount": loan_amount,
        "monthly_pmt": monthly_pmt, "total_interest": total_interest,
        "total_prop_tax": total_prop_tax, "total_insurance": total_insurance,
        "total_maint": total_maint, "future_home_value": future_home_value,
        "remaining_balance": remaining_balance, "closing_sell_cost": closing_sell,
        "net_sale_proceeds": net_sale_proceeds, "total_buy_outflows": total_buy_outflows,
        "buy_npv": buy_npv, "buy_irr": buy_irr_ann,
        "buyer_net_wealth": buyer_net_wealth,
        "total_rent_paid": total_rent_paid, "total_rent_outflows": total_rent_outflows,
        "renter_terminal": renter_terminal_wealth,
        "rent_npv": rent_npv, "rent_npv_with_invest": rent_npv_with_invest,
        "rent_irr": rent_irr_ann, "renter_net_wealth": renter_net_wealth,
        "advantage": "BUY" if buyer_net_wealth > renter_net_wealth else "RENT",
        "advantage_amount": abs(buyer_net_wealth - renter_net_wealth),
        "price_per_sqft": price_per_sqft, "rent_per_sqft": rent_per_sqft,
        "future_price_sqft": future_price_sqft,
        "buyer_equity_ts": buyer_equity_ts, "portfolio_ts": portfolio_ts,
        "home_value_ts": home_value_ts,
        "buy_yearly_avg": buy_yearly_avg, "rent_yearly_avg": rent_yearly_avg,
    }


def fmt_usd(v):
    return "N/A" if v is None else f"${v:,.0f}"

def fmt_usd2(v):
    return "N/A" if v is None else f"${v:,.2f}"

def fmt_pct(v):
    return "N/A" if v is None else f"{v * 100:,.2f}%"


# ──────────────────────────────────────────────
# Comps analysis
# ──────────────────────────────────────────────

def analyse_comps(comps: list, subject_price: float, subject_sqft: float,
                  subject_rent: float) -> dict:
    """
    comps: list of dicts with keys: name, price, sqft, rent
    Any comp with at least name + one numeric field is kept.
    """
    if not comps:
        return None

    # Separate pools: comps with price+sqft (for $/sqft) and comps with rent (for cap rate)
    price_comps = [c for c in comps if c["price"] > 0 and c["sqft"] > 0]
    rent_comps  = [c for c in comps if c["rent"] > 0 and c["sqft"] > 0]
    cap_comps   = [c for c in comps if c["rent"] > 0 and c["price"] > 0]

    if not price_comps and not rent_comps:
        return None

    prices_sqft = [c["price"] / c["sqft"] for c in price_comps] if price_comps else []
    rents_sqft  = [c["rent"] / c["sqft"] for c in rent_comps] if rent_comps else []
    cap_rates   = [(c["rent"] * 12) / c["price"] for c in cap_comps] if cap_comps else []
    prices      = [c["price"] for c in price_comps] if price_comps else []

    subj_price_sqft = subject_price / subject_sqft if subject_sqft > 0 else 0
    subj_rent_sqft  = subject_rent / subject_sqft if subject_sqft > 0 else 0
    subj_cap = (subject_rent * 12) / subject_price if subject_price > 0 and subject_rent > 0 else 0

    avg_price_sqft = np.mean(prices_sqft) if prices_sqft else 0
    avg_rent_sqft  = np.mean(rents_sqft) if rents_sqft else 0
    avg_cap        = np.mean(cap_rates) if cap_rates else 0
    med_price      = np.median(prices) if prices else 0

    implied_value = avg_price_sqft * subject_sqft if subject_sqft > 0 and avg_price_sqft > 0 else 0
    premium_discount = ((subject_price / implied_value) - 1) * 100 if implied_value > 0 else 0

    return {
        "price_comps":      price_comps,
        "rent_comps":       rent_comps,
        "cap_comps":        cap_comps,
        "count_price":      len(price_comps),
        "count_rent":       len(rent_comps),
        "avg_price_sqft":   avg_price_sqft,
        "avg_rent_sqft":    avg_rent_sqft,
        "avg_cap_rate":     avg_cap,
        "median_price":     med_price,
        "subj_price_sqft":  subj_price_sqft,
        "subj_rent_sqft":   subj_rent_sqft,
        "subj_cap_rate":    subj_cap,
        "implied_value":    implied_value,
        "premium_discount": premium_discount,
        "prices_sqft":      prices_sqft,
        "rents_sqft":       rents_sqft,
    }


# ──────────────────────────────────────────────
# GUI
# ──────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rent vs. Buy  |  NPV / IRR / Comps Simulation")
        self.configure(bg=BG)
        self.minsize(1280, 900)
        self.geometry("1360x940")

        self.title_font  = tkfont.Font(family="Helvetica Neue", size=20, weight="bold")
        self.head_font   = tkfont.Font(family="Helvetica Neue", size=13, weight="bold")
        self.label_font  = tkfont.Font(family="Helvetica Neue", size=11)
        self.entry_font  = tkfont.Font(family="Menlo", size=11)
        self.result_font = tkfont.Font(family="Menlo", size=11)
        self.small_font  = tkfont.Font(family="Helvetica Neue", size=10)

        self.comp_rows = []
        self._build_ui()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(18, 6))
        tk.Label(hdr, text="Rent vs. Buy Simulator", font=self.title_font,
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text="NPV  |  IRR  |  Opportunity Cost  |  Comps",
                 font=self.small_font, bg=BG, fg=SUBTEXT).pack(side="left", padx=14, pady=4)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=10)

        # ── Left: scrollable inputs ─────────
        left_outer = tk.Frame(body, bg=BG, width=480)
        left_outer.pack(side="left", fill="y", padx=(0, 12))
        left_outer.pack_propagate(False)

        left_canvas = tk.Canvas(left_outer, bg=BG, highlightthickness=0, width=460)
        left_scroll = tk.Scrollbar(left_outer, orient="vertical", command=left_canvas.yview)
        self.left_frame = tk.Frame(left_canvas, bg=BG)
        self.left_frame.bind("<Configure>",
                             lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=self.left_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scroll.set)
        left_canvas.pack(side="left", fill="both", expand=True)
        left_scroll.pack(side="right", fill="y")

        def _scroll(event):
            left_canvas.yview_scroll(-1 * (event.delta // 120 if event.delta else
                                           int(event.num == 4) - int(event.num == 5)), "units")
        left_canvas.bind_all("<MouseWheel>", _scroll)
        left_canvas.bind_all("<Button-4>", _scroll)
        left_canvas.bind_all("<Button-5>", _scroll)

        # ── Right: tabbed results ───────────
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook", background=BG, borderwidth=0)
        style.configure("Dark.TNotebook.Tab", background=CARD, foreground=TEXT,
                        padding=[14, 7], font=("Helvetica Neue", 11, "bold"))
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#1e1e2e")])

        self.notebook = ttk.Notebook(right, style="Dark.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Summary
        tab_summary = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab_summary, text="  Summary  ")
        self.result_text = tk.Text(tab_summary, bg=SURFACE, fg=TEXT,
                                   font=self.result_font, relief="flat",
                                   padx=18, pady=18, wrap="word", state="disabled",
                                   insertbackground=TEXT, selectbackground=ACCENT,
                                   highlightthickness=0)
        self.result_text.pack(fill="both", expand=True)
        for tag, kw in [("header", {"font": self.head_font, "foreground": ACCENT}),
                        ("green",  {"foreground": GREEN}),
                        ("red",    {"foreground": RED}),
                        ("orange", {"foreground": ORANGE}),
                        ("sub",    {"foreground": SUBTEXT, "font": self.small_font}),
                        ("bold",   {"font": tkfont.Font(family="Menlo", size=12, weight="bold")})]:
            self.result_text.tag_configure(tag, **kw)

        # Tab 2: Charts
        tab_charts = tk.Frame(self.notebook, bg=CHART_FACE)
        self.notebook.add(tab_charts, text="  Charts  ")
        self.chart_frame = tab_charts

        # Tab 3: Comps
        tab_comps = tk.Frame(self.notebook, bg=CHART_FACE)
        self.notebook.add(tab_comps, text="  Comps  ")
        self.comps_chart_frame = tab_comps

        # ── Build input sections ────────────
        self.entries = {}

        self._section(self.left_frame, "Subject Property", [
            ("home_price",     "Home Price ($)",              "400000"),
            ("sqft",           "Square Footage",              "1800"),
            ("location",       "Location / Neighborhood",     ""),
        ], text_fields=["location"])

        self._section(self.left_frame, "Purchase Assumptions", [
            ("down_pct",       "Down Payment (%)",            "20"),
            ("mortgage_rate",  "Mortgage Rate (%)",           "6.75"),
            ("mortgage_term",  "Loan Term (years)",           "30"),
            ("prop_tax",       "Property Tax (%/yr)",         "1.25"),
            ("insurance",      "Homeowner Ins. ($/yr)",       "1800"),
            ("maintenance",    "Maintenance (%/yr)",          "1.0"),
            ("appreciation",   "Home Appreciation (%/yr)",    "3.0"),
            ("closing_buy",    "Closing Costs - Buy (%)",     "3.0"),
            ("closing_sell",   "Closing Costs - Sell (%)",    "6.0"),
        ])

        self._section(self.left_frame, "Renting Assumptions", [
            ("monthly_rent",  "Monthly Rent ($)",             "2000"),
            ("rent_growth",   "Annual Rent Increase (%)",     "3.0"),
            ("renter_ins",    "Renter Insurance ($/yr)",      "250"),
        ])

        self._section(self.left_frame, "Analysis Parameters", [
            ("hold_years",    "Holding Period (years)",       "7"),
            ("invest_return", "Alt. Investment Return (%/yr)","8.0"),
            ("discount_rate", "Discount Rate (%/yr)",         "7.0"),
            ("marginal_tax",  "Marginal Tax Rate (%)",        "24"),
        ])

        self._build_comps_section(self.left_frame)

        tk.Button(self.left_frame, text="Run Simulation", font=self.head_font,
                  bg=ACCENT, fg="#1e1e2e", activebackground="#5b85e0",
                  activeforeground="#1e1e2e", bd=0, padx=20, pady=10,
                  cursor="hand2", command=self._run).pack(fill="x", pady=(14, 14))

        self._show_placeholder()

    def _section(self, parent, title, fields, text_fields=None):
        text_fields = text_fields or []
        frame = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=1,
                         highlightbackground="#44446a")
        frame.pack(fill="x", pady=(0, 10))
        tk.Label(frame, text=title, font=self.head_font,
                 bg=CARD, fg=ACCENT, anchor="w").pack(fill="x", padx=12, pady=(10, 4))
        for key, label, default in fields:
            row = tk.Frame(frame, bg=CARD)
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=label, font=self.label_font,
                     bg=CARD, fg=TEXT, width=26, anchor="w").pack(side="left")
            w = 18 if key in text_fields else 12
            e = tk.Entry(row, font=self.entry_font, bg=ENTRY_BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat", width=w,
                         highlightthickness=1, highlightcolor=ACCENT,
                         highlightbackground="#555578")
            e.insert(0, default)
            e.pack(side="left", padx=(4, 0))
            self.entries[key] = e
        tk.Frame(frame, bg=CARD, height=8).pack()

    # ── Comps table ─────────────────────────
    def _build_comps_section(self, parent):
        frame = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=1,
                         highlightbackground="#44446a")
        frame.pack(fill="x", pady=(0, 10))

        top_row = tk.Frame(frame, bg=CARD)
        top_row.pack(fill="x", padx=12, pady=(10, 2))
        tk.Label(top_row, text="Comparable Properties", font=self.head_font,
                 bg=CARD, fg=ACCENT, anchor="w").pack(side="left")

        # Instructions
        tk.Label(frame, text="Fill in what you have. Price+SqFt enables $/sqft chart. "
                 "Rent+Price enables cap rate chart.",
                 font=self.small_font, bg=CARD, fg=SUBTEXT, anchor="w",
                 wraplength=440, justify="left").pack(fill="x", padx=12, pady=(0, 6))

        # Column headers
        hdr = tk.Frame(frame, bg=CARD)
        hdr.pack(fill="x", padx=12, pady=(2, 2))
        for text, w in [("Name / Address", 16), ("Price ($)", 12),
                        ("Sq Ft", 8), ("Rent ($/mo)", 12)]:
            tk.Label(hdr, text=text, font=self.small_font, bg=CARD,
                     fg=ORANGE, width=w, anchor="w").pack(side="left", padx=2)

        self.comp_container = tk.Frame(frame, bg=CARD)
        self.comp_container.pack(fill="x", padx=12)

        for _ in range(5):
            self._add_comp_row()

        btn_row = tk.Frame(frame, bg=CARD)
        btn_row.pack(fill="x", padx=12, pady=(6, 10))
        tk.Button(btn_row, text="+ Add Comp", font=self.small_font,
                  bg=ENTRY_BG, fg=TEXT, bd=0, padx=10, pady=3,
                  activebackground="#555578", activeforeground=TEXT,
                  cursor="hand2", command=self._add_comp_row).pack(side="left")
        tk.Button(btn_row, text="Clear All", font=self.small_font,
                  bg=ENTRY_BG, fg=SUBTEXT, bd=0, padx=10, pady=3,
                  activebackground="#555578", activeforeground=TEXT,
                  cursor="hand2", command=self._clear_comps).pack(side="left", padx=6)

    def _add_comp_row(self):
        row = tk.Frame(self.comp_container, bg=CARD)
        row.pack(fill="x", pady=1)
        entries = []
        for w in [16, 12, 8, 12]:
            e = tk.Entry(row, font=self.entry_font, bg=ENTRY_BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat", width=w,
                         highlightthickness=1, highlightcolor=ACCENT,
                         highlightbackground="#555578")
            e.pack(side="left", padx=2)
            entries.append(e)
        self.comp_rows.append(tuple(entries))

    def _clear_comps(self):
        for widget in self.comp_container.winfo_children():
            widget.destroy()
        self.comp_rows.clear()
        for _ in range(5):
            self._add_comp_row()

    def _get_comps(self):
        """Parse comps — include any row that has a name and at least one number."""
        comps = []
        for name_e, price_e, sqft_e, rent_e in self.comp_rows:
            name = name_e.get().strip()
            if not name:
                continue
            try:
                price = float(price_e.get().replace(",", "").replace("$", "")) if price_e.get().strip() else 0
            except ValueError:
                price = 0
            try:
                sqft = float(sqft_e.get().replace(",", "")) if sqft_e.get().strip() else 0
            except ValueError:
                sqft = 0
            try:
                rent = float(rent_e.get().replace(",", "").replace("$", "")) if rent_e.get().strip() else 0
            except ValueError:
                rent = 0

            # Keep the comp if it has at least one useful number
            if price > 0 or sqft > 0 or rent > 0:
                comps.append({"name": name, "price": price, "sqft": sqft, "rent": rent})
        return comps

    def _show_placeholder(self):
        t = self.result_text
        t.config(state="normal"); t.delete("1.0", "end")
        t.insert("end", "\n\n")
        t.insert("end", "  Configure assumptions on the left,\n", "sub")
        t.insert("end", "  add comparable properties, then press\n", "sub")
        t.insert("end", "  Run Simulation.\n\n", "sub")
        t.insert("end", "  Three tabs will populate:\n\n", "sub")
        for item in ["Summary  -  NPV, IRR, $/sqft, verdict",
                     "Charts   -  Wealth growth & monthly costs",
                     "Comps    -  Benchmark vs. comparable properties"]:
            t.insert("end", f"   -  {item}\n", "sub")
        t.config(state="disabled")

    def _run(self):
        try:
            numeric_keys = [k for k in self.entries if k != "location"]
            p = {}
            for k in numeric_keys:
                p[k] = float(self.entries[k].get().replace(",", ""))
            p["location"] = self.entries["location"].get().strip()
        except ValueError:
            messagebox.showerror("Input Error", "All numeric fields must contain numbers.")
            return
        if p["hold_years"] < 1 or p["hold_years"] > 40:
            messagebox.showerror("Input Error", "Holding period must be 1-40 years.")
            return
        if p["sqft"] <= 0:
            messagebox.showerror("Input Error", "Square footage must be greater than 0.")
            return

        r = run_simulation(p)
        comps = self._get_comps()
        comp_analysis = analyse_comps(comps, p["home_price"], p["sqft"], p["monthly_rent"])

        self._display(r, p, comp_analysis, comps)
        self._draw_charts(r, p)
        self._draw_comps_chart(r, p, comp_analysis)
        self.notebook.select(0)

    # ── Summary text ────────────────────────
    def _display(self, r, p, comp_analysis, comps=None):
        t = self.result_text
        t.config(state="normal"); t.delete("1.0", "end")

        def line(text="", tag=None):
            t.insert("end", text + "\n", tag)
        def kv(label, value, tag=None):
            t.insert("end", f"  {label:<34}{value}\n", tag)

        sep = "-" * 56
        winner = r["advantage"]
        color  = "green" if winner == "BUY" else "orange"
        loc    = p.get("location", "")
        loc_str = f" in {loc}" if loc else ""

        line()
        line(f"  VERDICT: {winner} wins by {fmt_usd(r['advantage_amount'])}", color)
        line(f"     over a {r['hold_years']}-year horizon{loc_str}", "sub")
        line(); line(sep, "sub"); line()

        line("  SUBJECT PROPERTY", "header"); line()
        if loc:
            kv("Location", loc)
        kv("Price",                 fmt_usd(p["home_price"]))
        kv("Square Footage",        f"{p['sqft']:,.0f} sqft")
        kv("Price / Sq Ft",         fmt_usd2(r["price_per_sqft"]))
        kv("Rent / Sq Ft",          fmt_usd2(r["rent_per_sqft"]))
        if p["monthly_rent"] > 0 and p["home_price"] > 0:
            gr = (p["monthly_rent"] * 12) / p["home_price"] * 100
            kv("Gross Rent Yield",   f"{gr:.2f}%")
        line(); line(sep, "sub"); line()

        line("  BUY SCENARIO", "header"); line()
        kv("Down Payment",          fmt_usd(r["down_payment"]))
        kv("Loan Amount",           fmt_usd(r["loan_amount"]))
        kv("Monthly Mortgage Pmt",  fmt_usd(r["monthly_pmt"]))
        line()
        kv("Total Interest Paid",   fmt_usd(r["total_interest"]),  "red")
        kv("Total Property Tax",    fmt_usd(r["total_prop_tax"]))
        kv("Total Insurance",       fmt_usd(r["total_insurance"]))
        kv("Total Maintenance",     fmt_usd(r["total_maint"]))
        kv("Total Buy Outflows",    fmt_usd(r["total_buy_outflows"]), "red")
        line()
        kv("Future Home Value",     fmt_usd(r["future_home_value"]), "green")
        kv("Future $/Sq Ft",        fmt_usd2(r["future_price_sqft"]))
        kv("Remaining Mortgage",    fmt_usd(r["remaining_balance"]))
        kv("Selling Costs",         fmt_usd(r["closing_sell_cost"]))
        kv("Net Sale Proceeds",     fmt_usd(r["net_sale_proceeds"]),  "green")
        line()
        kv("NPV  (buy cash flows)", fmt_usd(r["buy_npv"]),
           "green" if r["buy_npv"] > 0 else "red")
        kv("IRR  (annualised)",     fmt_pct(r["buy_irr"]),
           "green" if r["buy_irr"] and r["buy_irr"] > 0 else "red")
        kv("Buyer Terminal Wealth", fmt_usd(r["buyer_net_wealth"]), "bold")
        line(); line(sep, "sub"); line()

        line("  RENT SCENARIO", "header"); line()
        kv("Starting Monthly Rent",    fmt_usd(p["monthly_rent"]))
        kv("Total Rent Paid",          fmt_usd(r["total_rent_paid"]),   "red")
        kv("Total Rent Outflows",      fmt_usd(r["total_rent_outflows"]), "red")
        line()
        capital = r["down_payment"] + p["home_price"] * p["closing_buy"] / 100
        kv("Capital Invested Instead", fmt_usd(capital))
        kv(f"Portfolio @ {p['invest_return']:.1f}% Return",
           fmt_usd(r["renter_terminal"]), "green")
        line()
        kv("NPV  (rent cash flows)",   fmt_usd(r["rent_npv"]))
        kv("NPV  (incl. investment)",  fmt_usd(r["rent_npv_with_invest"]),
           "green" if r["rent_npv_with_invest"] > 0 else "red")
        kv("IRR  (invested capital)",   fmt_pct(r["rent_irr"]),
           "green" if r["rent_irr"] and r["rent_irr"] > 0 else "red")
        kv("Renter Terminal Wealth",    fmt_usd(r["renter_net_wealth"]), "bold")
        line(); line(sep, "sub"); line()

        line("  OPPORTUNITY COST ANALYSIS", "header"); line()
        opp = r["renter_terminal"] - r["buyer_net_wealth"]
        if opp > 0:
            kv("Cost of Buying vs. Renting", fmt_usd(abs(opp)), "red")
            line()
            line("  By buying, you forgo investing your down payment", "sub")
            line(f"  and monthly savings at {p['invest_return']:.1f}%. The renter's", "sub")
            line(f"  portfolio would exceed your home equity by", "sub")
            line(f"  {fmt_usd(abs(opp))} after {r['hold_years']} years.", "sub")
        else:
            kv("Benefit of Buying vs. Renting", fmt_usd(abs(opp)), "green")
            line()
            line("  Home equity growth and the mortgage interest", "sub")
            line("  tax shield outpace what a renter could earn", "sub")
            line(f"  investing at {p['invest_return']:.1f}% over {r['hold_years']} years.", "sub")

        if comp_analysis:
            ca = comp_analysis
            line(); line(sep, "sub"); line()
            line("  COMPARABLE PROPERTIES ANALYSIS", "header"); line()

            if ca["count_price"] > 0:
                kv("Price Comps Used",       str(ca["count_price"]))
                kv("Comp Avg $/Sq Ft",       fmt_usd2(ca["avg_price_sqft"]))
                kv("Subject $/Sq Ft",        fmt_usd2(ca["subj_price_sqft"]),
                   "green" if ca["premium_discount"] < 0 else "red")
                kv("Comp Median Price",      fmt_usd(ca["median_price"]))
                kv("Implied Value (by sqft)",fmt_usd(ca["implied_value"]),
                   "green" if ca["implied_value"] > p["home_price"] else "orange")
                line()
                if ca["premium_discount"] > 0:
                    kv("Subject Trades At",  f"{ca['premium_discount']:.1f}% PREMIUM", "red")
                    line("  Subject is priced above the comp average on a", "sub")
                    line("  per-sqft basis. Negotiate or verify upgrades.", "sub")
                else:
                    kv("Subject Trades At",  f"{abs(ca['premium_discount']):.1f}% DISCOUNT", "green")
                    line("  Subject is priced below the comp average on a", "sub")
                    line("  per-sqft basis. This may indicate good value.", "sub")

            if ca["count_rent"] > 0:
                line()
                kv("Rent Comps Used",        str(ca["count_rent"]))
                kv("Comp Avg Rent/Sq Ft",    fmt_usd2(ca["avg_rent_sqft"]))
                kv("Subject Rent/Sq Ft",     fmt_usd2(ca["subj_rent_sqft"]))
            if ca["avg_cap_rate"] > 0:
                kv("Comp Avg Cap Rate",      f"{ca['avg_cap_rate'] * 100:.2f}%")
                kv("Subject Cap Rate",       f"{ca['subj_cap_rate'] * 100:.2f}%",
                   "green" if ca["subj_cap_rate"] >= ca["avg_cap_rate"] else "orange")

            # Per-comp detail table
            line()
            line("  COMP DETAIL", "orange")
            line(f"  {'Name':<18}{'Price':>10}{'SqFt':>8}{'$/sf':>9}{'Rent':>9}", "sub")
            line(f"  {'-'*54}", "sub")
            for c in comps:
                pr = fmt_usd(c['price']) if c['price'] > 0 else "-"
                sf = f"{c['sqft']:,.0f}" if c['sqft'] > 0 else "-"
                ps = fmt_usd2(c['price']/c['sqft']) if c['price'] > 0 and c['sqft'] > 0 else "-"
                rn = fmt_usd(c['rent']) if c['rent'] > 0 else "-"
                line(f"  {c['name'][:18]:<18}{pr:>10}{sf:>8}{ps:>9}{rn:>9}", "sub")
            line(f"  {'-'*54}", "sub")
            line(f"  {'SUBJECT':<18}{fmt_usd(p['home_price']):>10}"
                 f"{p['sqft']:>8,.0f}{fmt_usd2(r['price_per_sqft']):>9}"
                 f"{fmt_usd(p['monthly_rent']):>9}", "green")

        line(); line(sep, "sub"); line()
        line("  HOW TO READ THESE NUMBERS", "header"); line()
        line("  NPV / IRR", "orange")
        line(f"  NPV discounts cash flows at {p['discount_rate']:.1f}%. IRR is the", "sub")
        line("  break-even return. If IRR > hurdle, value is created.", "sub")
        line()
        line("  $/Sq Ft & Comps", "orange")
        line("  Benchmarks your price against nearby transactions.", "sub")
        line("  A premium means you're paying more per sqft than", "sub")
        line("  the market average; a discount means less.", "sub")
        line()
        line("  Cap Rate (Gross Rent Yield)", "orange")
        line("  Annual rent / price. Higher = better income return.", "sub")
        line("  Useful for comparing the rent-vs-own economics", "sub")
        line("  across properties in the same market.", "sub")
        line()

        t.config(state="disabled"); t.see("1.0")

    # ── Wealth & cost charts ────────────────
    def _draw_charts(self, r, p):
        for w in self.chart_frame.winfo_children():
            w.destroy()

        hold   = int(r["hold_years"])
        months = r["months"]

        fig = Figure(figsize=(8, 7.5), dpi=100, facecolor=CHART_FACE)
        fig.subplots_adjust(hspace=0.48, top=0.94, bottom=0.07, left=0.13, right=0.95)

        ax1 = fig.add_subplot(2, 1, 1)
        ax1.set_facecolor(CHART_BG)
        year_axis = np.arange(0, months + 1) / 12

        ax1.plot(year_axis, [v / 1000 for v in r["buyer_equity_ts"]],
                 color=ACCENT, linewidth=2.2, label="Buyer: Home Equity")
        ax1.plot(year_axis, [v / 1000 for v in r["portfolio_ts"]],
                 color=GREEN, linewidth=2.2, label="Renter: Portfolio")
        ax1.plot(year_axis, [v / 1000 for v in r["home_value_ts"]],
                 color=ORANGE, linewidth=1.2, linestyle="--", alpha=0.5,
                 label="Home Market Value")

        ax1.annotate(f'{fmt_usd(r["buyer_net_wealth"])}',
                     xy=(hold, r["buyer_equity_ts"][-1] / 1000),
                     fontsize=9, color=ACCENT, fontweight="bold",
                     xytext=(8, 0), textcoords="offset points", va="center")
        ax1.annotate(f'{fmt_usd(r["renter_terminal"])}',
                     xy=(hold, r["portfolio_ts"][-1] / 1000),
                     fontsize=9, color=GREEN, fontweight="bold",
                     xytext=(8, 0), textcoords="offset points", va="center")

        ax1.set_title("Wealth Accumulation Over Time", color=TEXT,
                      fontsize=13, fontweight="bold", pad=10)
        ax1.set_xlabel("Year", color=SUBTEXT, fontsize=10)
        ax1.set_ylabel("Value ($K)", color=SUBTEXT, fontsize=10)
        ax1.legend(loc="upper left", fontsize=9, facecolor=CARD,
                   edgecolor="#44446a", labelcolor=TEXT)
        ax1.tick_params(colors=SUBTEXT, labelsize=9)
        ax1.grid(True, alpha=0.15, color=TEXT)
        for sp in ax1.spines.values(): sp.set_color("#44446a")

        ax2 = fig.add_subplot(2, 1, 2)
        ax2.set_facecolor(CHART_BG)
        years = np.arange(1, hold + 1)
        w = 0.35
        ax2.bar(years - w / 2, r["buy_yearly_avg"],  w,
                color=ACCENT, alpha=0.85, label="Buy: Avg Monthly Cost")
        ax2.bar(years + w / 2, r["rent_yearly_avg"], w,
                color=GREEN, alpha=0.85, label="Rent: Avg Monthly Cost")
        ax2.set_title("Average Monthly Cost by Year", color=TEXT,
                      fontsize=13, fontweight="bold", pad=10)
        ax2.set_xlabel("Year", color=SUBTEXT, fontsize=10)
        ax2.set_ylabel("Monthly Cost ($)", color=SUBTEXT, fontsize=10)
        ax2.legend(loc="upper left", fontsize=9, facecolor=CARD,
                   edgecolor="#44446a", labelcolor=TEXT)
        ax2.tick_params(colors=SUBTEXT, labelsize=9)
        ax2.set_xticks(years)
        ax2.grid(True, axis="y", alpha=0.15, color=TEXT)
        for sp in ax2.spines.values(): sp.set_color("#44446a")

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ── Comps chart ─────────────────────────
    def _draw_comps_chart(self, r, p, comp_analysis):
        for w in self.comps_chart_frame.winfo_children():
            w.destroy()

        if not comp_analysis:
            lbl = tk.Label(self.comps_chart_frame,
                           text="\n\n  No usable comps entered.\n\n"
                           "  Each comp needs a Name plus at least\n"
                           "  Price + Sq Ft (for $/sqft chart) or\n"
                           "  Rent + Price (for cap rate chart).\n\n"
                           "  Fill in the table on the left and re-run.",
                           font=self.label_font, bg=CHART_FACE, fg=SUBTEXT,
                           justify="left", anchor="nw")
            lbl.pack(fill="both", expand=True, padx=20, pady=20)
            return

        ca = comp_analysis
        has_price_chart = ca["count_price"] > 0
        has_cap_chart   = len(ca["cap_comps"]) > 0 and p["monthly_rent"] > 0
        num_plots = (1 if has_price_chart else 0) + (1 if has_cap_chart else 0)

        if num_plots == 0:
            lbl = tk.Label(self.comps_chart_frame,
                           text="\n\n  Comps found but need more data for charts.\n\n"
                           "  For $/sqft chart: enter Price + Sq Ft\n"
                           "  For cap rate chart: enter Rent + Price",
                           font=self.label_font, bg=CHART_FACE, fg=SUBTEXT,
                           justify="left", anchor="nw")
            lbl.pack(fill="both", expand=True, padx=20, pady=20)
            return

        fig = Figure(figsize=(8, 7.5), dpi=100, facecolor=CHART_FACE)
        fig.subplots_adjust(hspace=0.55, top=0.94, bottom=0.08, left=0.18, right=0.90)

        plot_idx = 1

        # ── $/sqft chart ───────────────────
        if has_price_chart:
            ax1 = fig.add_subplot(num_plots, 1, plot_idx); plot_idx += 1
            ax1.set_facecolor(CHART_BG)

            names = [c["name"][:20] for c in ca["price_comps"]] + ["SUBJECT"]
            vals  = ca["prices_sqft"] + [ca["subj_price_sqft"]]
            colors = [ACCENT] * len(ca["price_comps"])
            colors += [GREEN if ca["premium_discount"] <= 0 else RED]
            y_pos = np.arange(len(names))

            ax1.barh(y_pos, vals, color=colors, alpha=0.85, height=0.55)
            ax1.axvline(ca["avg_price_sqft"], color=ORANGE, linestyle="--",
                        linewidth=1.5, alpha=0.8,
                        label=f"Comp Avg: {fmt_usd2(ca['avg_price_sqft'])}/sqft")

            for i, v in enumerate(vals):
                ax1.text(v + max(vals) * 0.02, i, fmt_usd2(v),
                         va="center", fontsize=9, color=TEXT)

            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(names, fontsize=9)
            ax1.set_title("Price per Square Foot Comparison", color=TEXT,
                          fontsize=13, fontweight="bold", pad=10)
            ax1.set_xlabel("$/Sq Ft", color=SUBTEXT, fontsize=10)
            ax1.legend(loc="lower right", fontsize=9, facecolor=CARD,
                       edgecolor="#44446a", labelcolor=TEXT)
            ax1.tick_params(colors=SUBTEXT, labelsize=9)
            ax1.grid(True, axis="x", alpha=0.15, color=TEXT)
            for sp in ax1.spines.values(): sp.set_color("#44446a")

        # ── Cap rate chart ─────────────────
        if has_cap_chart:
            ax2 = fig.add_subplot(num_plots, 1, plot_idx); plot_idx += 1
            ax2.set_facecolor(CHART_BG)

            cr_names  = [c["name"][:20] for c in ca["cap_comps"]] + ["SUBJECT"]
            cr_vals   = [(c["rent"] * 12 / c["price"]) * 100 for c in ca["cap_comps"]]
            cr_vals  += [ca["subj_cap_rate"] * 100]
            cr_colors = [ACCENT] * len(ca["cap_comps"])
            cr_colors += [GREEN if ca["subj_cap_rate"] >= ca["avg_cap_rate"] else ORANGE]
            y_pos2 = np.arange(len(cr_names))

            ax2.barh(y_pos2, cr_vals, color=cr_colors, alpha=0.85, height=0.55)
            ax2.axvline(ca["avg_cap_rate"] * 100, color=ORANGE, linestyle="--",
                        linewidth=1.5, alpha=0.8,
                        label=f"Comp Avg: {ca['avg_cap_rate'] * 100:.2f}%")

            for i, v in enumerate(cr_vals):
                ax2.text(v + max(cr_vals) * 0.02, i, f"{v:.2f}%",
                         va="center", fontsize=9, color=TEXT)

            ax2.set_yticks(y_pos2)
            ax2.set_yticklabels(cr_names, fontsize=9)
            ax2.set_title("Gross Rent Yield (Cap Rate) Comparison", color=TEXT,
                          fontsize=13, fontweight="bold", pad=10)
            ax2.set_xlabel("Cap Rate (%)", color=SUBTEXT, fontsize=10)
            ax2.legend(loc="lower right", fontsize=9, facecolor=CARD,
                       edgecolor="#44446a", labelcolor=TEXT)
            ax2.tick_params(colors=SUBTEXT, labelsize=9)
            ax2.grid(True, axis="x", alpha=0.15, color=TEXT)
            for sp in ax2.spines.values(): sp.set_color("#44446a")

        canvas = FigureCanvasTkAgg(fig, master=self.comps_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()