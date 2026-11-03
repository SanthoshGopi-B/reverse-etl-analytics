import duckdb
import pytest

@pytest.fixture(scope="module")
def db_conn():
    conn = duckdb.connect("data/analytics.duckdb", read_only=True)
    yield conn
    conn.close()

def test_customers_non_null(db_conn):
    null_count = db_conn.execute("SELECT COUNT(*) FROM customers WHERE customer_id IS NULL").fetchone()[0]
    assert null_count == 0

def test_orders_positive_amounts(db_conn):
    invalid_orders = db_conn.execute("SELECT COUNT(*) FROM orders WHERE order_amount <= 0").fetchone()[0]
    assert invalid_orders == 0

def test_rfm_segments_populated(db_conn):
    segments = db_conn.execute("SELECT DISTINCT customer_segment FROM rfm_view").fetchall()
    segment_names = [s[0] for s in segments]
    assert len(segment_names) > 0
    assert "At Risk (High Spender)" in segment_names or "Champions" in segment_names