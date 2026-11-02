import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Operational Analytics & Cohort Hub", layout="wide")

def get_connection():
    return duckdb.connect("data/analytics.duckdb", read_only=True)

conn = get_connection()

st.title("Operational Analytics & Customer Health")

# 1. High-Level KPI Summary
kpis = conn.execute("""
    SELECT 
        COUNT(DISTINCT customer_id) AS total_customers,
        ROUND(SUM(order_amount), 2) AS total_revenue,
        ROUND(AVG(order_amount), 2) AS avg_order_val
    FROM orders 
    WHERE order_status = 'COMPLETED'
""").df()

col1, col2, col3 = st.columns(3)
col1.metric("Transacting Customers", f"{kpis['total_customers'][0]:,}")
col2.metric("Total Completed Revenue", f"${kpis['total_revenue'][0]:,.2f}")
col3.metric("Average Order Value (AOV)", f"${kpis['avg_order_val'][0]:,.2f}")

st.markdown("---")

# 2. RFM Segment Breakdown
st.subheader("Customer Health Segments (RFM)")
segment_df = conn.execute("""
    SELECT 
        customer_segment, 
        COUNT(*) AS customer_count, 
        ROUND(AVG(monetary), 2) AS avg_spend,
        ROUND(AVG(recency_days), 1) AS avg_days_inactive
    FROM rfm_view
    GROUP BY customer_segment
    ORDER BY customer_count DESC
""").df()

fig_segment = px.bar(
    segment_df,
    x="customer_segment",
    y="customer_count",
    color="customer_segment",
    text="customer_count"
)
st.plotly_chart(fig_segment, use_container_width=True)

# 3. Monthly Cohort Retention Heatmap
st.subheader("Monthly Retention Cohort Matrix")
cohort_raw = conn.execute("SELECT * FROM cohort_retention_view").df()

if not cohort_raw.empty:
    cohort_pivot = cohort_raw.pivot(index="cohort_month", columns="cohort_index", values="active_users")
    cohort_size = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0) * 100

    fig_heatmap = px.imshow(
        retention_matrix,
        text_auto=".1f",
        aspect="auto",
        labels=dict(x="Months Active", y="Acquisition Cohort", color="Retention (%)"),
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# 4. Actionable Audience
st.subheader("Actionable Audience: At-Risk High Spenders")
at_risk_df = conn.execute("""
    SELECT customer_id, customer_name, email, recency_days, frequency, monetary
    FROM rfm_view
    WHERE customer_segment = 'At Risk (High Spender)'
    ORDER BY monetary DESC
""").df()

st.dataframe(at_risk_df, use_container_width=True)
st.download_button(
    label="Download Audience for CRM Re-engagement (CSV)",
    data=at_risk_df.to_csv(index=False),
    file_name="at_risk_high_spenders.csv",
    mime="text/csv"
)