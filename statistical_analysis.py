"""
statistical_analysis.py
Statistical analysis + data storytelling insights.
Outputs a text report and a summary CSV.
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
import os

DB_PATH  = "/home/claude/analytics_dashboard/data/sales.db"
OUT_PATH = "/home/claude/analytics_dashboard/reports/Statistical_Insights.txt"
CSV_PATH = "/home/claude/analytics_dashboard/reports/Monthly_Stats.csv"

def run():
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()

    df["date"] = pd.to_datetime(df["date"])
    lines = ["="*62, "  DATA ANALYTICS DASHBOARD — STATISTICAL INSIGHTS REPORT",
             "="*62, ""]

    # ── 1. Summary Stats ─────────────────────────────────────────────────────
    lines += ["── 1. OVERALL KPIs ─────────────────────────────────────────",
        f"  Total Orders  : {len(df):,}",
        f"  Total Revenue : ${df['revenue'].sum():,.2f}",
        f"  Total Profit  : ${df['profit'].sum():,.2f}",
        f"  Avg Margin    : {df['margin_pct'].mean():.2f}%",
        f"  Units Sold    : {df['quantity'].sum():,}",
        f"  Avg Order Val : ${df['revenue'].mean():.2f}", ""]

    # ── 2. YoY Growth ────────────────────────────────────────────────────────
    rev23 = df[df["year"]==2023]["revenue"].sum()
    rev24 = df[df["year"]==2024]["revenue"].sum()
    yoy   = (rev24-rev23)/rev23*100
    lines += ["── 2. YEAR-OVER-YEAR GROWTH ─────────────────────────────────",
        f"  2023 Revenue  : ${rev23:,.2f}",
        f"  2024 Revenue  : ${rev24:,.2f}",
        f"  YoY Growth    : {yoy:+.2f}%", ""]

    # ── 3. T-test: Online vs In-Store revenue ─────────────────────────────
    online   = df[df["channel"]=="Online"]["revenue"]
    instore  = df[df["channel"]=="In-Store"]["revenue"]
    t, p     = stats.ttest_ind(online, instore)
    lines += ["── 3. T-TEST: ONLINE vs IN-STORE ORDER VALUE ────────────────",
        f"  Online mean   : ${online.mean():.2f}",
        f"  In-Store mean : ${instore.mean():.2f}",
        f"  t-statistic   : {t:.4f}",
        f"  p-value       : {p:.4f}",
        f"  Significant   : {'YES (p < 0.05)' if p < 0.05 else 'NO'}",""]

    # ── 4. Correlation: discount vs margin ───────────────────────────────────
    r, pv = stats.pearsonr(df["discount"], df["margin_pct"])
    lines += ["── 4. CORRELATION: DISCOUNT RATE vs MARGIN % ────────────────",
        f"  Pearson r     : {r:.4f}",
        f"  p-value       : {pv:.4f}",
        f"  Interpretation: {'Strong negative' if r < -0.5 else 'Moderate negative' if r < 0 else 'Positive'} correlation",""]

    # ── 5. Top region / category / rep ───────────────────────────────────────
    top_reg = df.groupby("region")["revenue"].sum().idxmax()
    top_cat = df.groupby("category")["profit"].sum().idxmax()
    top_rep = df.groupby("sales_rep")["revenue"].sum().idxmax()
    lines += ["── 5. TOP PERFORMERS ────────────────────────────────────────",
        f"  Best Region   : {top_reg}  (${df[df['region']==top_reg]['revenue'].sum():,.2f})",
        f"  Best Category : {top_cat}  (${df[df['category']==top_cat]['profit'].sum():,.2f} profit)",
        f"  Top Sales Rep : {top_rep}  (${df[df['sales_rep']==top_rep]['revenue'].sum():,.2f})",""]

    # ── 6. Seasonal analysis ─────────────────────────────────────────────────
    qtr = df.groupby("quarter")["revenue"].mean()
    peak_q = qtr.idxmax()
    lines += ["── 6. SEASONAL PATTERNS ─────────────────────────────────────",
        f"  Peak Quarter  : Q{peak_q}  (avg ${qtr[peak_q]:,.2f}/order)",
        f"  Weakest Qtr   : Q{qtr.idxmin()}  (avg ${qtr.min():,.2f}/order)",""]

    # ── 7. Actionable Insights ───────────────────────────────────────────────
    lines += ["── 7. ACTIONABLE INSIGHTS (for Stakeholders) ────────────────",
        f"  • {top_reg} region drives the most revenue — prioritise marketing spend here.",
        f"  • {top_cat} has the highest profit — consider expanding SKU range.",
        f"  • Discounts show a {abs(r):.2f} correlation with margin erosion; review discount policy.",
        f"  • Q{peak_q} is peak season — pre-load inventory and campaigns by Q{peak_q-1 if peak_q>1 else 4}.",
        f"  • YoY growth of {yoy:+.2f}% suggests {'healthy expansion' if yoy>5 else 'need for growth initiatives'}.",
        ""]
    lines += ["="*62]

    report = "\n".join(lines)
    print(report)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(report)

    # Monthly stats CSV
    monthly = df.groupby(["year","month","month_name"]).agg(
        revenue=("revenue","sum"), profit=("profit","sum"),
        orders=("order_id","count"), units=("quantity","sum"),
        avg_margin=("margin_pct","mean")
    ).round(2).reset_index()
    monthly.to_csv(CSV_PATH, index=False)
    print(f"\nMonthly stats CSV → {CSV_PATH}")
    print(f"Report saved      → {OUT_PATH}")

if __name__ == "__main__":
    run()
