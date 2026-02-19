from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "anamika",
    "retries": 0,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="customer_transaction_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    run_spark_etl = BashOperator(
        task_id="run_spark_etl",
        bash_command="""
        spark-submit /opt/airflow/spark/etl_job.py
        """
    )

    run_spark_etl


