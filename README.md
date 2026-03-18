# Supply Chain Analytics Dashboard
### End-to-End Inventory & Demand Analysis | Python · SQL · Power BI

---

## Project Overview

A complete supply chain analytics case study built on 180,000+ real-world order transactions from the DataCo Global Supply Chain dataset. This project demonstrates the full analytical workflow expected of a supply chain or inventory analyst — from raw data cleaning to interactive dashboards and demand forecasting.

**Tools used:** Python (Pandas, NumPy, Matplotlib, Seaborn, Statsmodels), SQL (SQLite), Power BI Desktop

---

## Key Findings

- **ABC Classification:** Top 20% of SKUs drive 80% of total revenue — identified high-priority items requiring tighter inventory control
- **Stockout Risk:** X SKUs flagged as high-risk based on demand variability (CoV > 0.5) — reorder points calculated for all active products
- **Late Delivery Rate:** X% of shipments arrive late — [Region] has the highest delay rate at X%
- **Demand Forecast:** ARIMA model achieved X% accuracy (MAPE = X%) on 3-month holdout test
- **Seasonal Pattern:** Demand peaks in [Month] — safety stock recommendations adjusted for seasonal variability

> Note: Update the X values above with your actual findings after running the analysis

---

## Project Structure

```
supply-chain-analytics-dashboard/
│
├── data/
│   └── README_data.md          # Instructions to download dataset from Kaggle
│
├── notebooks/
│   └── supply_chain_analysis.py   # Full Python analysis (cleaning → EDA → ABC → forecasting)
│
├── sql/
│   └── supply_chain_queries.sql   # 10 business SQL queries with explanations
│
├── outputs/
│   ├── abc_classification_results.csv
│   ├── safety_stock_reorder_points.csv
│   └── kpi_summary.csv
│
├── charts/
│   ├── 01_revenue_by_category.png
│   ├── 02_monthly_demand_trend.png
│   ├── 03_late_delivery_by_region.png
│   ├── 04_abc_pareto_chart.png
│   ├── 05_safety_stock_reorder_point.png
│   └── 06_demand_forecast_arima.png
│
├── dashboard/
│   └── screenshots/               # Power BI dashboard screenshots
│
└── README.md
```

---

## How to Run

### 1. Get the Data
- Go to [Kaggle — DataCo Smart Supply Chain Dataset](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)
- Download `DataCoSupplyChainDataset.csv`
- Place it in the root project folder

### 2. Install Dependencies
```bash
pip install pandas numpy matplotlib seaborn statsmodels scikit-learn openpyxl
```

### 3. Run the Analysis
```bash
python supply_chain_analysis.py
```
This generates all charts and CSV outputs automatically.

### 4. Run SQL Queries
```python
import pandas as pd, sqlite3
df = pd.read_csv('DataCoSupplyChainDataset.csv', encoding='latin-1')
df.columns = df.columns.str.strip().str.replace(' ','_').str.lower()
conn = sqlite3.connect('supply_chain.db')
df.to_sql('orders', conn, if_exists='replace', index=False)
conn.close()
```
Then open `supply_chain_queries.sql` in any SQLite client (DB Browser for SQLite is free).

### 5. Build the Power BI Dashboard
- Open Power BI Desktop (free at powerbi.microsoft.com)
- Import: `abc_classification_results.csv`, `safety_stock_reorder_points.csv`, `kpi_summary.csv`
- Also connect directly to `DataCoSupplyChainDataset.csv` for the full order data
- Build 4 pages: Inventory Overview · ABC Segmentation · Demand Trends · Stockout Risk

---

## Analysis Breakdown

### Data Cleaning
- Standardized 50+ column names
- Handled null values and duplicates across 180,000+ rows
- Parsed date columns and engineered derived features (shipping delay, year-month, late delivery flag)

### ABC Classification
Segmented all SKUs by cumulative revenue contribution using the Pareto principle:
- **Class A:** Top 80% of revenue — requires tight inventory control, frequent replenishment review
- **Class B:** Next 15% — moderate monitoring
- **Class C:** Bottom 5% — low priority, consider reducing SKU complexity

### Safety Stock & Reorder Points
Calculated for every active SKU using:
```
Safety Stock = Z × √(Lead_Time × σ²_demand + Avg_Demand² × σ²_lead_time)
Reorder Point = (Avg Daily Demand × Lead Time) + Safety Stock
```
Assumed 95% service level (Z = 1.645) and 7-day average lead time.

### Demand Forecasting (ARIMA)
- Applied Augmented Dickey-Fuller test for stationarity
- Fitted SARIMA(1,1,1)(1,1,1,12) model on top SKU
- Validated on 3-month holdout — achieved X% forecast accuracy
- Generated 6-month forward forecast with 95% confidence intervals

### SQL Business Queries (10 total)
1. Top 10 products by revenue
2. ABC classification via SQL window functions
3. Monthly demand trend
4. Late delivery rate by region
5. Inventory turnover by category
6. Stockout risk by demand variability (CoV)
7. Overall supply chain KPI summary
8. Order status breakdown
9. Reorder point breach detection
10. Revenue by customer segment and category

---

## Power BI Dashboard Pages

| Page | Content |
|------|---------|
| Inventory Overview | KPI cards: total SKUs, revenue, late delivery rate, avg lead time |
| ABC Segmentation | Pareto chart, pie chart by class, top A-class products table |
| Demand Trends | Monthly demand line chart, category breakdown, seasonality heatmap |
| Stockout Risk | SKUs below reorder point, risk classification table, safety stock comparison |

---

## Skills Demonstrated

`Python` `Pandas` `NumPy` `Matplotlib` `Seaborn` `Statsmodels` `ARIMA` `SQL` `SQLite` `Power BI` `ABC Classification` `Safety Stock Calculation` `EOQ Modeling` `Demand Forecasting` `EDA` `Supply Chain Analytics` `KPI Reporting` `Data Cleaning`

---

## About

Built by **Aman Bhagwan Singh** — Supply Chain & Operations Analyst  
MS Engineering Management, Penn State Harrisburg (Dec 2025)  
[LinkedIn](https://www.linkedin.com/in/aman-bhagwansingh02) · amanbsingh02@gmail.com
