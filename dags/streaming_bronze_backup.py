from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import sys

def create_spark_session():
    """Create Spark session with Delta support"""
    return SparkSession.builder \
        .appName("KafkaToDeltaBronze") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("🚀 Starting Kafka to Delta Lake (Bronze Layer)...")

    # Schema matching the producer
    schema = StructType([
        StructField("vente_id", IntegerType(), True),
        StructField("client_id", IntegerType(), True),
        StructField("produit_id", IntegerType(), True),
        StructField("timestamp", StringType(), True),
        StructField("quantite", IntegerType(), True),
        StructField("montant", DoubleType(), True),
        StructField("client_nom", StringType(), True),
        StructField("produit_nom", StringType(), True),
        StructField("categorie", StringType(), True),
        StructField("pays", StringType(), True),
        StructField("segment", StringType(), True)
    ])

    try:
        # Read from Kafka in BATCH mode
        df_kafka = spark \
            .read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "broker1:19092,broker2:19093,broker3:19094") \
            .option("subscribe", "ventes_stream") \
            .option("startingOffsets", "earliest") \
            .option("endingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()

        print("✅ Connected to Kafka")

        # Parse JSON and enrich with metadata
        df_parsed = df_kafka.select(
            from_json(col("value").cast("string"), schema).alias("data"),
            col("timestamp").alias("kafka_timestamp"),
            col("partition"),
            col("offset")
        ).select("data.*", "kafka_timestamp", "partition", "offset")

        # Add processing columns
        df_enriched = df_parsed \
            .withColumn("date_ingestion", current_timestamp()) \
            .withColumn("jour", to_date(col("timestamp")))

        # Count messages
        message_count = df_enriched.count()
        print(f"📊 Found {message_count} messages in Kafka")

        if message_count > 0:
            # Write to Delta Lake (Bronze layer)
            df_enriched.write \
                .format("delta") \
                .mode("append") \
                .save("/tmp/delta/bronze/ventes_stream")
            
            print(f"✅ Successfully wrote {message_count} records to Bronze layer!")
            
            # Show sample
            print("\n📋 Sample of first 5 records:")
            df_enriched.select("vente_id", "client_nom", "produit_nom", "montant", "pays").show(5, truncate=False)
        else:
            print("⚠️  No messages found in Kafka topic 'ventes_stream'")
            # Create empty bronze structure for pipeline continuity
            df_enriched.limit(0).write \
                .format("delta") \
                .mode("overwrite") \
                .save("/tmp/delta/bronze/ventes_stream")
            print("✅ Created empty Bronze layer structure")

        print("✅ Bronze processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in Bronze processing: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
