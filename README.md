# Supply Chain Analytics Dashboard
### End-to-End Inventory & Demand Analysis | Python · SQL · Power BI

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![SQL](https://img.shields.io/badge/SQL-SQLite-green) ![PowerBI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow) ![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## Project Overview

A complete end-to-end supply chain analytics case study built on **180,519 real-world order transactions** from the DataCo Global Supply Chain dataset (2015–2018). This project demonstrates the full analytical workflow of a supply chain analyst — from raw data cleaning to demand forecasting, inventory optimization, and interactive Power BI dashboards.

---

## Key Findings

| Metric | Value |
|--------|-------|
| Total Revenue Analyzed | $33,054,402 |
| Unique SKUs | 118 |
| Product Categories | 50 |
| Date Range | Jan 2015 – Jan 2018 |
| Late Delivery Rate | **57.3%** (all regions above 50% threshold) |
| Avg Shipping Delay | 0.6 days |
| Class A SKUs (drive 80% revenue) | **Only 7 out of 118** |
| Class C SKUs (bottom 5% revenue) | 95 products |

### Top Insights

**1. ABC Classification — Pareto Principle confirmed**
Just 7 SKUs (6% of the catalog) generate 80% of total revenue. The top product — **Field & Stream Sportsman 16 Gun Fire Safe** — alone accounts for ~$6.2M in revenue. This means 95 SKUs contribute only 5% of revenue and represent a significant opportunity for SKU rationalization.

**2. Revenue by Category — Fishing dominates**
Fishing ($6.2M) leads all categories by a wide margin, followed by Cleats ($4.0M) and Camping & Hiking ($3.7M). The top 3 categories account for over 40% of total revenue.

**3. Late Delivery — systemic supply chain issue**
Every single region has a late delivery rate above 50%, with Central Africa at 61% and Canada at the lowest (52%). This is a systemic issue — not regional — suggesting upstream supply chain or carrier-level problems requiring structural intervention.

**4. Demand Trend — sharp decline in late 2017**
Monthly demand held steady at ~11,000–12,000 units from 2015 through mid-2017, then dropped sharply to ~2,000 units in late 2017 — likely reflecting a data cutoff or major operational change. Forecasting was applied to the stable 2015–2017 period.

**5. Demand Forecasting — ARIMA model on top SKU**
SARIMA(1,1,1)(1,1,1,12) model applied to top revenue SKU. Historical demand was stable at ~520–560 units/month. 6-month forward forecast generated with 95% confidence intervals, supporting procurement planning decisions.

**6. Safety Stock & Reorder Points**
Reorder points calculated for all active SKUs at 95% service level. Top priority item (Perfect Fitness Perf...) requires a reorder point of ~765 units with safety stock of ~252 units, reflecting high demand variability.

---

## Charts

### Revenue by Category
![Revenue by Category](charts/01_revenue_by_category.png)

### Monthly Demand Trend
![Monthly Demand](charts/02_monthly_demand_trend.png)

### Late Delivery Rate by Region
![Late Delivery](charts/03_late_delivery_by_region.png)

### ABC Classification — Pareto Chart
![ABC Pareto](charts/04_abc_pareto_chart.png)

### Safety Stock vs Reorder Point
![Safety Stock](charts/05_safety_stock_reorder_point.png)

### Demand Forecast — ARIMA
![Forecast](charts/06_demand_forecast_arima.png)

---

## Project Structure

```
supply-chain-analytics-dashboard/
│
├── supply_chain_analysis.py        # Full Python analysis pipeline
├── supply_chain_queries.sql        # 10 business SQL queries
├── README.md
│
├── charts/
│   ├── 01_revenue_by_category.png
│   ├── 02_monthly_demand_trend.png
│   ├── 03_late_delivery_by_region.png
│   ├── 04_abc_pareto_chart.png
│   ├── 05_safety_stock_reorder_point.png
│   └── 06_demand_forecast_arima.png
│
├── outputs/
│   ├── abc_classification_results.csv
│   ├── safety_stock_reorder_points.csv
│   └── kpi_summary.csv
│
└── dashboard/
    ├── Supply_Chain_Analytics_Dashboard.pbix
    ├── dashboard_page1_inventory_overview.png
    ├── dashboard_page2_abc_segmentation.png
    ├── dashboard_page3_demand_trends.png
    └── dashboard_page4_stockout_risk.png
```

---

## How to Run

### 1. Get the Data
- Download from [Kaggle — DataCo Smart Supply Chain Dataset](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)
- Save `DataCoSupplyChainDataset.csv` in the project root folder

### 2. Install Dependencies
```bash
pip install pandas numpy matplotlib seaborn statsmodels scikit-learn openpyxl
```

### 3. Run the Analysis
```bash
python supply_chain_analysis.py
```
Automatically generates all 6 charts and 3 CSV output files.

### 4. Load into SQLite for SQL Queries
```python
import pandas as pd, sqlite3
df = pd.read_csv('DataCoSupplyChainDataset.csv', encoding='latin-1')
df.columns = df.columns.str.strip().str.replace(' ','_').str.lower()
conn = sqlite3.connect('supply_chain.db')
df.to_sql('orders', conn, if_exists='replace', index=False)
conn.close()
```
Then open `supply_chain_queries.sql` in DB Browser for SQLite (free).

### 5. Power BI Dashboard
- Open Power BI Desktop (free at powerbi.microsoft.com)
- Load: `DataCoSupplyChainDataset.csv`, `abc_classification_results.csv`, `safety_stock_reorder_points.csv`, `kpi_summary.csv`
- Open `Supply_Chain_Analytics_Dashboard.pbix` to view the full dashboard

---

## Analysis Breakdown

### Data Cleaning
- Standardized 50+ column names across 180,519 rows
- Handled null values, duplicates, and date parsing
- Engineered features: shipping delay, late delivery flag, year-month period

### ABC Classification
Applied Pareto analysis to segment all 118 SKUs by cumulative revenue:
- **Class A (7 SKUs):** Drive 80% of $33M revenue — require tight inventory control and frequent replenishment review
- **Class B (16 SKUs):** Next 15% of revenue — moderate monitoring frequency
- **Class C (95 SKUs):** Bottom 5% — candidates for SKU rationalization or discontinuation

### Safety Stock & Reorder Points
Calculated for every active SKU using industry-standard formula:
```
Safety Stock = Z × √(Lead_Time × σ²_demand + Avg_Demand² × σ²_lead_time)
Reorder Point = (Avg Daily Demand × Lead Time) + Safety Stock
```
Parameters: 95% service level (Z = 1.645), 7-day avg lead time, 2-day lead time std deviation.

### Demand Forecasting (SARIMA)
- Stationarity tested using Augmented Dickey-Fuller (ADF) test
- SARIMA(1,1,1)(1,1,1,12) model fitted on top revenue SKU
- Train/test split with 3-month holdout validation
- 6-month forward forecast with 95% confidence intervals generated

### SQL Business Queries (10 total)
1. Top 10 products by revenue
2. ABC classification via window functions
3. Monthly demand trend
4. Late delivery rate by region
5. Inventory turnover by category
6. Stockout risk by demand variability (CoV)
7. Overall supply chain KPI summary
8. Order status breakdown
9. Reorder point breach detection
10. Revenue by customer segment and category

---

## Power BI Dashboard

| Page | Visuals |
|------|---------|
| Inventory Overview | KPI summary table, revenue by category bar chart, monthly demand line chart |
| ABC Segmentation | Pareto chart by ABC class, product revenue breakdown |
| Demand Trends | Monthly demand trend, category demand, late delivery by region |
| Stockout Risk | Safety stock vs reorder point table, at-risk SKU identification |

---

## Business Recommendations

Based on the analysis:

1. **Focus inventory investment on 7 Class A SKUs** — these drive 80% of revenue and require the tightest replenishment controls and safety stock buffers
2. **Address systemic late delivery** — with 57.3% of all shipments arriving late across every region, this requires carrier or process-level intervention, not regional fixes
3. **Review Class C SKU portfolio** — 95 SKUs contribute only 5% of revenue; rationalizing this tail could significantly reduce inventory holding costs
4. **Increase safety stock for high-variability SKUs** — Perfect Fitness Perf and Nike Men's Dri-FIT show the highest demand variability and need reorder points above 700 units

---

## Skills Demonstrated

`Python` `Pandas` `NumPy` `Matplotlib` `Seaborn` `Statsmodels` `SARIMA` `ARIMA` `SQL` `SQLite` `Power BI` `ABC Classification` `Safety Stock` `EOQ Modeling` `Demand Forecasting` `EDA` `Supply Chain Analytics` `KPI Reporting` `Data Cleaning` `Inventory Optimization`

---

## About

**Aman Bhagwan Singh**  
Supply Chain & Operations Analyst | MS Engineering Management, Penn State Harrisburg (Dec 2025)  
Open to Supply Chain Analyst / Inventory Analyst roles across the US

[LinkedIn](https://www.linkedin.com/in/aman-bhagwansingh02) · amanbsingh02@gmail.com
