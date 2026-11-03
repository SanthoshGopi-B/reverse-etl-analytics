import duckdb
import pandas as pd

def run_reverse_etl_sync(db_path="data/analytics.duckdb", output_csv="data/crm_outbound_queue.csv"):
    conn = duckdb.connect(db_path, read_only=True)

    query = """
        SELECT 
            customer_id, 
            customer_name, 
            email, 
            recency_days, 
            frequency, 
            monetary,
            CURRENT_TIMESTAMP AS synced_at
        FROM rfm_view
        WHERE customer_segment = 'At Risk (High Spender)'
        ORDER BY monetary DESC
    """
    df = conn.execute(query).df()
    conn.close()

    if df.empty:
        print("[Reverse ETL] No records match the criteria today.")
        return

    # Export audience directly to downstream queue
    df.to_csv(output_csv, index=False)
    print(f"[Reverse ETL] Successfully synced {len(df)} at-risk accounts to {output_csv}")

    # Operational preview
    print("\n--- Outbound Sync Payload Preview ---")
    for _, row in df.head(3).iterrows():
        print(f"Alert: {row['customer_name']} ({row['email']}) | "
              f"Inactive: {row['recency_days']} days | LTV: ${row['monetary']:,.2f}")

if __name__ == "__main__":
    run_reverse_etl_sync()