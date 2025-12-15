# bronze_to_silver.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
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

def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("=" * 80)
    print("🚀 STARTING BRONZE TO SILVER TRANSFORMATION")
    print("=" * 80)

    # Paths
    bronze_path = "/tmp/delta/bronze/ventes_stream"
    silver_path = "/tmp/delta/silver/ventes_clean"
    
    print(f"📖 Reading from bronze: {bronze_path}")
    print(f"💾 Writing to silver: {silver_path}")

    try:
        # Read from Bronze Delta table
        print("\n📋 Loading data from Bronze layer...")
        bronze_df = spark.read.format("delta").load(bronze_path)
        
        # Show initial stats
        initial_count = bronze_df.count()
        print(f"✅ Loaded {initial_count} records from Bronze layer")
        
        if initial_count == 0:
            print("⚠️  Bronze layer is empty!")
            # Create empty silver table for consistency
            bronze_df.limit(0).write \
                .format("delta") \
                .mode("overwrite") \
                .save(silver_path)
            print("✅ Created empty Silver layer structure")
            spark.stop()
            return
        
        # Show bronze schema and sample
        print("\n📋 Bronze data schema:")
        bronze_df.printSchema()
        
        print("\n📋 Sample of bronze data (first 5 rows):")
        bronze_df.select("vente_id", "client_nom", "produit_nom", "montant", "pays").show(5, truncate=False)
        
        # ========== SILVER TRANSFORMATIONS ==========
        print("\n🔄 Applying silver transformations...")
        
        # 1. Data cleaning and type casting
        silver_df = bronze_df \
            .filter(col("montant").isNotNull()) \
            .filter(col("montant") > 0) \
            .filter(col("vente_id").isNotNull()) \
            .withColumn("vente_id", col("vente_id").cast("integer")) \
            .withColumn("client_id", col("client_id").cast("integer")) \
            .withColumn("produit_id", col("produit_id").cast("integer")) \
            .withColumn("quantite", col("quantite").cast("integer")) \
            .withColumn("montant", round(col("montant"), 2))
        
        # 2. Add derived columns
        silver_df = silver_df \
            .withColumn("annee", year(to_date(col("timestamp")))) \
            .withColumn("mois", month(to_date(col("timestamp")))) \
            .withColumn("jour", dayofmonth(to_date(col("timestamp")))) \
            .withColumn("jour_semaine", date_format(to_date(col("timestamp")), "EEEE")) \
            .withColumn("heure", hour(to_timestamp(col("timestamp")))) \
            .withColumn("processed_at", current_timestamp())
        
        # 3. Create aggregated view (for analytics)
        print("\n📊 Creating aggregated view for analytics...")
        
        # Aggregation 1: Sales by category and country
        aggregated_df = silver_df.groupBy("categorie", "pays", "mois") \
            .agg(
                count("*").alias("nombre_ventes"),
                sum("montant").alias("chiffre_affaires"),
                avg("montant").alias("panier_moyen"),
                countDistinct("client_id").alias("clients_uniques")
            ) \
            .withColumn("chiffre_affaires", round(col("chiffre_affaires"), 2)) \
            .withColumn("panier_moyen", round(col("panier_moyen"), 2)) \
            .withColumn("processed_at", current_timestamp())
        
        # Aggregation 2: Top products
        top_products_df = silver_df.groupBy("produit_nom", "categorie") \
            .agg(
                count("*").alias("ventes_count"),
                sum("montant").alias("revenue_total"),
                avg("quantite").alias("quantite_moyenne")
            ) \
            .withColumn("revenue_total", round(col("revenue_total"), 2)) \
            .withColumn("quantite_moyenne", round(col("quantite_moyenne"), 2)) \
            .orderBy(col("revenue_total").desc())
        
        # ========== WRITE SILVER LAYERS ==========
        
        # Write cleaned transactions (Silver Clean layer)
        print(f"\n💾 Writing cleaned transactions to: {silver_path}")
        silver_df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .save(silver_path)
        
        # Write aggregated view (Silver Aggregated layer)
        aggregated_path = "/tmp/delta/silver/ventes_aggreges"
        print(f"💾 Writing aggregated view to: {aggregated_path}")
        aggregated_df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .save(aggregated_path)
        
        # Write top products view
        top_products_path = "/tmp/delta/silver/top_produits"
        print(f"💾 Writing top products to: {top_products_path}")
        top_products_df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .save(top_products_path)
        
        # ========== VERIFICATION ==========
        print("\n" + "=" * 80)
        print("✅ VERIFICATION")
        print("=" * 80)
        
        # Verify cleaned data
        silver_verify = spark.read.format("delta").load(silver_path)
        silver_count = silver_verify.count()
        print(f"  Cleaned transactions: {silver_count} records")
        
        # Verify aggregated data
        agg_verify = spark.read.format("delta").load(aggregated_path)
        agg_count = agg_verify.count()
        print(f"  Aggregated view: {agg_count} aggregation rows")
        
        # Show samples
        print("\n📋 Sample of cleaned silver data:")
        silver_verify.select("vente_id", "client_nom", "produit_nom", "montant", "pays", "annee", "mois").show(5, truncate=False)
        
        print("\n📋 Sample of aggregated data:")
        agg_verify.show(5)
        
        print("\n" + "=" * 80)
        print("🎉 SILVER TRANSFORMATION COMPLETED SUCCESSFULLY")
        print(f"   • Cleaned {initial_count} → {silver_count} records")
        print(f"   • Created {agg_count} aggregation rows")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error in silver transformation: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()