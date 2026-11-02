import random
from datetime import datetime
import duckdb
from faker import Faker

fake = Faker()

def init_db(db_path="data/analytics.duckdb"):
    conn = duckdb.connect(db_path)

    # 1. Raw Schema
    conn.execute("""
        CREATE OR REPLACE TABLE customers (
            customer_id VARCHAR PRIMARY KEY,
            customer_name VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            signup_date DATE NOT NULL
        );

        CREATE OR REPLACE TABLE orders (
            order_id VARCHAR PRIMARY KEY,
            customer_id VARCHAR NOT NULL,
            order_date TIMESTAMP NOT NULL,
            order_amount DECIMAL(10, 2) NOT NULL,
            order_status VARCHAR NOT NULL
        );
    """)

    # 2. Seed Customers
    customers = []
    base_date = datetime(2025, 1, 1)
    for i in range(1, 301):
        cust_id = f"CUST_{i:04d}"
        signup = fake.date_between(start_date=base_date, end_date="today")
        customers.append((cust_id, fake.name(), fake.email(), signup))

    conn.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)

    # 3. Seed Orders
    orders = []
    statuses = ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "CANCELLED", "REFUNDED"]
    for i in range(1, 2501):
        order_id = f"ORD_{i:05d}"
        cust_id = random.choice(customers)[0]
        order_date = fake.date_time_between(start_date=base_date, end_date="now")
        amount = round(random.uniform(15.0, 650.0), 2)
        orders.append((order_id, cust_id, order_date, amount, random.choice(statuses)))

    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)
    conn.close()
    print("Database initialized and seeded in data/analytics.duckdb")

if __name__ == "__main__":
    init_db()