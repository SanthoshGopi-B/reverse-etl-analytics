import duckdb

def create_views(db_path="data/analytics.duckdb"):
    conn = duckdb.connect(db_path)

    # 1. RFM Customer Health & Segmentation View
    conn.execute("""
        CREATE OR REPLACE VIEW rfm_view AS
        WITH rfm_calc AS (
            SELECT 
                c.customer_id,
                c.customer_name,
                c.email,
                MAX(o.order_date) AS last_order_date,
                COUNT(DISTINCT o.order_id) AS frequency,
                ROUND(SUM(o.order_amount), 2) AS monetary,
                DATE_DIFF('day', MAX(o.order_date), CURRENT_DATE) AS recency_days
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'COMPLETED'
            GROUP BY c.customer_id, c.customer_name, c.email
        )
        SELECT 
            *,
            CASE 
                WHEN recency_days <= 30 AND frequency >= 6 THEN 'Champions'
                WHEN recency_days <= 60 AND monetary >= 1000 THEN 'High-Value Loyal'
                WHEN recency_days > 90 AND monetary >= 800 THEN 'At Risk (High Spender)'
                WHEN recency_days > 120 THEN 'Churned'
                ELSE 'Regular'
            END AS customer_segment
        FROM rfm_calc;
    """)

    # 2. Monthly Retention Cohort Matrix View
    conn.execute("""
        CREATE OR REPLACE VIEW cohort_retention_view AS
        WITH customer_cohort AS (
            SELECT 
                customer_id,
                DATE_TRUNC('month', MIN(order_date)) AS cohort_month
            FROM orders
            WHERE order_status = 'COMPLETED'
            GROUP BY customer_id
        ),
        monthly_activity AS (
            SELECT 
                o.customer_id,
                DATE_TRUNC('month', o.order_date) AS activity_month,
                c.cohort_month,
                (EXTRACT(YEAR FROM o.order_date) - EXTRACT(YEAR FROM c.cohort_month)) * 12 +
                (EXTRACT(MONTH FROM o.order_date) - EXTRACT(MONTH FROM c.cohort_month)) AS cohort_index
            FROM orders o
            JOIN customer_cohort c ON o.customer_id = c.customer_id
            WHERE o.order_status = 'COMPLETED'
            GROUP BY 1, 2, 3, 4
        )
        SELECT 
            STRFTIME(cohort_month, '%Y-%m') AS cohort_month,
            CAST(cohort_index AS INTEGER) AS cohort_index,
            COUNT(DISTINCT customer_id) AS active_users
        FROM monthly_activity
        GROUP BY cohort_month, cohort_index
        ORDER BY cohort_month, cohort_index;
    """)

    conn.close()
    print("Analytical views (rfm_view, cohort_retention_view) created successfully.")

if __name__ == "__main__":
    create_views()