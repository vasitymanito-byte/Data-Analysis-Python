# 📊 Data Analytics Dashboard

> End-to-end data pipeline: Python ETL → SQLite → Excel KPI Reports + Tableau-ready export

## Project Structure
```
analytics_dashboard/
├── data/
│   ├── raw/               # Raw CSV from generator
│   ├── processed/         # Cleaned & enriched CSV
│   └── sales.db           # SQLite database (fact table + 5 views)
├── src/
│   ├── generate_data.py   # Synthetic sales data generator (2,000 rows, 2023–2024)
│   ├── etl_pipeline.py    # Extract → Clean → Transform → Load pipeline
│   ├── generate_reports.py# Multi-sheet Excel workbook + Tableau CSV export
│   └── statistical_analysis.py # Statistical tests & stakeholder insights
├── sql/
│   └── analytics_queries.sql   # 10 KPI queries (monthly, YoY, region, rep, etc.)
├── reports/
│   ├── Sales_Dashboard.xlsx    # 8-tab Excel workbook with charts
│   ├── Tableau_Ready.csv       # Flat enriched export for Tableau
│   ├── Monthly_Stats.csv       # Aggregated monthly summary
│   └── Statistical_Insights.txt# Written insights report
└── requirements.txt
```

## Quick Start
```bash
pip install -r requirements.txt

# 1. Generate raw data
python src/generate_data.py

# 2. Run ETL pipeline (clean + load to SQLite)
python src/etl_pipeline.py

# 3. Export Excel reports + Tableau CSV
python src/generate_reports.py

# 4. Run statistical analysis
python src/statistical_analysis.py
```

## Key Results (2023–2024)
| KPI | Value |
|---|---|
| Total Revenue | $3,133,027 |
| Total Profit | $1,266,571 |
| Avg Margin | 40.30% |
| YoY Growth | +12.62% |
| Top Region | South |
| Top Category | Electronics |
| Peak Season | Q3 |

## Tech Stack
- **Python**: pandas, numpy, scipy, openpyxl
- **SQL**: SQLite with 5 analytical views
- **Excel**: 8-tab workbook with bar/line charts, pivot-style tables
- **Tableau**: Flat enriched CSV ready for drag-and-drop viz
