# Databricks notebook source
# MAGIC %md
# MAGIC # Ingest TPM feedback
# MAGIC Creates `feedback_bronze` if it does not exist and appends a starter sample row.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "consultant_pulse")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
table = f"{catalog}.{schema}.feedback_bronze"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS {table} (
      feedback_id STRING,
      consultant_name STRING,
      engagement STRING,
      submitted_at TIMESTAMP,
      score DOUBLE,
      comment STRING
    )
    USING DELTA
    """
)

spark.sql(
    f"""
    INSERT INTO {table}
    SELECT
      'seed-0001' AS feedback_id,
      'Example Consultant' AS consultant_name,
      'Example Engagement' AS engagement,
      current_timestamp() AS submitted_at,
      4.0 AS score,
      'Starter row from the Consultant Pulse bundle' AS comment
    WHERE NOT EXISTS (
      SELECT 1 FROM {table} WHERE feedback_id = 'seed-0001'
    )
    """
)

display(spark.table(table).limit(20))
