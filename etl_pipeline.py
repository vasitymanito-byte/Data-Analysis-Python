"""
etl_pipeline.py
Extract → Clean → Transform → Load into SQLite database.
"""
import pandas as pd
import numpy as np
import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

RAW_PATH  = "/home/claude/analytics_dashboard/data/raw/sales_raw.csv"
PROC_PATH = "/home/claude/analytics_dashboard/data/processed/sales_clean.csv"
DB_PATH   = "/home/claude/analytics_dashboard/data/sales.db"


# ── EXTRACT ──────────────────────────────────────────────────────────────────
def extract(path=RAW_PATH) -> pd.DataFrame:
    log.info(f"Extracting data from {path}")
    df = pd.read_csv(path, parse_dates=["date"])
    log.info(f"  → {len(df)} rows, {df.shape[1]} columns")
    return df


# ── CLEAN ─────────────────────────────────────────────────────────────────────
def clean(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Cleaning data...")
    original_len = len(df)

    # Drop exact duplicates
    df = df.drop_duplicates()

    # Drop rows missing critical fields
    df = df.dropna(subset=["order_id","date","revenue","profit"])

    # Clip negative quantities / revenues (data quality guard)
    df = df[df["quantity"] > 0]
    df = df[df["revenue"] > 0]

    # Standardise string columns
    for col in ["region","channel","sales_rep","category","product"]:
        df[col] = df[col].str.strip().str.title()

    log.info(f"  → Dropped {original_len - len(df)} bad rows; {len(df)} remain")
    return df.reset_index(drop=True)


# ── TRANSFORM ─────────────────────────────────────────────────────────────────
def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Transforming data...")

    # Date parts
    df["year"]    = df["date"].dt.year
    df["quarter"] = df["date"].dt.quarter
    df["month"]   = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["week"]    = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.day_name()

    # Margin %
    df["margin_pct"] = (df["profit"] / df["revenue"] * 100).round(2)

    # Revenue bands
    df["rev_band"] = pd.cut(
        df["revenue"],
        bins=[0, 100, 500, 2000, 99999],
        labels=["<$100", "$100-$500", "$500-$2k", ">$2k"]
    )

    # YoY flag
    df["is_2024"] = (df["year"] == 2024).astype(int)

    log.info(f"  → Added derived columns; shape now {df.shape}")
    return df


# ── LOAD ──────────────────────────────────────────────────────────────────────
def load(df: pd.DataFrame, db_path=DB_PATH, csv_path=PROC_PATH):
    log.info(f"Loading to SQLite: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Save processed CSV
    df.to_csv(csv_path, index=False)
    log.info(f"  → Processed CSV saved to {csv_path}")

    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    # Main fact table
    df_db = df.copy()
    df_db["date"] = df_db["date"].astype(str)
    df_db["rev_band"] = df_db["rev_band"].astype(str)
    df_db.to_sql("sales", conn, if_exists="replace", index=False)

    # ── Pre-built summary views ───────────────────────────────────────────────
    cur.executescript("""
    DROP VIEW IF EXISTS v_monthly_kpis;
    CREATE VIEW v_monthly_kpis AS
        SELECT year, month, month_name,
               SUM(revenue)              AS total_revenue,
               SUM(profit)               AS total_profit,
               SUM(quantity)             AS units_sold,
               COUNT(DISTINCT order_id)  AS orders,
               ROUND(AVG(margin_pct),2)  AS avg_margin_pct
        FROM sales
        GROUP BY year, month;

    DROP VIEW IF EXISTS v_region_kpis;
    CREATE VIEW v_region_kpis AS
        SELECT region,
               SUM(revenue)  AS total_revenue,
               SUM(profit)   AS total_profit,
               COUNT(*)      AS orders,
               ROUND(AVG(margin_pct),2) AS avg_margin_pct
        FROM sales
        GROUP BY region;

    DROP VIEW IF EXISTS v_category_kpis;
    CREATE VIEW v_category_kpis AS
        SELECT category,
               SUM(revenue)  AS total_revenue,
               SUM(profit)   AS total_profit,
               SUM(quantity) AS units_sold,
               ROUND(AVG(discount)*100,1) AS avg_discount_pct
        FROM sales
        GROUP BY category;

    DROP VIEW IF EXISTS v_rep_kpis;
    CREATE VIEW v_rep_kpis AS
        SELECT sales_rep,
               SUM(revenue)              AS total_revenue,
               SUM(profit)               AS total_profit,
               COUNT(DISTINCT order_id)  AS orders,
               ROUND(AVG(margin_pct),2)  AS avg_margin_pct
        FROM sales
        GROUP BY sales_rep
        ORDER BY total_revenue DESC;

    DROP VIEW IF EXISTS v_channel_kpis;
    CREATE VIEW v_channel_kpis AS
        SELECT channel,
               SUM(revenue)  AS total_revenue,
               SUM(profit)   AS total_profit,
               COUNT(*)      AS orders
        FROM sales
        GROUP BY channel;
    """)

    conn.commit()
    conn.close()
    log.info("  → SQLite DB written with 5 summary views")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def run_pipeline():
    df = extract()
    df = clean(df)
    df = transform(df)
    load(df)
    log.info("Pipeline complete ✓")
    return df

if __name__ == "__main__":
    run_pipeline()
