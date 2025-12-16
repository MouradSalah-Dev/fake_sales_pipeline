# bronze_to_silver.py
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import *
import sys

def create_spark_session():
    """Create Spark session with Delta support"""
    return SparkSession.builder \
        .appName("BronzeToSilverTransformation") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

def print_separator(title=""):
    """Print formatted separator"""
    if title:
        print("\n" + "=" * 80)
        print(f"📊 {title}")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)

def create_text_chart(data, title, x_label="", y_label=""):
    """Create simple text-based chart"""
    print_separator(f"📈 {title}")
    
    if not data or len(data) == 0:
        print("No data available for chart")
        return
    
    max_value = max([value for _, value in data])
    scale = 50 / max_value if max_value > 0 else 1
    
    for label, value in data:
        bar_length = int(value * scale)
        bar = "█" * bar_length + " " * (50 - bar_length)
        print(f"{label:20} | {bar} | {value:,.2f}")
    
    if x_label or y_label:
        print(f"\nLegend: {x_label} | {y_label}")

def print_statistics(df, df_name="Dataset"):
    """Print comprehensive statistics"""
    print_separator(f"📊 STATISTICS: {df_name}")
    
    # Basic counts
    total_count = df.count()
    print(f"📈 Total Records: {total_count:,}")
    
    if total_count == 0:
        print("⚠️  No data available for statistics")
        return
    
    # Sample data
    print(f"\n🔍 Sample Data (first 3 rows):")
    df.limit(3).show(3, truncate=False, vertical=True)
    
    # Schema info
    print(f"\n📋 Schema Information:")
    for field in df.schema.fields:
        print(f"  • {field.name}: {field.dataType}")

def print_data_quality_report(df, df_name="Dataset"):
    """Print data quality metrics"""
    print_separator(f"🔍 DATA QUALITY REPORT: {df_name}")
    
    total_count = df.count()
    if total_count == 0:
        print("No data for quality report")
        return
    
    # Null checks for key columns
    key_columns = ["vente_id", "client_id", "produit_id", "montant", "timestamp"]
    quality_metrics = []
    
    for col_name in key_columns:
        if col_name in df.columns:
            null_count = df.filter(F.col(col_name).isNull()).count()
            null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
            quality_metrics.append((col_name, null_count, null_percentage))
    
    print("📊 Null Value Analysis:")
    print(f"{'Column':<20} {'Null Count':<15} {'Null %':<10}")
    print("-" * 45)
    for col_name, null_count, null_percentage in quality_metrics:
        status = "✅" if null_percentage == 0 else "⚠️" if null_percentage < 5 else "❌"
        print(f"{status} {col_name:<18} {null_count:<15} {null_percentage:<8.2f}%")
    
    # Value range checks
    print(f"\n📊 Value Range Analysis:")
    numeric_cols = [f for f in df.schema.fields if isinstance(f.dataType, (IntegerType, DoubleType, FloatType, DecimalType))]
    
    for field in numeric_cols[:5]:  # Limit to first 5 numeric columns
        col_name = field.name
        try:
            stats = df.select(
                F.count(col_name).alias("count"),
                F.mean(col_name).alias("mean"),
                F.stddev(col_name).alias("stddev"),
                F.min(col_name).alias("min"),
                F.max(col_name).alias("max")
            ).collect()[0]
            
            print(f"\n📈 {col_name}:")
            print(f"  Count:   {stats['count']:,}")
            print(f"  Mean:    {stats['mean']:.2f}")
            print(f"  StdDev:  {stats['stddev']:.2f}")
            print(f"  Range:   [{stats['min']:.2f} → {stats['max']:.2f}]")
            
            # Check for outliers (values beyond 3 standard deviations)
            if stats['stddev'] and stats['stddev'] > 0:
                upper_limit = stats['mean'] + (3 * stats['stddev'])
                lower_limit = stats['mean'] - (3 * stats['stddev'])
                outlier_count = df.filter((F.col(col_name) > upper_limit) | (F.col(col_name) < lower_limit)).count()
                outlier_percent = (outlier_count / stats['count']) * 100 if stats['count'] > 0 else 0
                print(f"  Outliers: {outlier_count:,} ({outlier_percent:.2f}%)")
                
        except Exception as e:
            print(f"  ⚠️ Could not compute statistics for {col_name}: {e}")

