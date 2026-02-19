<div align="center">

# 🚀 End-to-End Data Engineering Pipeline

### Apache Airflow · Apache Spark · Delta Lake · ScyllaDB · Docker

![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.8.0-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5.0-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.2.0-003366?style=for-the-badge&logo=delta&logoColor=white)
![ScyllaDB](https://img.shields.io/badge/ScyllaDB-NoSQL-53CADD?style=for-the-badge&logo=scylladb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)

<br/>

> A **production-grade batch data pipeline** simulating a real-world customer transaction processing system — built with distributed computing, ACID-compliant storage, and fully containerized microservices.

</div>

---

## 📌 Project Overview

This project demonstrates a **complete end-to-end Data Engineering pipeline** built using modern distributed technologies.

The pipeline simulates a real-world customer transaction processing system where:

- 📥 Raw transaction data is **ingested** from CSV
- ⚡ Data is **transformed and aggregated** using Apache Spark
- 🏔️ Data is **stored in Delta Lake** format (ACID-compliant)
- 📦 Aggregated results are **loaded into ScyllaDB** (Cassandra-compatible NoSQL)
- 🔁 The entire workflow is **orchestrated using Apache Airflow**
- 🐳 Everything runs in **isolated Docker containers**

This project showcases real-world Data Engineering concepts including distributed processing, orchestration, Delta Lake architecture, serving layer design, and containerized microservices.

---

## 🏗️ Architecture

```
┌─────────────────────────┐
│     transactions.csv    │   ← Raw Source Data
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      Apache Spark       │   ← Distributed ETL Processing
│     (ETL Processing)    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       Delta Lake        │   ← ACID-Compliant Storage Layer
│     (ACID Storage)      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      Aggregation        │   ← Daily Customer Totals
│    (Daily Totals)       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       ScyllaDB          │   ← High-Performance Serving Layer
│    (Serving Layer)      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     Apache Airflow      │   ← Workflow Orchestration & Scheduling
│    (Orchestration)      │
└─────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|---|---|---|
| 🔁 Orchestration | Apache Airflow | 2.8.0 |
| ⚡ Processing | Apache Spark (PySpark) | 3.5.0 |
| 🏔️ Storage | Delta Lake | 3.2.0 |
| 📦 Serving Layer | ScyllaDB | Latest |
| 🐳 Containerization | Docker + Docker Compose | — |
| 🐍 Language | Python | 3.10 |
| 🔨 Build Strategy | Multi-stage Docker Build | — |

---

## 📂 Project Structure

```
customer-transaction-pipeline/
│
├── 📁 airflow/
│   └── 📁 dags/
│       └── 📄 etl_pipeline_dag.py       # Airflow DAG definition
│
├── 📁 spark/
│   └── 📄 etl_job.py                    # PySpark ETL job
│
├── 📁 scylla/
│   └── 📄 init.cql                      # ScyllaDB schema initialization
│
├── 📁 data/
│   └── 📄 transactions.csv              # Raw input dataset
│
├── 📄 Dockerfile.airflow                # Multi-stage Docker build
├── 📄 docker-compose.yml                # Service orchestration
└── 📄 README.md
```

---

## 🔄 Pipeline Workflow

### 1️⃣ Data Ingestion

Reads `transactions.csv` using Spark's DataFrame API with schema inference:

```python
df_raw = spark.read.csv(
    "/opt/airflow/data/transactions.csv",
    header=True,
    inferSchema=True
)
```

**Dataset characteristics:**
- 1000+ transaction records
- Duplicate `transaction_id` values
- Invalid / negative amounts
- Mixed timestamp formats
- Simulates real-world dirty financial data

---

### 2️⃣ Data Cleaning & Transformation

**Quality checks applied:**
- Removed duplicates based on `transaction_id`
- Filtered out records where `amount <= 0`
- Parsed and standardized `timestamp` → `transaction_date`
- Enforced schema validation

**Aggregation** — groups transactions per customer per day:

```python
result = df_raw.groupBy("customer_id", "transaction_date") \
    .agg(sum("amount").alias("daily_total"))
```

> Simulates financial daily reporting use cases.

---

### 3️⃣ Delta Lake Storage

Processed data is persisted in Delta format:

```python
result.write \
    .format("delta") \
    .mode("overwrite") \
    .save("/opt/airflow/data/daily_customer_totals")
```

**Why Delta Lake?**

| Feature | Benefit |
|---|---|
| ACID Transactions | Prevents partial failures |
| Schema Enforcement | Ensures data consistency |
| Time Travel | Historical data access |
| Batch & Streaming | Unified processing support |

---

### 4️⃣ Loading into ScyllaDB (Serving Layer)

Aggregated records are inserted into ScyllaDB for low-latency querying:

```python
cluster = Cluster(["scylla"])
session = cluster.connect("finance")

for row in result.collect():
    session.execute("""
        INSERT INTO daily_customer_totals
        (customer_id, transaction_date, daily_total)
        VALUES (%s, %s, %s)
    """, (row.customer_id, row.transaction_date, float(row.daily_total)))
```

**Why ScyllaDB?**

| Feature | Benefit |
|---|---|
| High Throughput | Millions of writes/sec |
| Low Latency | Sub-millisecond reads |
| Cassandra-Compatible | Easy driver integration |
| Serving Layer Ready | Optimized for dashboards & APIs |

---

### 5️⃣ Orchestration with Apache Airflow

The Airflow DAG triggers the Spark job via a `BashOperator`:

```python
run_spark_etl = BashOperator(
    task_id="run_spark_etl",
    bash_command="spark-submit /opt/airflow/spark/etl_job.py"
)
```

**Airflow features leveraged:**
- ✅ Task retry handling
- ✅ Real-time monitoring
- ✅ Structured logging
- ✅ Cron-based scheduling support

---

## 🐳 Dockerized Setup

### Multi-Stage Docker Build

```dockerfile
# Stage 1 — Spark base
FROM apache/spark:3.5.0 AS spark_stage

# Stage 2 — Airflow with Spark embedded
FROM apache/airflow:2.8.0-python3.10

RUN apt-get update && \
    apt-get install -y default-jdk curl && \
    apt-get clean

COPY --from=spark_stage /opt/spark /opt/spark

ENV PATH="/opt/spark/bin:${PATH}"
```

### Docker Compose Services

| Service | Role |
|---|---|
| `airflow_webserver` | Airflow UI on port 8080 |
| `airflow_scheduler` | DAG scheduling |
| `scylla` | ScyllaDB NoSQL instance |

---

## 🗄️ Database Schema

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

**Partitioning strategy:**

| Key | Column | Purpose |
|---|---|---|
| Partition Key | `customer_id` | Fast per-customer lookups |
| Clustering Column | `transaction_date` | Efficient time-series queries |

---

## 📊 Row Count Breakdown

| Stage | Record Count |
|---|---|
| Raw transactions | ~1000 |
| After deduplication | Reduced |
| After invalid amount filtering | Reduced further |
| Final aggregated rows | Significantly lower |

> Row reduction validates correct deduplication, filtering, and aggregation logic — a sign of a healthy, well-enforced pipeline.

---

## ▶️ How to Run

### Step 1 — Build & Start Containers

```bash
docker-compose up --build
```

### Step 2 — Open Airflow UI

```
http://localhost:8080
```

Enable the DAG `customer_transaction_pipeline` and trigger it manually.

### Step 3 — Validate Results in ScyllaDB

```bash
docker exec -it scylla cqlsh
```

```sql
USE finance;
SELECT * FROM daily_customer_totals LIMIT 10;
```

---

## ✅ Key Features Implemented

| Feature | Status |
|---|---|
| End-to-End Pipeline | ✅ |
| Spark-based Aggregation | ✅ |
| Delta Lake ACID Storage | ✅ |
| NoSQL Serving Layer | ✅ |
| Airflow Orchestration | ✅ |
| Dockerized Microservices | ✅ |
| Error Handling in ETL | ✅ |
| Modular Project Structure | ✅ |

---

## 🧠 Concepts Demonstrated

- Distributed Processing at scale
- Data Lakehouse Architecture (Delta Lake)
- ETL vs ELT design patterns
- Serving Layer Design for low-latency access
- Workflow Orchestration with dependency management
- Container Networking across services
- Microservices-based Data Stack

---

## 🧯 Error Handling & Logging

- Spark logs record counts at each major stage
- Exceptions caught and handled during ScyllaDB writes
- Safe shutdown of Cassandra cluster connections
- Airflow task retries configured
- Delta dependency conflicts resolved at build time
- Docker volume permissions correctly set

---

## 🚀 Possible Enhancements

- [ ] Incremental data loads with Change Data Capture (CDC)
- [ ] Real-time streaming ingestion (Kafka + Spark Structured Streaming)
- [ ] Partitioned Delta tables for performance at scale
- [ ] Data quality framework (Great Expectations)
- [ ] CI/CD integration (GitHub Actions)
- [ ] Monitoring with Prometheus + Grafana
- [ ] Cloud deployment on AWS / Azure

---

## 👩‍💻 Author

<div align="center">

**Anamika Gour**
*Azure Data Engineer*

Passionate about building scalable, production-grade Data Engineering systems.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com)

</div>

---

<div align="center">

### ⭐ If you found this project useful, please star the repository!

*Contributions, feedback, and collaboration are always welcome.*

</div>
