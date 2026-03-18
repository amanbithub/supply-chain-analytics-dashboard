-- ============================================================
-- SUPPLY CHAIN ANALYTICS PROJECT — SQL QUERIES
-- Aman Bhagwan Singh
-- Run in SQLite after loading data with Python
-- ============================================================

-- ── HOW TO LOAD DATA INTO SQLITE ────────────────────────────
-- Run this Python snippet first to create the database:
--
-- import pandas as pd, sqlite3
-- df = pd.read_csv('DataCoSupplyChainDataset.csv', encoding='latin-1')
-- df.columns = df.columns.str.strip().str.replace(' ','_').str.lower()
-- conn = sqlite3.connect('supply_chain.db')
-- df.to_sql('orders', conn, if_exists='replace', index=False)
-- conn.close()
-- print("Database created: supply_chain.db")
-- ────────────────────────────────────────────────────────────


-- ============================================================
-- QUERY 1: Top 10 Products by Total Revenue
-- Business Question: Which SKUs drive the most revenue?
-- ============================================================
SELECT
    product_name                            AS product,
    COUNT(*)                                AS order_count,
    SUM(order_item_quantity)                AS total_units_sold,
    ROUND(SUM(order_item_total), 2)         AS total_revenue,
    ROUND(AVG(order_item_product_price), 2) AS avg_unit_price
FROM orders
GROUP BY product_name
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- QUERY 2: ABC Classification (Revenue Segmentation)
-- Business Question: Which products are A, B, and C class?
-- ============================================================
WITH product_revenue AS (
    SELECT
        product_name,
        ROUND(SUM(order_item_total), 2) AS total_revenue
    FROM orders
    GROUP BY product_name
),
ranked AS (
    SELECT
        product_name,
        total_revenue,
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC) AS cumulative_revenue,
        SUM(total_revenue) OVER ()                            AS grand_total
    FROM product_revenue
),
classified AS (
    SELECT
        product_name,
        total_revenue,
        ROUND(cumulative_revenue / grand_total * 100, 2) AS cumulative_pct,
        CASE
            WHEN cumulative_revenue / grand_total * 100 <= 80 THEN 'A'
            WHEN cumulative_revenue / grand_total * 100 <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM ranked
)
SELECT
    abc_class,
    COUNT(*)                                   AS product_count,
    ROUND(SUM(total_revenue), 2)               AS class_revenue,
    ROUND(SUM(total_revenue) * 100.0
        / SUM(SUM(total_revenue)) OVER (), 1)  AS revenue_pct
FROM classified
GROUP BY abc_class
ORDER BY abc_class;


-- ============================================================
-- QUERY 3: Monthly Demand Trend
-- Business Question: How is demand trending month over month?
-- ============================================================
SELECT
    STRFTIME('%Y-%m', "order_date_(dateorders)")    AS year_month,
    COUNT(DISTINCT "order_id")                       AS total_orders,
    SUM(order_item_quantity)                         AS total_units,
    ROUND(SUM(order_item_total), 2)                  AS total_revenue,
    ROUND(AVG(order_item_total), 2)                  AS avg_order_value
FROM orders
WHERE "order_date_(dateorders)" IS NOT NULL
GROUP BY year_month
ORDER BY year_month;


