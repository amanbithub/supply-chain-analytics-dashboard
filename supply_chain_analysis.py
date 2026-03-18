# ============================================================
# SUPPLY CHAIN ANALYTICS PROJECT
# Aman Bhagwan Singh
# Dataset: DataCo Supply Chain Dataset (Kaggle)
# Tools: Python, Pandas, Matplotlib, Statsmodels
# ============================================================

# ── STEP 0: INSTALL DEPENDENCIES ────────────────────────────
# Run this in your terminal before running the script:
# pip install pandas numpy matplotlib seaborn statsmodels scikit-learn openpyxl

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set plot style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['font.size'] = 11


# ============================================================
# STEP 1: LOAD DATA
# ============================================================
# Download from: https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis
# Save as 'DataCoSupplyChainDataset.csv' in the same folder as this script

print("=" * 60)
print("STEP 1: Loading Data")
print("=" * 60)

df = pd.read_csv('DataCoSupplyChainDataset.csv', encoding='latin-1')
print(f"Rows loaded: {len(df):,}")
print(f"Columns: {list(df.columns)}")


# ============================================================
# STEP 2: DATA CLEANING
# ============================================================
print("\n" + "=" * 60)
print("STEP 2: Data Cleaning")
print("=" * 60)

# Standardize column names
df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()

