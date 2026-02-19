from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, sum as spark_sum

print("=== STARTING ETL ===")

spark = SparkSession.builder \
    .appName("CustomerTransactionETL") \
    .master("local[*]") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

print("=== Spark Started ===")

# ------------------------------------------
# 1️⃣ Read CSV (Raw Data)
# ------------------------------------------

csv_path = "/opt/airflow/spark/transactions.csv"

df_raw = spark.read.csv(
    csv_path,
    header=True,
    inferSchema=True
)

print("Initial Count:", df_raw.count())

# ------------------------------------------
# 2️⃣ Write to Delta Lake
# ------------------------------------------

delta_path = "/opt/airflow/data/customer_transactions"


df_raw.write.format("delta") \
    .mode("overwrite") \
    .save(delta_path)

print("=== Written to Delta ===")

# ------------------------------------------
# 3️⃣ Read from Delta
# ------------------------------------------

df = spark.read.format("delta").load(delta_path)

# ------------------------------------------
# 4️⃣ Transformations
# ------------------------------------------

df = df.dropDuplicates(["transaction_id"])
df = df.filter(col("amount") > 0)
df = df.withColumn("transaction_date", to_date(col("timestamp")))

result = df.groupBy("customer_id", "transaction_date") \
    .agg(spark_sum("amount").alias("daily_total"))

print("=== Aggregated Result ===")
result.show()

print("=== ETL FINISHED ===")

# ------------------------------------------
# 5️⃣ Write Aggregated Output to New Delta Table
# ------------------------------------------

aggregated_path = "/opt/airflow/data/daily_customer_totals"

result.write.format("delta") \
    .mode("overwrite") \
    .save(aggregated_path)

print("=== Aggregated Data Written to Delta ===")


# ------------------------------------------
# 6️⃣ Load Aggregated Data into ScyllaDB
# ------------------------------------------

print("=== Loading Data into ScyllaDB ===")

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

try:
    cluster = Cluster(["scylla"])  # Docker service name
    session = cluster.connect()
    session.set_keyspace("finance")
    rows = result.collect()

    insert_query = """
    INSERT INTO daily_customer_totals (customer_id, transaction_date, daily_total)
    VALUES (%s, %s, %s)
    """

    for row in rows:
        session.execute(insert_query, (
            row.customer_id,
            row.transaction_date,
            float(row.daily_total)
        ))

    print("=== Data Successfully Loaded into Scylla ===")

except Exception as e:
    print("Error while inserting into Scylla:", str(e))

finally:
    cluster.shutdown()

spark.stop()