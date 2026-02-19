print("=== STARTING JOB ===")

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Test") \
    .master("local[*]") \
    .getOrCreate()

print("=== Spark session created ===")

df = spark.range(10)
df.show()

spark.stop()

print("=== JOB FINISHED ===")