# Show nulls before cleaning
print("\nNull values before cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])

# Drop columns with >50% nulls
threshold = len(df) * 0.5
df = df.dropna(thresh=threshold, axis=1)

# Fill remaining nulls
df['order_item_discount'].fillna(0, inplace=True)
df['order_profit_per_order'].fillna(0, inplace=True)

# Parse dates
date_cols = [c for c in df.columns if 'date' in c.lower()]
for col in date_cols:
    try:
        df[col] = pd.to_datetime(df[col])
    except:
        pass

# Remove duplicates
before = len(df)
df.drop_duplicates(inplace=True)
print(f"\nDuplicates removed: {before - len(df)}")

# Key columns — rename for clarity
rename_map = {
    'order_item_product_price': 'unit_price',
    'order_item_quantity': 'quantity',
    'order_item_total': 'revenue',
    'category_name': 'category',
    'product_name': 'product',
    'order_date_(dateorders)': 'order_date',
    'shipping_date_(dateorders)': 'ship_date',
    'customer_segment': 'segment',
    'order_region': 'region',
    'order_status': 'order_status',
    'days_for_shipping_(real)': 'actual_shipping_days',
    'days_for_shipment_(scheduled)': 'scheduled_shipping_days',
}
df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

# Create useful derived columns
if 'order_date' in df.columns:
    df['year_month'] = df['order_date'].dt.to_period('M')
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month

if 'actual_shipping_days' in df.columns and 'scheduled_shipping_days' in df.columns:
    df['shipping_delay'] = df['actual_shipping_days'] - df['scheduled_shipping_days']
    df['late_delivery'] = df['shipping_delay'] > 0

print(f"\nCleaned dataset: {len(df):,} rows, {len(df.columns)} columns")
print("Cleaning complete.")


# ============================================================
# STEP 3: EXPLORATORY DATA ANALYSIS (EDA)
# ============================================================
print("\n" + "=" * 60)
print("STEP 3: Exploratory Data Analysis")
print("=" * 60)

# --- 3a. Revenue by Category ---
if 'category' in df.columns and 'revenue' in df.columns:
    cat_revenue = df.groupby('category')['revenue'].sum().sort_values(ascending=False).head(10)
    print("\nTop 10 Categories by Revenue:")
    print(cat_revenue.apply(lambda x: f"${x:,.0f}"))

    fig, ax = plt.subplots(figsize=(12, 5))
    cat_revenue.plot(kind='bar', ax=ax, color='#7F77DD', edgecolor='none')
    ax.set_title('Top 10 Product Categories by Revenue', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Category')
    ax.set_ylabel('Total Revenue ($)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('01_revenue_by_category.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: 01_revenue_by_category.png")

# --- 3b. Monthly Demand Trend ---
if 'year_month' in df.columns and 'quantity' in df.columns:
    monthly = df.groupby('year_month')['quantity'].sum().reset_index()
    monthly['year_month_str'] = monthly['year_month'].astype(str)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(monthly['year_month_str'], monthly['quantity'], color='#1D9E75', linewidth=2, marker='o', markersize=3)
    ax.fill_between(monthly['year_month_str'], monthly['quantity'], alpha=0.15, color='#1D9E75')
    ax.set_title('Monthly Demand Trend (Units Ordered)', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Units Ordered')
    step = max(1, len(monthly) // 12)
    ax.set_xticks(monthly['year_month_str'][::step])
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('02_monthly_demand_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: 02_monthly_demand_trend.png")

# --- 3c. Late Delivery Rate ---
if 'late_delivery' in df.columns:
    late_rate = df['late_delivery'].mean() * 100
    print(f"\nLate Delivery Rate: {late_rate:.1f}%")

    if 'region' in df.columns:
        late_by_region = df.groupby('region')['late_delivery'].mean().sort_values(ascending=False) * 100
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ['#E24B4A' if v > 50 else '#EF9F27' if v > 30 else '#1D9E75' for v in late_by_region]
        late_by_region.plot(kind='bar', ax=ax, color=colors, edgecolor='none')
        ax.set_title('Late Delivery Rate by Region (%)', fontsize=14, fontweight='bold', pad=12)
        ax.set_xlabel('Region')
        ax.set_ylabel('Late Delivery Rate (%)')
        ax.axhline(50, color='red', linestyle='--', linewidth=1, alpha=0.5, label='50% threshold')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig('03_late_delivery_by_region.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Saved: 03_late_delivery_by_region.png")


# ============================================================
# STEP 4: ABC CLASSIFICATION
# ============================================================
print("\n" + "=" * 60)
print("STEP 4: ABC Classification")
print("=" * 60)

if 'product' in df.columns and 'revenue' in df.columns:
    abc = df.groupby('product').agg(
        total_revenue=('revenue', 'sum'),
        total_units=('quantity', 'sum') if 'quantity' in df.columns else ('revenue', 'count'),
        order_count=('revenue', 'count')
    ).sort_values('total_revenue', ascending=False).reset_index()

    # Calculate cumulative revenue %
    abc['cumulative_revenue'] = abc['total_revenue'].cumsum()
    abc['cumulative_pct'] = abc['cumulative_revenue'] / abc['total_revenue'].sum() * 100

    # Assign ABC class
    def assign_abc(pct):
        if pct <= 80:
            return 'A'
        elif pct <= 95:
            return 'B'
        else:
            return 'C'

    abc['abc_class'] = abc['cumulative_pct'].apply(assign_abc)

    # Summary
    summary = abc.groupby('abc_class').agg(
        product_count=('product', 'count'),
        total_revenue=('total_revenue', 'sum')
    )
    summary['revenue_pct'] = summary['total_revenue'] / summary['total_revenue'].sum() * 100
    summary['product_pct'] = summary['product_count'] / summary['product_count'].sum() * 100
    print("\nABC Classification Summary:")
    print(summary.to_string())

    # Pareto Chart
    fig, ax1 = plt.subplots(figsize=(14, 6))
    top50 = abc.head(50)
    colors = ['#7F77DD' if c == 'A' else '#1D9E75' if c == 'B' else '#EF9F27' for c in top50['abc_class']]
    ax1.bar(range(len(top50)), top50['total_revenue'], color=colors, edgecolor='none')
    ax1.set_ylabel('Total Revenue ($)', color='#444441')
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}K'))

    ax2 = ax1.twinx()
    ax2.plot(range(len(top50)), top50['cumulative_pct'], color='#E24B4A', linewidth=2)
    ax2.axhline(80, color='#E24B4A', linestyle='--', alpha=0.5, linewidth=1)
    ax2.axhline(95, color='#EF9F27', linestyle='--', alpha=0.5, linewidth=1)
    ax2.set_ylabel('Cumulative Revenue %', color='#E24B4A')
    ax2.set_ylim(0, 110)

    ax1.set_title('ABC Classification — Pareto Chart (Top 50 Products)', fontsize=14, fontweight='bold', pad=12)
    ax1.set_xlabel('Products (ranked by revenue)')
    ax1.set_xticks([])

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#7F77DD', label='A — Top 80% revenue'),
        Patch(facecolor='#1D9E75', label='B — Next 15% revenue'),
        Patch(facecolor='#EF9F27', label='C — Bottom 5% revenue'),
    ]
    ax1.legend(handles=legend_elements, loc='center right')
    plt.tight_layout()
    plt.savefig('04_abc_pareto_chart.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: 04_abc_pareto_chart.png")

    # Save ABC results
    abc.to_csv('abc_classification_results.csv', index=False)
    print("Saved: abc_classification_results.csv")


# ============================================================
# STEP 5: SAFETY STOCK & REORDER POINT
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: Safety Stock & Reorder Point Calculation")
print("=" * 60)

# Safety Stock Formula:
#   Safety Stock = Z * σ_demand * sqrt(lead_time)
# Reorder Point Formula:
#   ROP = (avg_daily_demand * lead_time) + safety_stock
# Z-score for 95% service level = 1.645

Z = 1.645  # 95% service level

if 'product' in df.columns and 'quantity' in df.columns and 'order_date' in df.columns:
    # Calculate daily demand stats per product
    daily_demand = df.groupby(['product', df['order_date'].dt.date])['quantity'].sum().reset_index()
    daily_demand.columns = ['product', 'date', 'daily_qty']

    demand_stats = daily_demand.groupby('product')['daily_qty'].agg(
        avg_daily_demand='mean',
        std_daily_demand='std',
        demand_days='count'
    ).reset_index()

    # Assume average lead time of 7 days (can be replaced with actual data)
    avg_lead_time = 7
    std_lead_time = 2  # lead time variability

    # Safety stock and ROP
    demand_stats['safety_stock'] = (
        Z * np.sqrt(
            (avg_lead_time * demand_stats['std_daily_demand']**2) +
            (demand_stats['avg_daily_demand']**2 * std_lead_time**2)
        )
    ).round(1)

    demand_stats['reorder_point'] = (
        demand_stats['avg_daily_demand'] * avg_lead_time + demand_stats['safety_stock']
    ).round(1)

    demand_stats['eoq_order_qty'] = (
        np.sqrt(2 * demand_stats['avg_daily_demand'] * 365 * 50 / 0.25)
    ).round(0)  # EOQ assuming ordering cost=$50, holding cost=25% of price

    # Merge with ABC class
    if 'abc' in locals():
        demand_stats = demand_stats.merge(
            abc[['product', 'abc_class', 'total_revenue']],
            on='product', how='left'
        )

    # Sort by reorder point descending (highest priority items first)
    demand_stats = demand_stats.sort_values('reorder_point', ascending=False)

    print("\nTop 10 Products by Reorder Point:")
    display_cols = ['product', 'avg_daily_demand', 'safety_stock', 'reorder_point', 'eoq_order_qty']
    if 'abc_class' in demand_stats.columns:
        display_cols.append('abc_class')
    print(demand_stats[display_cols].head(10).to_string(index=False))

    # Plot top 15 products by safety stock
    top15 = demand_stats.head(15)
    fig, ax = plt.subplots(figsize=(13, 6))
    x = np.arange(len(top15))
    width = 0.4
    bars1 = ax.bar(x - width/2, top15['safety_stock'], width, label='Safety Stock', color='#7F77DD', edgecolor='none')
    bars2 = ax.bar(x + width/2, top15['reorder_point'], width, label='Reorder Point', color='#1D9E75', edgecolor='none')
    ax.set_title('Safety Stock vs Reorder Point — Top 15 Products', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Product')
    ax.set_ylabel('Units')
    ax.set_xticks(x)
    ax.set_xticklabels([p[:20] + '...' if len(p) > 20 else p for p in top15['product']], rotation=45, ha='right')
    ax.legend()
    plt.tight_layout()
    plt.savefig('05_safety_stock_reorder_point.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: 05_safety_stock_reorder_point.png")

    demand_stats.to_csv('safety_stock_reorder_points.csv', index=False)
    print("Saved: safety_stock_reorder_points.csv")


# ============================================================
# STEP 6: DEMAND FORECASTING (ARIMA)
# ============================================================
print("\n" + "=" * 60)
print("STEP 6: Demand Forecasting — ARIMA")
print("=" * 60)

from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_percentage_error

if 'quantity' in df.columns and 'year_month' in df.columns:
    # Pick the top product by total revenue for forecasting
    if 'abc' in locals():
        top_product = abc.iloc[0]['product']
    else:
        top_product = df.groupby('product')['revenue'].sum().idxmax() if 'revenue' in df.columns else df.groupby('product')['quantity'].sum().idxmax()

    print(f"\nForecasting demand for: {top_product}")

    # Monthly demand for top product
    ts_data = df[df['product'] == top_product].groupby('year_month')['quantity'].sum()
    ts_data.index = ts_data.index.to_timestamp()

    if len(ts_data) < 12:
        # Fall back to total monthly demand if not enough product-level data
        print("Not enough product-level data — using total monthly demand instead")
        ts_data = df.groupby('year_month')['quantity'].sum()
        ts_data.index = ts_data.index.to_timestamp()
        top_product = "All Products (Total)"

    print(f"Time series length: {len(ts_data)} months")

    # Stationarity check
    adf_result = adfuller(ts_data.dropna())
    print(f"ADF Statistic: {adf_result[0]:.4f}")
    print(f"p-value: {adf_result[1]:.4f}")
    print("Stationary" if adf_result[1] < 0.05 else "Not stationary — will difference")

    # Train/test split (last 3 months as test)
    train = ts_data.iloc[:-3]
    test = ts_data.iloc[-3:]

    # Fit ARIMA model
    try:
        model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12),
                        enforce_stationarity=False, enforce_invertibility=False)
        fitted = model.fit(disp=False)
        print(f"\nModel AIC: {fitted.aic:.2f}")

        # Forecast next 6 months
        forecast_steps = 6
        forecast = fitted.get_forecast(steps=len(test) + forecast_steps)
        forecast_mean = forecast.predicted_mean
        forecast_ci = forecast.conf_int(alpha=0.05)

        # MAPE on test set
        test_forecast = forecast_mean.iloc[:len(test)]
        mape = mean_absolute_percentage_error(test, test_forecast) * 100
        print(f"Forecast MAPE (test period): {mape:.1f}%")
        print(f"Forecast Accuracy: {100 - mape:.1f}%")

        # Plot forecast
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(train.index, train, label='Historical Demand', color='#3C3489', linewidth=2)
        ax.plot(test.index, test, label='Actual (test)', color='#1D9E75', linewidth=2, linestyle='--')
        ax.plot(forecast_mean.index, forecast_mean, label='Forecast', color='#E24B4A', linewidth=2)
        ax.fill_between(forecast_ci.index,
                        forecast_ci.iloc[:, 0],
                        forecast_ci.iloc[:, 1],
                        alpha=0.15, color='#E24B4A', label='95% Confidence Interval')
        ax.axvline(test.index[0], color='gray', linestyle=':', linewidth=1.5, alpha=0.7, label='Train/Test split')
        ax.set_title(f'Demand Forecast — {top_product[:50]}', fontsize=14, fontweight='bold', pad=12)
        ax.set_xlabel('Month')
        ax.set_ylabel('Units Ordered')
        ax.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig('06_demand_forecast_arima.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Saved: 06_demand_forecast_arima.png")

        # Print forecast values
        future_forecast = forecast_mean.iloc[len(test):]
        print("\nForecast for next 6 months:")
        for date, val in future_forecast.items():
            print(f"  {date.strftime('%b %Y')}: {val:.0f} units")

    except Exception as e:
        print(f"ARIMA fitting issue: {e}")
        print("Falling back to moving average forecast...")

        # Moving Average Forecast (fallback)
        window = 3
        ma = ts_data.rolling(window).mean()
        last_ma = ma.iloc[-1]
        print(f"\n3-Month Moving Average Forecast: {last_ma:.0f} units/month")

        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(ts_data.index, ts_data, label='Historical Demand', color='#3C3489', linewidth=2)
        ax.plot(ma.index, ma, label=f'{window}-Month Moving Average', color='#E24B4A', linewidth=2, linestyle='--')
        ax.set_title('Demand Trend with Moving Average', fontsize=14, fontweight='bold', pad=12)
        ax.set_xlabel('Month')
        ax.set_ylabel('Units Ordered')
        ax.legend()
        plt.tight_layout()
        plt.savefig('06_demand_forecast_moving_average.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Saved: 06_demand_forecast_moving_average.png")


# ============================================================
# STEP 7: INVENTORY KPI SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("STEP 7: KPI Summary Dashboard")
print("=" * 60)

kpis = {}

if 'revenue' in df.columns:
    kpis['Total Revenue'] = f"${df['revenue'].sum():,.0f}"
if 'product' in df.columns:
    kpis['Unique SKUs'] = f"{df['product'].nunique():,}"
if 'order_date' in df.columns:
    kpis['Date Range'] = f"{df['order_date'].min().date()} to {df['order_date'].max().date()}"
if 'late_delivery' in df.columns:
    kpis['Late Delivery Rate'] = f"{df['late_delivery'].mean()*100:.1f}%"
if 'category' in df.columns:
    kpis['Product Categories'] = str(df['category'].nunique())
if 'abc' in locals():
    kpis['Class A SKUs (top 80% revenue)'] = str(len(abc[abc['abc_class'] == 'A']))
    kpis['Class C SKUs (bottom 5% revenue)'] = str(len(abc[abc['abc_class'] == 'C']))
if 'shipping_delay' in df.columns:
    kpis['Avg Shipping Delay (days)'] = f"{df['shipping_delay'].mean():.1f}"

print("\n--- PROJECT KPI SUMMARY ---")
for k, v in kpis.items():
    print(f"  {k}: {v}")

# Save KPI summary
kpi_df = pd.DataFrame(list(kpis.items()), columns=['KPI', 'Value'])
kpi_df.to_csv('kpi_summary.csv', index=False)
print("\nSaved: kpi_summary.csv")

print("\n" + "=" * 60)
print("ALL STEPS COMPLETE")
print("=" * 60)
print("\nFiles generated:")
print("  Charts:  01_revenue_by_category.png")
print("           02_monthly_demand_trend.png")
print("           03_late_delivery_by_region.png")
print("           04_abc_pareto_chart.png")
print("           05_safety_stock_reorder_point.png")
print("           06_demand_forecast_arima.png")
print("  Data:    abc_classification_results.csv")
print("           safety_stock_reorder_points.csv")
print("           kpi_summary.csv")
print("\nNext: Load CSVs into Power BI to build your dashboard!")
