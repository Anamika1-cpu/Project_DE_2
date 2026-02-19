🚀 End-to-End Data Engineering Pipeline
Apache Airflow + Apache Spark + Delta Lake + ScyllaDB (Dockerized)
📌 Project Overview

This project demonstrates a complete end-to-end Data Engineering pipeline built using modern distributed technologies.

The pipeline simulates a real-world customer transaction processing system, where:

Raw transaction data is ingested

Data is transformed and aggregated using Apache Spark

Data is stored in Delta Lake format (ACID compliant)

Aggregated results are loaded into ScyllaDB (Cassandra-compatible NoSQL database)

The entire workflow is orchestrated using Apache Airflow

Everything runs in isolated containers using Docker

This project showcases real-world Data Engineering concepts including:

Distributed processing

Orchestration

Delta Lake architecture

Serving layer design

Containerized microservices architecture

🏗️ Architecture
                +------------------+
                |  transactions.csv|
                +------------------+
                          |
                          ▼
                +------------------+
                |  Apache Spark    |
                |  ETL Processing  |
                +------------------+
                          |
                          ▼
                +------------------+
                |   Delta Lake     |
                |  (ACID Storage)  |
                +------------------+
                          |
                          ▼
                +------------------+
                |  Aggregation     |
                |  (Daily Totals)  |
                +------------------+
                          |
                          ▼
                +------------------+
                |   ScyllaDB       |
                |  (Serving Layer) |
                +------------------+
                          |
                          ▼
                +------------------+
                |   Apache Airflow |
                |  Orchestration   |
                +------------------+

🛠️ Tech Stack
Layer	Technology
Orchestration	Apache Airflow 2.8.0
Processing	Apache Spark 3.5.0
Storage	Delta Lake 3.2.0
Serving Layer	ScyllaDB
Containerization	Docker + Docker Compose
Language	Python 3.10
Build Strategy	Multi-stage Docker Build
📂 Project Structure
.
├── airflow/
│   └── dags/
│       └── etl_pipeline_dag.py
│
├── spark/
│   └── etl_job.py
│
├── scylla/
│   └── init.cql
│
├── docker-compose.yml
├── Dockerfile.airflow
└── transactions.csv

🔄 Pipeline Workflow
1️⃣ Data Ingestion

Reads transactions.csv

Uses Spark DataFrame API

Schema inference enabled

df_raw = spark.read.csv(
    "/opt/airflow/data/transactions.csv",
    header=True,
    inferSchema=True
)

2️⃣ Data Transformation

Aggregates transactions per:

customer_id

transaction_date

result = df_raw.groupBy("customer_id", "transaction_date") \
    .agg(sum("amount").alias("daily_total"))


This simulates financial reporting use cases.

3️⃣ Delta Lake Storage

Data is written in Delta format:

result.write \
    .format("delta") \
    .mode("overwrite") \
    .save("/opt/airflow/data/daily_customer_totals")

Why Delta Lake?

ACID transactions

Schema enforcement

Time travel support

Reliable batch & streaming support

4️⃣ Loading into ScyllaDB (Serving Layer)

Aggregated data is inserted into ScyllaDB:

cluster = Cluster(["scylla"])
session = cluster.connect("finance")

for row in result.collect():
    session.execute("""
    INSERT INTO daily_customer_totals 
    (customer_id, transaction_date, daily_total)
    VALUES (%s, %s, %s)
    """, (row.customer_id, row.transaction_date, float(row.daily_total)))

Why ScyllaDB?

High throughput

Low latency

Cassandra-compatible

Ideal for serving layer workloads

5️⃣ Orchestration with Airflow

Airflow DAG triggers Spark job:

run_spark_etl = BashOperator(
    task_id="run_spark_etl",
    bash_command="spark-submit /opt/airflow/spark/etl_job.py"
)


Features:

Task retry handling

Monitoring

Logging

Scheduling support

🐳 Dockerized Setup
Multi-Stage Docker Build
# Stage 1 - Spark
FROM apache/spark:3.5.0 as spark_stage

# Stage 2 - Airflow
FROM apache/airflow:2.8.0-python3.10

# Install Java
RUN apt-get update && \
    apt-get install -y default-jdk curl && \
    apt-get clean

# Copy Spark
COPY --from=spark_stage /opt/spark /opt/spark

ENV PATH="/opt/spark/bin:${PATH}"

docker-compose Services

Airflow

ScyllaDB

Scheduler

Webserver

Run everything:

docker-compose up --build

🗄️ Database Schema
Keyspace
CREATE KEYSPACE finance
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

Table
CREATE TABLE finance.daily_customer_totals (
    customer_id TEXT,
    transaction_date DATE,
    daily_total DOUBLE,
    PRIMARY KEY (customer_id, transaction_date)
);


Partitioning strategy ensures:

Fast lookup per customer

Efficient daily reporting queries

▶️ How to Run
Step 1: Build Containers
docker-compose up --build

Step 2: Open Airflow UI
http://localhost:8080


Trigger DAG manually.

Step 3: Validate in Scylla
docker exec -it scylla cqlsh

SELECT * FROM finance.daily_customer_totals LIMIT 10;

📊 Key Features Implemented

✅ End-to-End Pipeline
✅ Spark-based Aggregation
✅ Delta Lake ACID Storage
✅ NoSQL Serving Layer
✅ Airflow Orchestration
✅ Dockerized Microservices
✅ Error Handling in ETL
✅ Modular Project Structure

🧠 Concepts Demonstrated

Distributed Processing

Data Lakehouse Architecture

ETL vs ELT Concepts

Serving Layer Design

Workflow Orchestration

Container Networking

Microservices-based Data Stack

🚀 Possible Enhancements

Incremental data loads

Change Data Capture (CDC)

Streaming support

Partition optimization

CI/CD integration

Monitoring with Prometheus

Cloud deployment (AWS / Azure)

👩‍💻 Author

Anamika Gour
Azure Data Engineer
Passionate about building scalable Data Engineering systems.