-- ============================================================
-- QUERY 4: Late Delivery Analysis by Region
-- Business Question: Which regions have the worst delivery performance?
-- ============================================================
SELECT
    order_region                                            AS region,
    COUNT(*)                                                AS total_shipments,
    SUM(CASE WHEN "days_for_shipping_(real)"
             > "days_for_shipment_(scheduled)"
             THEN 1 ELSE 0 END)                             AS late_deliveries,
    ROUND(
        SUM(CASE WHEN "days_for_shipping_(real)"
                 > "days_for_shipment_(scheduled)"
                 THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 1
    )                                                       AS late_delivery_rate_pct,
    ROUND(AVG("days_for_shipping_(real)"), 1)               AS avg_actual_days,
    ROUND(AVG("days_for_shipment_(scheduled)"), 1)          AS avg_scheduled_days,
    ROUND(AVG("days_for_shipping_(real)"
              - "days_for_shipment_(scheduled)"), 1)        AS avg_delay_days
FROM orders
GROUP BY order_region
ORDER BY late_delivery_rate_pct DESC;


-- ============================================================
-- QUERY 5: Inventory Turnover by Category
-- Business Question: Which categories move fastest / slowest?
-- ============================================================
SELECT
    category_name                                       AS category,
    SUM(order_item_quantity)                            AS total_units_sold,
    ROUND(SUM(order_item_total), 2)                     AS total_revenue,
    COUNT(DISTINCT product_name)                        AS sku_count,
    ROUND(SUM(order_item_total)
          / COUNT(DISTINCT product_name), 2)            AS revenue_per_sku,
    ROUND(SUM(order_item_quantity)
          / COUNT(DISTINCT product_name), 1)            AS units_per_sku
FROM orders
GROUP BY category_name
ORDER BY total_revenue DESC;


-- ============================================================
-- QUERY 6: Stockout Risk — Products with High Demand Variability
-- Business Question: Which SKUs have unpredictable demand (high risk)?
-- ============================================================
WITH daily_demand AS (
    SELECT
        product_name,
        DATE("order_date_(dateorders)")     AS order_day,
        SUM(order_item_quantity)            AS daily_qty
    FROM orders
    GROUP BY product_name, order_day
),
demand_stats AS (
    SELECT
        product_name,
        COUNT(*)                            AS active_days,
        ROUND(AVG(daily_qty), 2)            AS avg_daily_demand,
        ROUND(
            SQRT(
                AVG(daily_qty * daily_qty)
                - AVG(daily_qty) * AVG(daily_qty)
            ), 2
        )                                   AS std_daily_demand
    FROM daily_demand
    GROUP BY product_name
    HAVING active_days >= 30
)
SELECT
    product_name,
    avg_daily_demand,
    std_daily_demand,
    ROUND(std_daily_demand / NULLIF(avg_daily_demand, 0), 2) AS coefficient_of_variation,
    CASE
        WHEN std_daily_demand / NULLIF(avg_daily_demand, 0) > 0.5 THEN 'HIGH RISK'
        WHEN std_daily_demand / NULLIF(avg_daily_demand, 0) > 0.25 THEN 'MEDIUM RISK'
        ELSE 'LOW RISK'
    END                                     AS stockout_risk
FROM demand_stats
ORDER BY coefficient_of_variation DESC
LIMIT 20;


-- ============================================================
-- QUERY 7: Supplier / Shipping Performance KPIs
-- Business Question: What is the overall supply chain health?
-- ============================================================
SELECT
    ROUND(
        SUM(CASE WHEN "days_for_shipping_(real)"
                 <= "days_for_shipment_(scheduled)"
                 THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 1
    )                                               AS on_time_delivery_rate_pct,
    ROUND(AVG("days_for_shipping_(real)"), 1)        AS avg_actual_lead_time_days,
    ROUND(AVG("days_for_shipment_(scheduled)"), 1)   AS avg_scheduled_lead_time_days,
    ROUND(
        AVG("days_for_shipping_(real)"
            - "days_for_shipment_(scheduled)"), 1
    )                                               AS avg_delay_days,
    COUNT(DISTINCT product_name)                    AS total_skus,
    COUNT(DISTINCT category_name)                   AS total_categories,
    COUNT(DISTINCT order_region)                    AS total_regions,
    COUNT(DISTINCT "order_id")                      AS total_orders,
    ROUND(SUM(order_item_total), 2)                 AS total_revenue
FROM orders;


-- ============================================================
-- QUERY 8: Order Status Breakdown
-- Business Question: How many orders are cancelled, shipped, pending?
-- ============================================================
SELECT
    order_status,
    COUNT(*)                                        AS order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct_of_total,
    ROUND(SUM(order_item_total), 2)                 AS total_value
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;


-- ============================================================
-- QUERY 9: Reorder Point Breach Detection
-- Business Question: Which products are likely below reorder point right now?
-- ============================================================
WITH recent_demand AS (
    SELECT
        product_name,
        ROUND(AVG(daily_qty), 2)    AS avg_daily_demand,
        ROUND(
            SQRT(AVG(daily_qty*daily_qty) - AVG(daily_qty)*AVG(daily_qty))
        , 2)                        AS demand_std
    FROM (
        SELECT
            product_name,
            DATE("order_date_(dateorders)") AS order_day,
            SUM(order_item_quantity)        AS daily_qty
        FROM orders
        WHERE "order_date_(dateorders)" >= DATE('now', '-90 days')
        GROUP BY product_name, order_day
    ) d
    GROUP BY product_name
)
SELECT
    product_name,
    avg_daily_demand,
    demand_std,
    ROUND(avg_daily_demand * 7, 1)              AS demand_during_lead_time,
    ROUND(1.645 * demand_std * 2.646, 1)        AS safety_stock_95pct,
    ROUND(avg_daily_demand * 7
          + 1.645 * demand_std * 2.646, 1)      AS reorder_point,
    'CHECK STOCK LEVEL'                         AS action_needed
FROM recent_demand
WHERE avg_daily_demand > 0
ORDER BY reorder_point DESC
LIMIT 15;


-- ============================================================
-- QUERY 10: Revenue by Customer Segment and Category
-- Business Question: Which segment + category combos are most valuable?
-- ============================================================
SELECT
    customer_segment                            AS segment,
    category_name                               AS category,
    COUNT(DISTINCT "order_id")                  AS orders,
    ROUND(SUM(order_item_total), 2)             AS total_revenue,
    ROUND(AVG(order_item_total), 2)             AS avg_order_value
FROM orders
GROUP BY customer_segment, category_name
ORDER BY total_revenue DESC
LIMIT 20;
