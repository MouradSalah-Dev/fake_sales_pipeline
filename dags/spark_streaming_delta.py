from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
import stat

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

def ensure_directory_permissions(path):
    """Ensure directory exists with proper permissions (777)"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        
        # Set permissions to 777 (read, write, execute for all)
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        
        # Also set permissions on parent directories
        parent = os.path.dirname(path)
        while parent and parent != '/':
            if os.path.exists(parent):
                os.chmod(parent, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            parent = os.path.dirname(parent)
            
        print(f"✅ Set permissions for: {path}")
        return True
    except Exception as e:
        print(f"⚠️ Warning setting permissions for {path}: {e}")
        return False

def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("🚀 Starting Kafka to Delta Lake (Bronze Layer)...")
    
    # Log user info for debugging
    import getpass
    print(f"Spark running as user: {getpass.getuser()}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check and fix directory permissions
    bronze_path = "/tmp/delta/bronze/ventes_stream"
    ensure_directory_permissions(bronze_path)
    
    # Also ensure parent directories have proper permissions
    ensure_directory_permissions("/tmp/delta")
    ensure_directory_permissions("/tmp/delta/bronze")

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
            print(f"📝 Writing to: {bronze_path}")
            print(f"📝 Directory permissions: {oct(os.stat(bronze_path).st_mode)}")
            
            # Write in smaller batches to avoid permission issues
            df_enriched.write \
                .format("delta") \
                .mode("overwrite") \
                .save(bronze_path)
            
            print(f"✅ Successfully wrote {message_count} records to Bronze layer!")
            
            # Show sample
            print("\n📋 Sample of first 5 records:")
            df_enriched.select("vente_id", "client_nom", "produit_nom", "montant", "pays").show(5, truncate=False)
            
            # Verify write was successful
            try:
                delta_df = spark.read.format("delta").load(bronze_path)
                read_count = delta_df.count()
                print(f"✅ Verification: Read back {read_count} records from Delta table")
                if read_count == message_count:
                    print("🎉 Data integrity verified!")
                else:
                    print(f"⚠️ Count mismatch: wrote {message_count}, read {read_count}")
            except Exception as e:
                print(f"⚠️ Could not verify Delta table: {e}")
        else:
            print("⚠️  No messages found in Kafka topic 'ventes_stream'")
            # Create empty bronze structure for pipeline continuity
            df_enriched.limit(0).write \
                .format("delta") \
                .mode("overwrite") \
                .save(bronze_path)
            print("✅ Created empty Bronze layer structure")

        print("✅ Bronze processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in Bronze processing: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()