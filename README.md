# Customer Retention & Operational Analytics Engine (Reverse ETL)

An end-to-end data pipeline that ingests raw e-commerce transaction logs, models customer health using RFM segmentation and cohort retention matrices, provides interactive analytics via Streamlit, and pushes actionable segments to downstream operational workflows (Reverse ETL).

---

## Architecture Overview

```text
┌───────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ Raw Event / Orders    │ ───► │ Analytical Lakehouse    │ ───► │ Streamlit Dashboard     │
│ (Synthetic Ingestion) │      │ (DuckDB Modeling Views) │      │ (Plotly Visualizations) │
└───────────────────────┘      └───────────┬─────────────┘      └─────────────────────────┘
                                           │
                                           ▼
                               ┌─────────────────────────┐
                               │ Reverse ETL Sync Engine │ ───► CRM Queue / Webhook
                               │ (Automated Outbound)    │
                               └─────────────────────────┘
```

---

## Tech Stack & Tooling

* **Storage & Transformation:** DuckDB (in-process analytical OLAP database, CTE-based SQL modeling)
* **Application & UI:** Streamlit, Plotly
* **Data Synthesis & Testing:** Faker, Pytest
* **Language & Runtime:** Python 3.11+

---

## Key Features

1. **RFM Segmentation Engine:** Calculates Recency, Frequency, and Monetary metrics across transactional histories to categorize users (*Champions*, *High-Value Loyal*, *At Risk*, *Churned*).
2. **Monthly Cohort Retention Matrix:** Computes dynamic retention percentages indexed by acquisition month.
3. **Interactive Operational Dashboard:** Live KPIs (AOV, Net Revenue), dynamic heatmaps, and segment distributions.
4. **Reverse ETL Outbound Pipeline:** Automatically identifies accounts requiring immediate retention action and exports formatted sync queues for CRM ingestion.
5. **Data Quality Tests:** Automated test suite validating data non-nullness, positive monetary boundaries, and segmentation validity.

---

## Getting Started

### 1. Prerequisites & Setup
```bash
git clone [https://github.com/SanthoshGopi-B/reverse-etl-analytics.git](https://github.com/SanthoshGopi-B/reverse-etl-analytics.git)
cd reverse-etl-analytics

python -m venv venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Seed Data & Materialize Views
```bash
python scripts/generate_data.py
python scripts/create_views.py
```

### 3. Run Pipeline Tests
```bash
pytest tests/
```

### 4. Launch Dashboard & Run Outbound Sync
```bash
# Terminal 1: Launch UI
streamlit run app.py

# Terminal 2: Run Reverse ETL Sync
python scripts/sync_alerts.py
```