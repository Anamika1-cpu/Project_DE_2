# Customer Transaction Data Pipeline – Spark, Delta Lake & ScyllaDB (Dockerized)

## 📌 Project Overview

This repository implements an end-to-end data engineering pipeline using **Apache Spark**, **Delta Lake**, **ScyllaDB**, and **Apache Airflow**, fully containerized with Docker.

The pipeline:
- Reads raw transaction data from a CSV file
- Cleans, validates, and transforms the data using Apache Spark
- Stores processed data in Delta Lake format (ACID-compliant storage)
- Aggregates daily customer totals
- Loads aggregated results into ScyllaDB (Cassandra-compatible NoSQL database)
- Orchestrates the workflow using Apache Airflow

> This project was developed as part of a Data Engineering assignment focused on building a realistic, production-style batch data pipeline.

---

## 🛠 Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Apache Spark (PySpark) | 3.5.0 | Data processing & transformations |
| Delta Lake | 3.2.0 | ACID-compliant storage layer |
| ScyllaDB | Latest | High-performance NoSQL serving layer |
| Apache Airflow | 2.8.0 | Workflow orchestration |
| Docker & Docker Compose | — | Containerized environment |
| Python | 3.10 | ETL implementation |

---

## 🏗 Architecture

```
transactions.csv
      ↓
Apache Spark (Data Cleaning & Aggregation)
      ↓
Delta Lake (ACID Storage Layer)
      ↓
Daily Customer Aggregation
      ↓
ScyllaDB (Serving Layer)
      ↓
Apache Airflow (Orchestration)
```

All services (Airflow, Spark, ScyllaDB) run inside Docker containers.

---

## 📂 Project Structure

```
customer-transaction-pipeline/
├── airflow/
│   └── dags/
│       └── etl_pipeline_dag.py
├── spark/
│   └── etl_job.py
├── scylla/
│   └── init.cql
├── data/
│   └── transactions.csv
├── Dockerfile.airflow
├── docker-compose.yml
└── README.md
```

---

## 🧪 Input Dataset

The pipeline processes a transaction dataset with the following schema:

| Field | Description |
|---|---|
| `transaction_id` | Unique transaction identifier |
| `customer_id` | Customer identifier |
| `timestamp` | Transaction timestamp |
| `amount` | Transaction amount |

**Dataset characteristics:**
- 1000+ transaction records
- Duplicate transaction IDs
- Invalid or negative transaction amounts
- Mixed timestamp formats
- Potential dirty records

This simulates real-world transactional financial data.

---

## 🔍 Data Cleaning & Transformations (Spark)

### Data Quality Checks
- Removed duplicate records based on `transaction_id`
- Filtered out transactions where `amount <= 0`
- Explicit date parsing from `timestamp`
- Enforced schema validation

### Transformations
- Extracted `transaction_date` from `timestamp`
- Aggregated total daily spend per customer
- Ensured numeric consistency before storage
- Converted aggregated values to `double` for ScyllaDB compatibility

### Aggregation Logic

Grouped by `customer_id` and `transaction_date`, computing:

```
daily_total = SUM(amount)
```

---

## 🗄 Delta Lake Storage

Processed data is written in Delta format:

```python
result.write \
    .format("delta") \
    .mode("overwrite") \
    .save("/opt/airflow/data/daily_customer_totals")
```

**Why Delta Lake?**
- ACID transactions
- Schema enforcement
- Reliable batch writes
- Prevents partial failures
- Production-grade storage layer

---

## 🗄 Database Design (ScyllaDB)

### Keyspace

```sql
CREATE KEYSPACE finance
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
```

### Table

```sql
CREATE TABLE finance.daily_customer_totals (
    customer_id      TEXT,
    transaction_date DATE,
    daily_total      DOUBLE,
    PRIMARY KEY (customer_id, transaction_date)
);
```

### Design Rationale

| Key | Column | Rationale |
|---|---|---|
| Partition Key | `customer_id` | Fast per-customer lookups |
| Clustering Column | `transaction_date` | Time-series style queries |

Optimized for daily reporting workloads and per-customer time-series queries.

---

## 📊 Row Count Explanation

| Stage | Record Count |
|---|---|
| Raw transactions | ~1000 |
| After deduplication | Reduced |
| After invalid amount filtering | Reduced |
| Final aggregated rows | Significantly lower |

**Why rows were reduced:**
- Duplicate `transaction_id` values removed
- Invalid or negative amounts filtered out
- Aggregation reduces row count by grouping transactions

This reduction demonstrates effective data quality enforcement and proper aggregation logic.

---

## 🚀 How to Run the Pipeline

### 1️⃣ Build and Start Containers

```bash
docker compose up --build
```

Ensure the following containers are running:
- `airflow_webserver`
- `airflow_scheduler`
- `scylla`

### 2️⃣ Open Airflow UI

Navigate to [http://localhost:8080](http://localhost:8080)

- Enable DAG: `customer_transaction_pipeline`
- Trigger manually

### 3️⃣ Spark Job Execution

The DAG runs the following command:

```bash
spark-submit /opt/airflow/spark/etl_job.py
```

Spark processes data and loads results into ScyllaDB.

### 4️⃣ Verify Data in ScyllaDB

```bash
docker exec -it scylla cqlsh
```

```sql
USE finance;
SELECT * FROM daily_customer_totals LIMIT 10;
```

---

## 🧯 Error Handling & Logging

- Spark logs record counts at major stages
- Exceptions handled during ScyllaDB insertion
- Safe shutdown of Cassandra cluster connection
- Airflow task retries enabled
- Delta dependency conflicts resolved during setup
- Permission issues fixed via proper container ownership

---

## 🧠 Key Learnings

- Spark + Delta version compatibility is critical
- Missing Delta JARs cause runtime failures
- Spark container and Airflow container must share a consistent environment
- Cassandra drivers must be installed in the correct container
- Docker networking impacts database connectivity
- Writing to local file systems inside containers requires correct permissions

---

## ⚡ Challenges Solved During Development

- Delta Lake dependency mismatch
- Scala version conflicts
- Missing `delta-storage` JAR
- Cassandra driver installation errors
- Docker container permission issues
- Keyspace connection failures
- Volume path inconsistencies

---

## 🔮 Possible Improvements

- Incremental loads instead of full overwrite
- Streaming ingestion
- Partitioned Delta tables
- Metrics monitoring with Prometheus integration
- Cloud deployment (AWS / Azure)
- Data quality validation framework integration

---

## 👩‍💻 Author

**Anamika Gour**  
Azure Data Engineer  
*Passionate about building scalable data systems*