def print_business_insights(df):
    """Print business insights and analytics"""
    print_separator("💡 BUSINESS INSIGHTS")
    
    if df.count() == 0:
        print("No data for business insights")
        return

    # Use Python built-ins explicitly
    py_sum = __builtins__.sum
    py_max = __builtins__.max
    py_min = __builtins__.min

    # 1. Top Products by Revenue
    print("🏆 TOP PRODUCTS BY REVENUE:")
    top_products = df.groupBy("produit_nom", "categorie") \
        .agg(
            F.sum("montant").alias("total_revenue"),
            F.count("*").alias("sales_count"),
            F.avg("montant").alias("avg_price")
        ) \
        .orderBy(F.col("total_revenue").desc()) \
        .limit(10) \
        .collect()
    
    for i, row in enumerate(top_products, 1):
        print(f"  {i:2}. {row['produit_nom'][:30]:30} | "
              f"Revenue: €{row['total_revenue']:8,.2f} | "
              f"Sales: {row['sales_count']:3} | "
              f"Category: {row['categorie']}")

    # 2. Revenue by Country
    print(f"\n🌍 REVENUE BY COUNTRY:")
    country_revenue = df.groupBy("pays") \
        .agg(
            F.sum("montant").alias("total_revenue"),
            F.count("*").alias("sales_count"),
            F.countDistinct("client_id").alias("unique_customers")
        ) \
        .orderBy(F.col("total_revenue").desc()) \
        .collect()
    
    for row in country_revenue:
        print(f"  {row['pays']:15} | "
              f"Revenue: €{row['total_revenue']:8,.2f} | "
              f"Sales: {row['sales_count']:3} | "
              f"Customers: {row['unique_customers']}")

    # 3. Daily Sales Trend
    print(f"\n📅 DAILY SALES TREND:")
    daily_sales = df.groupBy(F.to_date(F.col("timestamp")).alias("date")) \
        .agg(
            F.sum("montant").alias("daily_revenue"),
            F.count("*").alias("daily_sales")
        ) \
        .orderBy("date") \
        .collect()
    
    if daily_sales:
        dates = [row['date'].strftime('%Y-%m-%d') for row in daily_sales]
        revenues = [float(row['daily_revenue']) for row in daily_sales]

        chart_data = list(zip(dates, revenues))[:10]  # Show last 10 days

        max_revenue = py_max(revenues) if revenues else 0

        if max_revenue > 0:
            for date_str, revenue in chart_data:
                bar_length = int((revenue / max_revenue) * 40)
                bar = "█" * bar_length
                print(f"  {date_str} | {bar:40} | €{revenue:8,.2f}")

    # 4. Customer Segmentation
    print(f"\n👥 CUSTOMER SEGMENT ANALYSIS:")
    customer_stats = df.groupBy("segment") \
        .agg(
            F.countDistinct("client_id").alias("customer_count"),
            F.sum("montant").alias("segment_revenue"),
            F.avg("montant").alias("avg_transaction_value")
        ) \
        .orderBy(F.col("segment_revenue").desc()) \
        .collect()
    
    total_revenue = py_sum([row['segment_revenue'] for row in customer_stats])
    
    for row in customer_stats:
        percentage = (row['segment_revenue'] / total_revenue * 100) if total_revenue > 0 else 0
        print(f"  {row['segment']:15} | "
              f"{row['customer_count']:3} customers | "
              f"Revenue: €{row['segment_revenue']:8,.2f} ({percentage:.1f}%) | "
              f"Avg: €{row['avg_transaction_value']:.2f}")

def print_performance_metrics(start_time, end_time, record_counts):
    duration = end_time - start_time
    print("\n" + "="*80)
    print("⏱ PERFORMANCE METRICS")
    print("="*80)
    print(f"Total execution time : {duration:.2f} seconds")
    for layer, count in record_counts.items():
        print(f"{layer.capitalize():15} | {count:,} records")
    print("="*80)

