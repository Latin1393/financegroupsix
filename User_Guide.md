# Rent vs. Buy Simulator — User Guide

**Fisher College of Business — The Ohio State University**

This guide explains every part of the simulator: what to enter, what the results mean, and how to read the charts. Written for people who are not finance majors.

---

## Table of Contents

1. [Overview: What This Tool Does](#1-overview-what-this-tool-does)
2. [The Layout](#2-the-layout)
3. [Entering Your Data (Input Cards)](#3-entering-your-data-input-cards)
4. [Dashboard Tab — The Quick Answer](#4-dashboard-tab--the-quick-answer)
5. [Sensitivity Tab — What-If Scenarios](#5-sensitivity-tab--what-if-scenarios)
6. [Detail Tab — The Full Breakdown](#6-detail-tab--the-full-breakdown)
7. [How to Read Each Chart](#7-how-to-read-each-chart)
8. [Example Scenario Walkthrough](#8-example-scenario-walkthrough)
9. [Glossary of Financial Terms](#9-glossary-of-financial-terms)
10. [References & Further Reading](#10-references--further-reading)

---

## 1. Overview: What This Tool Does

The simulator compares two paths over a set number of years:

**Path A — BUY:** You put down a down payment, take out a mortgage, pay property taxes, insurance, and maintenance. At the end, you sell the home and keep whatever's left after paying off the mortgage and selling costs.

**Path B — RENT:** You pay monthly rent (which increases each year). The money you *would have* spent on a down payment gets invested in the stock market instead. At the end, you have whatever that investment portfolio grew to.

The tool calculates which path leaves you with **more money** at the end and tells you **exactly why**, using both plain English and MBA-level financial metrics.

---

## 2. The Layout

The window is split into two sections with a **draggable divider** between them:

```
┌─────────────────────────────────────────────────────┐
│  THE OHIO STATE UNIVERSITY                          │  ← Scarlet header bar
│  Fisher College of Business                         │
├─────────────────────────────────────────────────────┤
│ [Subject] [Lifestyle] [Purchase] [Renting] [Analysis] [RUN] │  ← Input cards
│  Property   & Budget                                │     (scroll left/right)
│                                                     │
├═══════════════════ drag to resize ═══════════════════┤  ← Drag this bar
│                                                     │
│  ┌──────────┐ ┌─────────────┐ ┌──────────┐         │
│  │Dashboard │ │ Sensitivity │ │  Detail  │         │  ← Three result tabs
│  └──────────┘ └─────────────┘ └──────────┘         │
│                                                     │
│  (charts, verdict, analysis appear here)            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Tip:** If the input cards are covering the results, grab the gray divider bar between them and drag it **upward** to give the results area more room.

---

## 3. Entering Your Data (Input Cards)

The top row contains five cards. Scroll left/right if they extend beyond your screen. Here's what each field means and where to find the numbers:

### Subject Property

| Field | What to Enter | Where to Find It |
|-------|--------------|-------------------|
| **Home Price ($)** | The asking price or your offer price | Zillow, Redfin, Realtor.com, your agent |
| **Square Footage** | Total living area in sq ft | The listing page for the property |
| **Location** | Neighborhood, city, or address | Just a label — doesn't affect calculations |

### Lifestyle & Budget

| Field | What to Enter | Where to Find It |
|-------|--------------|-------------------|
| **Gross Salary ($/yr)** | Your annual income before taxes | Your offer letter or pay stub (gross pay × pay periods) |
| **State Tax (%)** | Your state income tax rate | Google "[your state] income tax rate" — Ohio is ~3.5–4% |
| **Other Debt ($/mo)** | Car payment + student loans + minimum credit card payments | Add up your monthly statements |
| **Savings Goal ($/mo)** | How much you want to save each month beyond housing | Your personal target — $500 is a common starting point |
| **Emergency Fund ($)** | Cash you have saved for emergencies right now | Check your savings account balance |

### Purchase

| Field | What to Enter | Typical Range |
|-------|--------------|---------------|
| **Down Payment (%)** | Percentage of home price you pay upfront | 3.5%–20%. Use 20% to avoid PMI. |
| **Mortgage Rate (%)** | Annual interest rate on your loan | Check bankrate.com or your lender's quote. Currently ~6–7%. |
| **Loan Term (yrs)** | Length of your mortgage | 30 (most common) or 15 |
| **Property Tax (%/yr)** | Annual property tax as % of home value | Google "[your county] property tax rate". Ohio avg ~1.6%. |
| **Home Ins. ($/yr)** | Annual homeowner's insurance premium | $1,200–$2,400 is typical. Get a quote from your insurer. |
| **Maintenance (%/yr)** | Annual repair/upkeep costs as % of home value | 1% is the standard rule of thumb. |
| **Appreciation (%/yr)** | How fast the home's value grows each year | 3% is the U.S. historical average (Case-Shiller Index). |
| **Close Cost Buy (%)** | Buyer's closing costs as % of price | 2%–5% is typical. 3% is a safe estimate. |
| **Close Cost Sell (%)** | Selling costs (agent commission + fees) | 5%–6% is standard (agent takes ~5%, plus fees). |

### Renting

| Field | What to Enter | Where to Find It |
|-------|--------------|-------------------|
| **Monthly Rent ($)** | What you'd pay in rent per month | Apartments.com, Zillow rentals, Craigslist |
| **Rent Increase (%/yr)** | How much rent goes up each year | 3% is the national average. Check your local market. |
| **Renter Ins. ($/yr)** | Annual renter's insurance premium | $150–$300 is typical. |

### Analysis

| Field | What to Enter | What It Means |
|-------|--------------|---------------|
| **Hold Period (yrs)** | How many years you plan to live there | This is the most important input. Be realistic. |
| **Alt. Return (%/yr)** | What you'd earn investing in stocks instead | 8% is the S&P 500 historical average after inflation adjustments. |
| **Discount Rate (%/yr)** | Your personal "hurdle rate" for investments | 7% is common in finance. This is the minimum return you'd accept. |
| **Marginal Tax (%)** | Your top federal income tax bracket | Check IRS brackets. $45K–$95K income = 22%. $95K–$190K = 24%. |

### After Entering Data

Click the red **RUN SIMULATION** button on the far right of the input row.

---

## 4. Dashboard Tab — The Quick Answer

This is the first tab that appears after you run the simulation. It's designed to give you the answer in 5 seconds.

### The Verdict Banner

At the very top, you'll see a large banner:

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  YOU SHOULD BUY.                              Breakeven  Yr 5│
│  You'll have $47,832 MORE than if you rented. B/E Rent $2,341│
│                                               Cash     $92,000│
│  Your home grows from $400,000 to $491,918    Buy IRR   6.82%│
│  in 7 years. After selling costs, you pocket                 │
│  $196,542. A renter investing the same capital               │
│  would only reach $148,710.                                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**How to read it:**
- The **big text** tells you what to do: BUY or RENT
- The **dollar amount** is how much richer you'll be compared to the other option
- The **paragraph below** explains the exact math in plain English
- The **numbers on the right** are key metrics (explained below)

### Key Metrics on the Right

| Metric | What It Tells You |
|--------|-------------------|
| **Breakeven** | The year when buying starts winning. If it says "Year 5" and you plan to hold 7 years, you're good — you pass the breakeven. If it says "Never", buying never catches up. |
| **Break-Even Rent** | The monthly rent that would make renting and buying exactly equal. If your actual rent is lower than this number, renting wins. If your rent is higher, buying wins. |
| **Cash to Buy** | Total cash you need on closing day: down payment + closing costs. This is the check you write. |
| **Buy IRR** | Your annual return on the buying investment. Compare this to your discount rate. Higher = better. |

### The Three Charts

Below the verdict banner, you'll see three charts side by side:

**Chart 1 (Left) — "Where Your Money Goes"**
A donut chart breaking down your monthly ownership cost. Each slice shows what percentage goes to mortgage principal, interest, property tax, insurance, and maintenance. The title shows the total monthly cost.

**Chart 2 (Center) — "Wealth Over Time"**
Two lines tracking your wealth year by year:
- **Scarlet line (Buy: Equity)** = your home equity (home value minus remaining mortgage)
- **Gray line (Rent: Portfolio)** = your investment portfolio if you rented instead
- The line that ends **higher** is the winner
- A dotted vertical line marks the **breakeven year** (where the lines cross)
- The dollar amounts are labeled at the end of each line

**Chart 3 (Right) — "Avg Monthly Cost by Year"**
Grouped bars comparing what you pay each month:
- **Scarlet bars** = average monthly cost of owning
- **Gray bars** = average monthly cost of renting
- Notice how rent bars grow each year (rent increases) while buy bars stay more stable (fixed mortgage)

### The Affordability Strip

A row of boxes at the bottom with color-coded metrics:

| Box | Green Means | Red Means |
|-----|-------------|-----------|
| **Take-Home** | Your monthly income after taxes | (always shown, no color judgment) |
| **Buy Cost** | Your monthly ownership cost | (always shown in scarlet) |
| **Rent Cost** | Your monthly rent cost | (always shown in gray) |
| **Buy DTI** | Your debt-to-income ratio is under 36% — you qualify | Over 36% — lenders may reject you |
| **Buy Leftover** | You have money left after all bills | You're living paycheck to paycheck |
| **Emergency** | 3+ months of reserves — you're safe | Under 3 months — you need more savings |

Each box includes a one-line explanation underneath the number.

---

## 5. Sensitivity Tab — What-If Scenarios

This tab answers every "but what if...?" question automatically. It reruns the simulation hundreds of times with different assumptions.

### Chart 1 (Left) — The Heatmap

A grid showing how the verdict changes based on two variables:
- **X-axis (horizontal):** Hold period from 1 to 15 years
- **Y-axis (vertical):** Home appreciation rate from 0% to 6%
- **Each cell** shows the dollar advantage of buying (in thousands)
- **Green cells** = buying wins by that amount
- **Red cells** = renting wins by that amount
- **Your current scenario** is outlined with a scarlet border

```
Example reading: The cell at "7 years, 3%" shows "+$48K"
→ That means: if you hold 7 years and appreciation is 3%, 
  buying beats renting by $48,000.
```

### Chart 2 (Center) — Advantage by Hold Period

A line chart showing the buy advantage across 1–20 years:
- **Above zero (green shading)** = buying wins
- **Below zero (red shading)** = renting wins
- The breakeven year is marked with a green dashed line
- This answers: "How long do I need to stay for buying to make sense?"

### Chart 3 (Right) — Advantage by Mortgage Rate

Bar chart showing how the verdict changes at different interest rates (4%–8.5%):
- **Green bars** = buying wins at that rate
- **Red bars** = renting wins at that rate
- **Your current rate** has a scarlet outline
- This answers: "What if rates go up/down before I lock in?"

---

## 6. Detail Tab — The Full Breakdown

A scrollable text report with every number, organized into sections:

### Sections in Order

1. **The Bottom Line** — The verdict in plain English with a step-by-step explanation of the math
2. **Key Numbers You Need to Know** — Breakeven year, break-even rent, and cash needed, each with an interpretation
3. **Can You Actually Afford This?** — Income, taxes, DTI checks, leftover cash, emergency fund analysis with PASS/FAIL ratings
4. **Full Buy Breakdown** — Every cost itemized: down payment, monthly payment, total interest, total taxes, future home value, net proceeds from sale, NPV, IRR
5. **Full Rent Breakdown** — Starting rent, rent in the final year, total rent paid, investment portfolio value, NPV, IRR
6. **Opportunity Cost** — Exactly how much you gain or lose by choosing one path over the other
7. **Glossary** — Every financial term defined in plain English

### Color Coding in the Detail Tab

| Color | Meaning |
|-------|---------|
| **Scarlet** | Section headers |
| **Green** | Good numbers — you're in good shape |
| **Red** | Warning — this number is a concern |
| **Orange** | Caution — not a dealbreaker but worth noting |
| **Gray** | Explanatory text |

---

## 7. How to Read Each Chart

### Donut Chart (Dashboard, left)

```
         ┌──────────┐
        ╱    37%     ╲        37% = Interest (biggest slice)
       │   Interest   │       28% = Principal (goes to equity)
       │              │       15% = Property Tax
        ╲    28%     ╱        12% = Insurance
         │ Principal │         8% = Maintenance
         └──────────┘
         Total: $2,847/mo
```

**What to look for:** The interest slice will be the largest in early years. This is money going to the bank, not building equity. The principal slice is the portion that actually builds your ownership stake.

### Wealth Over Time (Dashboard, center)

```
    $250K ┤
          │                          ╱ Buy: $196K ← you keep this
    $200K ┤                       ╱╱
          │                    ╱╱╱
    $150K ┤                ╱╱╱     ╱ Rent: $149K
          │            ╱╱╱     ╱╱╱
    $100K ┤        ╱╱╱     ╱╱╱
          │    ╱╱╱     ╱╱╱
     $50K ┤╱╱╱   ╱╱╱╱
          │  ╱╱╱╱
       $0 ┼───┬───┬───┬───┬───┬───┬───
          0   1   2   3   4   5   6   7  ← Years
                      ↑
                  Breakeven (year where lines cross)
```

**What to look for:**
- Whichever line ends **higher** is the better financial choice
- The **gap** between the lines at the end is your advantage amount
- The **crossover point** is when buying starts winning
- If the lines never cross, renting always wins under these assumptions

### Monthly Cost Bars (Dashboard, right)

```
    $3,000 ┤
           │  ██        ██        ██        ██
    $2,500 ┤  ██  ░░    ██  ░░    ██  ░░    ██  ░░░
           │  ██  ░░    ██  ░░    ██  ░░░   ██  ░░░
    $2,000 ┤  ██  ░░    ██  ░░    ██  ░░░   ██  ░░░
           │  ██  ░░    ██  ░░    ██  ░░░   ██  ░░░
    $1,500 ┤  ██  ░░    ██  ░░    ██  ░░    ██  ░░
           │
           └──Yr 1──────Yr 3──────Yr 5──────Yr 7──

           ██ = Buy (stays mostly flat — fixed mortgage)
           ░░ = Rent (grows each year — rent increases)
```

**What to look for:** Buying is often more expensive in early years but stays flat. Renting starts cheaper but climbs. The point where the gray bars catch up to the scarlet bars is when renting becomes more expensive month-to-month.

### Sensitivity Heatmap (Sensitivity tab, left)

```
    6% │ -12  -2  +8  +22  +38  +58  +81
    5% │ -18  -8  +3  +15  +30  +48  +68
    4% │ -24  -14  -4  +8  +22  +38  +56
    3% │ -30  -20  -10  +1  +14  +28  +44   ← your scenario [bordered]
    2% │ -36  -26  -16  -6  +6  +18  +32
    1% │ -42  -32  -22  -12  -2  +8  +20
    0% │ -48  -38  -28  -18  -8  +2  +12
       └──1────3────5────7────9───11───13── years
```

**What to look for:**
- Find your scenario (scarlet border) — that's your baseline
- Look at the cells around it — how stable is the result?
- If even small changes flip the color, the decision is fragile
- If your cell is deep green with green all around it, buying is robust

---

## 8. Example Scenario Walkthrough

Here's a concrete example using these inputs:

**Inputs:**
- Home price: $400,000 | 1,800 sqft
- Salary: $85,000 | Ohio (4% state tax)
- 20% down ($80,000) | 6.75% mortgage | 30-year term
- Property tax: 1.25% | Insurance: $1,800/yr | Maintenance: 1%
- Appreciation: 3%/yr | Closing: 3% buy, 6% sell
- Rent: $2,000/mo | Rent growth: 3%/yr
- Hold period: 7 years | Alt. return: 8% | Discount rate: 7% | Tax: 24%

**What the tool tells you:**

> **YOU SHOULD BUY.**
> You'll have $47,832 MORE than if you rented.

**Why:**
- Your $400,000 home grows to ~$491,918 in 7 years (at 3% appreciation)
- You pay off some mortgage, leaving ~$285,000 remaining balance
- After 6% selling costs (~$29,515), you keep ~$177,000 in cash
- A renter investing $92,000 (your down payment + closing costs) at 8% would grow it to ~$129,000
- Difference: ~$48,000 in your favor as a buyer

**Breakeven: Year 5**
- If you sold before year 5, renting would have been smarter
- Since you plan to hold 7 years, you're 2 years past breakeven — good position

**Break-even rent: ~$2,341/mo**
- Your actual rent ($2,000) is below this threshold
- If rent were above $2,341, buying would be even more compelling
- This tells you renting at $2,000 is a good deal — buying only wins because of appreciation and forced savings

**Affordability:**
- Monthly take-home: ~$5,100
- Monthly buy cost: ~$2,847 (56% of take-home — high but manageable)
- DTI: 46% — OVER the 36% limit. A lender might push back.
- Leftover after bills: ~$353/mo — tight

**What the sensitivity heatmap shows:**
- At 3% appreciation and 7 years, you're in green (+$48K)
- But at 0% appreciation, you'd need 12+ years to break even
- If rates were 8% instead of 6.75%, the advantage shrinks to ~$20K
- The decision is moderately sensitive to appreciation — it works at 2%+ but fails at 0–1%

---

## 9. Glossary of Financial Terms

| Term | Simple Definition | Why It Matters |
|------|-------------------|----------------|
| **NPV (Net Present Value)** | Future money converted to today's dollars. A dollar next year is worth less than a dollar today because you could invest today's dollar. | Positive NPV = you come out ahead. Negative = you lose value. |
| **IRR (Internal Rate of Return)** | The annual percentage return your money earns in this scenario. Think of it as the "interest rate" of your decision. | Compare to your discount rate. If IRR > discount rate, it's a good investment. |
| **Opportunity Cost** | What you give up by choosing one option. Money in a house can't also be in the stock market. | This is the real cost of buying — not just the mortgage, but the missed investment returns. |
| **Discount Rate** | Your personal minimum acceptable return. The rate you use to judge whether an investment is "worth it." | 7% is standard in corporate finance. Adjust based on your risk tolerance. |
| **DTI (Debt-to-Income)** | Total monthly debt payments ÷ gross monthly income. | Lenders want this under 36%. Over 43% and most won't approve you. |
| **28/36 Rule** | Housing < 28% of gross income; total debt < 36%. | The standard test banks use to decide if you can afford a mortgage. |
| **Appreciation** | How much the home's value increases per year. | 3% is the U.S. long-term average. Some markets are higher, some lower. |
| **Equity** | Home value minus remaining mortgage. The part of the home you actually own. | This is what you keep when you sell (minus selling costs). |
| **Breakeven Year** | The first year when buying becomes cheaper than renting over the full period. | If you plan to sell before this year, renting is mathematically better. |
| **Break-Even Rent** | The monthly rent that makes renting and buying produce identical outcomes. | Below this = renting wins. Above this = buying wins. |
| **PMI** | Private mortgage insurance, required if down payment < 20%. | Not modeled in this tool. If you're putting less than 20% down, your actual costs will be higher. |
| **Cap Rate** | Annual rent ÷ property price. Measures rental income as a % of value. | Not used in this version but common in real estate investment analysis. |

---

## 10. References & Further Reading

### Data Sources for Your Inputs

- **Home prices:** Zillow (zillow.com), Redfin (redfin.com), Realtor.com
- **Mortgage rates:** Bankrate (bankrate.com), Freddie Mac Weekly Survey (freddiemac.com/pmms)
- **Rental prices:** Apartments.com, Zillow Rentals, Rent.com
- **Property tax rates:** Your county auditor's website (search "[county name] property tax rate")
- **State tax rates:** Tax Foundation (taxfoundation.org/state-individual-income-tax-rates)
- **Historical home appreciation:** S&P/Case-Shiller Home Price Index — averaged ~3.4%/yr nationally since 1987
- **Historical stock returns:** S&P 500 long-term average ~10% nominal, ~7% inflation-adjusted

### Academic References

- Beracha, E., & Johnson, K. H. (2012). "Lessons from Over 30 Years of Buy versus Rent Decisions." *Real Estate Economics*, 40(2), 217–247. — Foundational study showing rent-vs-buy outcomes depend heavily on holding period and local appreciation rates.

- Gallin, J. (2008). "The Long-Run Relationship Between House Prices and Rents." *Real Estate Economics*, 36(4), 635–658. — Demonstrates that price-to-rent ratios mean-revert over time, supporting the use of comparative analysis.

- Goodman, L. S., & Mayer, C. (2018). "Homeownership and the American Dream." *Journal of Economic Perspectives*, 32(1), 31–58. — Discusses the financial and non-financial dimensions of the rent-vs-buy decision.

- Sinai, T., & Souleles, N. S. (2005). "Owner-Occupied Housing as a Hedge Against Rent Risk." *The Quarterly Journal of Economics*, 120(2), 763–789. — Argues that buying provides insurance against future rent increases, a key factor modeled in this tool.

### Concepts Used in This Tool

- **Net Present Value (NPV):** Brealey, R., Myers, S., & Allen, F. *Principles of Corporate Finance* (14th ed.). McGraw-Hill. — Chapter 2: How to Calculate Present Values.

- **Internal Rate of Return (IRR):** Same text, Chapter 5: Net Present Value and Other Investment Criteria.

- **Opportunity Cost:** Mankiw, N. G. *Principles of Economics* (9th ed.). Cengage. — Chapter 1: Ten Principles of Economics.

---

*This tool was built as a class project for the Fisher College of Business MBA Finance curriculum at The Ohio State University.*
