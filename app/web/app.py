from flask import Flask, jsonify, render_template
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import *
import os

app = Flask(__name__)

# Function to create Spark session
def create_spark_session():
    return SparkSession.builder \
        .appName("SalesDashboardAPI") \
        .config("spark.jars", "/opt/spark/jars/delta-spark_2.12-3.2.0.jar,/opt/spark/jars/delta-storage-3.2.0.jar") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.driver.memory", "512m") \
        .config("spark.ui.enabled", "false") \
        .master("local[*]") \
        .getOrCreate()

# Initialize Spark session (can be lazy loaded for performance)
spark = None

def get_spark_session():
    global spark
    if spark is None:
        spark = create_spark_session()
        spark.sparkContext.setLogLevel("WARN")
    return spark

# Define Delta table paths
DELTA_BASE_PATH = "/tmp/delta/silver"
AGGREGATED_SALES_PATH = os.path.join(DELTA_BASE_PATH, "ventes_aggreges")
TOP_PRODUCTS_PATH = os.path.join(DELTA_BASE_PATH, "top_produits")
HOURLY_SALES_PATH = os.path.join(DELTA_BASE_PATH, "hourly_sales")
SILVER_CLEAN_PATH = os.path.join(DELTA_BASE_PATH, "ventes_clean")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/aggregated_sales")
def get_aggregated_sales():
    spark = get_spark_session()
    try:
        df = spark.read.format("delta").load(AGGREGATED_SALES_PATH)
        data = df.limit(100).toPandas().to_dict(orient="records") # Limit for display
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to load aggregated sales data"}), 500

@app.route("/api/top_products")
def get_top_products():
    spark = get_spark_session()
    try:
        df = spark.read.format("delta").load(TOP_PRODUCTS_PATH)
        data = df.limit(100).toPandas().to_dict(orient="records")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to load top products data"}), 500

@app.route("/api/hourly_sales")
def get_hourly_sales():
    spark = get_spark_session()
    try:
        df = spark.read.format("delta").load(HOURLY_SALES_PATH)
        data = df.limit(100).toPandas().to_dict(orient="records")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to load hourly sales data"}), 500

@app.route("/api/overall_statistics")
def get_overall_statistics():
    spark = get_spark_session()
    try:
        silver_df = spark.read.format("delta").load(SILVER_CLEAN_PATH)
        total_revenue = silver_df.agg(F.sum("montant").alias("total_revenue")).collect()[0]["total_revenue"]
        total_sales = silver_df.count()
        unique_products = silver_df.select(F.countDistinct("produit_id").alias("unique_products")).collect()[0]["unique_products"]
        unique_customers = silver_df.select(F.countDistinct("client_id").alias("unique_customers")).collect()[0]["unique_customers"]

        return jsonify({
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "unique_products": unique_products,
            "unique_customers": unique_customers
        })
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to load overall statistics"}), 500

@app.route("/api/revenue_by_country")
def get_revenue_by_country():
    spark = get_spark_session()
    try:
        df = spark.read.format("delta").load(SILVER_CLEAN_PATH)
        country_revenue = df.groupBy("pays") \
            .agg(F.sum("montant").alias("total_revenue")) \
            .orderBy(F.col("total_revenue").desc()) \
            .limit(100).toPandas().to_dict(orient="records")
        return jsonify(country_revenue)
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to load revenue by country data"}), 500

@app.route("/api/customer_segmentation")
def get_customer_segmentation():
    spark = get_spark_session()
    try:
        df = spark.read.format("delta").load(SILVER_CLEAN_PATH)
        customer_stats = df.groupBy("segment") \
            .agg(
                F.countDistinct("client_id").alias("customer_count"),
                F.sum("montant").alias("segment_revenue"),
                F.avg("montant").alias("avg_transaction_value")
            ) \
            .orderBy(F.col("segment_revenue").desc()) \
            .limit(100).toPandas().to_dict(orient="records")
        return jsonify(customer_stats)
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to load customer segmentation data"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