def main():
    import time
    start_time = time.time()
    
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("=" * 80)
    print("🚀 STARTING BRONZE TO SILVER TRANSFORMATION")
    print("=" * 80)

    # Paths
    bronze_path = "/tmp/delta/bronze/ventes_stream"
    silver_path = "/tmp/delta/silver/ventes_clean"
    aggregated_path = "/tmp/delta/silver/ventes_aggreges"
    top_products_path = "/tmp/delta/silver/top_produits"
    hourly_path = "/tmp/delta/silver/hourly_sales"
    
    record_counts = {}

    try:
        # ========== BRONZE DATA LOADING ==========
        print_separator("BRONZE DATA LOADING")
        bronze_df = spark.read.format("delta").load(bronze_path)
        bronze_count = bronze_df.count()
        record_counts['bronze'] = bronze_count
        print(f"✅ Loaded {bronze_count:,} records from Bronze layer")

        if bronze_count == 0:
            print("⚠️  Bronze layer is empty!")
            for path in [silver_path, aggregated_path]:
                bronze_df.limit(0).write.format("delta").mode("overwrite").save(path)
            print("✅ Created empty Silver layer structures")
            spark.stop()
            return
        
        # Print statistics
        print_statistics(bronze_df, "Bronze Layer")
        print_data_quality_report(bronze_df, "Bronze Layer")
        
        # ========== SILVER TRANSFORMATIONS ==========
        print_separator("SILVER TRANSFORMATIONS")
        silver_df = bronze_df \
            .filter(F.col("montant").isNotNull() & (F.col("montant") > 0) & F.col("vente_id").isNotNull()) \
            .withColumn("vente_id", F.col("vente_id").cast("integer")) \
            .withColumn("client_id", F.col("client_id").cast("integer")) \
            .withColumn("produit_id", F.col("produit_id").cast("integer")) \
            .withColumn("quantite", F.col("quantite").cast("integer")) \
            .withColumn("montant", F.round(F.col("montant"), 2)) \
            .withColumn("annee", F.year(F.to_date(F.col("timestamp")))) \
            .withColumn("mois", F.month(F.to_date(F.col("timestamp")))) \
            .withColumn("jour", F.dayofmonth(F.to_date(F.col("timestamp")))) \
            .withColumn("jour_semaine", F.date_format(F.to_date(F.col("timestamp")), "EEEE")) \
            .withColumn("heure", F.hour(F.to_timestamp(F.col("timestamp")))) \
            .withColumn("processed_at", F.current_timestamp())
        
        silver_count = silver_df.count()
        record_counts['silver'] = silver_count
        print(f"✅ Cleaned data: {silver_count:,} records ({bronze_count - silver_count:,} filtered)")
        
        # Print silver statistics
        print_statistics(silver_df, "Silver Layer")
        print_data_quality_report(silver_df, "Silver Layer")
        
        # ========== AGGREGATIONS ==========
        print_separator("AGGREGATED VIEWS CREATION")
        aggregated_df = silver_df.groupBy("categorie", "pays", "mois") \
            .agg(
                F.count("*").alias("nombre_ventes"),
                F.sum("montant").alias("chiffre_affaires"),
                F.avg("montant").alias("panier_moyen"),
                F.countDistinct("client_id").alias("clients_uniques")
            ) \
            .withColumn("chiffre_affaires", F.round(F.col("chiffre_affaires"), 2)) \
            .withColumn("panier_moyen", F.round(F.col("panier_moyen"), 2)) \
            .withColumn("processed_at", F.current_timestamp())
        
        record_counts['aggregated'] = aggregated_df.count()
        print(f"✅ Created {record_counts['aggregated']:,} aggregation rows")
        
        top_products_df = silver_df.groupBy("produit_nom", "categorie") \
            .agg(
                F.count("*").alias("ventes_count"),
                F.sum("montant").alias("revenue_total"),
                F.avg("quantite").alias("quantite_moyenne")
            ) \
            .withColumn("revenue_total", F.round(F.col("revenue_total"), 2)) \
            .withColumn("quantite_moyenne", F.round(F.col("quantite_moyenne"), 2)) \
            .orderBy(F.col("revenue_total").desc())
        
        hourly_sales = silver_df.groupBy("heure") \
            .agg(
                F.count("*").alias("ventes_count"),
                F.sum("montant").alias("revenue_total")
            ) \
            .orderBy("heure")
        
        # ========== BUSINESS INSIGHTS ==========
        print_business_insights(silver_df)
        
        # ========== TEXT VISUALIZATIONS ==========
        category_revenue = silver_df.groupBy("categorie") \
            .agg(F.sum("montant").alias("total_revenue")) \
            .orderBy(F.col("total_revenue").desc()) \
            .collect()
        if category_revenue:
            create_text_chart([(row['categorie'], float(row['total_revenue'])) for row in category_revenue],
                              "REVENUE BY CATEGORY", "Category", "Revenue (€)")
        
        top_products_list = top_products_df.limit(5).collect()
        if top_products_list:
            create_text_chart([(row['produit_nom'][:20], float(row['revenue_total'])) for row in top_products_list],
                              "TOP 5 PRODUCTS BY REVENUE", "Product", "Revenue (€)")
        
        hourly_data = hourly_sales.collect()
        if hourly_data:
            create_text_chart([(f"Hour {row['heure']}", float(row['revenue_total'])) for row in hourly_data],
                              "HOURLY SALES DISTRIBUTION", "Hour", "Revenue (€)")
        
        # ========== WRITE SILVER LAYERS ==========
        for df_to_write, path in [(silver_df, silver_path),
                                  (aggregated_df, aggregated_path),
                                  (top_products_df, top_products_path),
                                  (hourly_sales, hourly_path)]:
            df_to_write.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(path)
            print(f"💾 Written to {path}")
        
        # ========== VERIFICATION ==========
        print_separator("FINAL VERIFICATION")
        for name, path in [("Silver Clean", silver_path), ("Aggregated View", aggregated_path),
                           ("Top Products", top_products_path), ("Hourly Sales", hourly_path)]:
            try:
                count = spark.read.format("delta").load(path).count()
                print(f"  {name:25} | {count:6,} records | ✅ SUCCESS")
            except Exception as e:
                print(f"  {name:25} | N/A | ❌ FAILED: {str(e)[:50]}")
        
        # ========== PERFORMANCE & SUMMARY ==========
        end_time = time.time()
        print_performance_metrics(start_time, end_time, record_counts)
        
    except Exception as e:
        import traceback
        print(f"❌ Error in silver transformation: {e}")
        traceback.print_exc()
        raise
    finally:
        spark.stop()
        print("\n🔚 Spark session stopped")

if __name__ == "__main__":
    main()
