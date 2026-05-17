"""
generate_data.py — Generates realistic synthetic sales data.
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

REGIONS     = ["North", "South", "East", "West", "Central"]
CATEGORIES  = ["Electronics", "Apparel", "Home & Garden", "Sports", "Food & Beverage"]
CHANNELS    = ["Online", "In-Store", "Partner", "Wholesale"]
REPS        = ["Alice Morgan","Bob Chen","Clara Diaz","David Kim",
                "Eva Patel","Frank Russo","Grace Lee","Henry Osei"]

PRODUCTS = {
    "Electronics":     [("Laptop Pro 15",1200),("Wireless Earbuds",89),("Smart Watch",249),("4K Monitor",599)],
    "Apparel":         [("Running Jacket",85),("Denim Jeans",65),("Yoga Set",55),("Wool Sweater",110)],
    "Home & Garden":   [("Robot Vacuum",299),("Air Purifier",199),("Planter Set",45),("LED Strip Kit",35)],
    "Sports":          [("Foam Roller",30),("Resistance Bands",25),("Gym Bag",70),("Protein Shaker",18)],
    "Food & Beverage": [("Premium Coffee Blend",22),("Protein Bars 12pk",28),("Green Tea Set",18),("Olive Oil 1L",16)],
}

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def generate_sales(n=2000):
    start, end = datetime(2023, 1, 1), datetime(2024, 12, 31)
    rows = []
    for i in range(1, n + 1):
        category            = random.choice(CATEGORIES)
        product, base_price = random.choice(PRODUCTS[category])
        qty                 = random.randint(1, 20)
        discount            = round(random.choice([0,0,0,0.05,0.10,0.15,0.20]), 2)
        unit_price          = round(base_price * (1 - discount), 2)
        revenue             = round(unit_price * qty, 2)
        cost                = round(base_price * 0.55 * qty, 2)
        profit              = round(revenue - cost, 2)
        rows.append({
            "order_id":   f"ORD-{i:05d}",
            "date":       random_date(start, end).strftime("%Y-%m-%d"),
            "region":     random.choice(REGIONS),
            "channel":    random.choice(CHANNELS),
            "sales_rep":  random.choice(REPS),
            "category":   category,
            "product":    product,
            "quantity":   qty,
            "unit_price": unit_price,
            "discount":   discount,
            "revenue":    revenue,
            "cost":       cost,
            "profit":     profit,
        })
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

if __name__ == "__main__":
    df = generate_sales()
    df.to_csv("../data/raw/sales_raw.csv", index=False)
    print(f"Generated {len(df)} rows -> data/raw/sales_raw.csv")
    print(df.head())
