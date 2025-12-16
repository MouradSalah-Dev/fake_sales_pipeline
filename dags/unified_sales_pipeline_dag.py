from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.sensors.python import PythonSensor
from datetime import datetime, timedelta
import json
import time
import random
import subprocess
import os
from kafka import KafkaProducer

# Configuration
KAFKA_TOPIC = "ventes_stream"
KAFKA_BROKER_URL = "broker1:19092,broker2:19093,broker3:19094"

# Sample data
PRODUITS = [
    {"id": 101, "nom": "Ordinateur portable", "categorie": "Electronique", "prix": 899.99},
    {"id": 102, "nom": "Souris sans fil", "categorie": "Electronique", "prix": 25.50},
    {"id": 103, "nom": "Clavier mecanique", "categorie": "Electronique", "prix": 75.00},
    {"id": 104, "nom": "Casque audio", "categorie": "Electronique", "prix": 59.99},
    {"id": 105, "nom": "Livre Data Science", "categorie": "Livre", "prix": 19.99},
]

CLIENTS = [
    {"id": 1, "nom": "Jean Dupont", "pays": "France", "segment": "Particulier"},
    {"id": 2, "nom": "Maria Garcia", "pays": "Espagne", "segment": "Particulier"},
    {"id": 3, "nom": "John Smith", "pays": "UK", "segment": "Entreprise"},
    {"id": 4, "nom": "Anna Mueller", "pays": "Allemagne", "segment": "Particulier"},
    {"id": 5, "nom": "Paolo Rossi", "pays": "Italie", "segment": "Entreprise"},
]

def check_infrastructure():
    """Check that all services are ready"""
    print("🔍 Checking infrastructure...")
    
    # Check Kafka connectivity
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL.split(','),
            max_block_ms=3000
        )
        producer.close()
        print("✅ Kafka brokers are reachable")
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")
        raise
    
    # Check Spark master
    try:
        result = subprocess.run([
            'docker', 'exec', 'spark-master', 
            'curl', '-s', 'http://localhost:8080'
        ], capture_output=True, timeout=10)
        if result.returncode == 0:
            print("✅ Spark master is reachable")
        else:
            raise Exception("Spark master not responding")
    except Exception as e:
        print(f"❌ Spark master check failed: {e}")
        raise
    
    print("✅ All infrastructure services are ready")

def produce_sales_data():
    """Produce sales data to Kafka"""
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL.split(','),
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        max_block_ms=5000
    )

    print("🚀 Starting Kafka producer...")
    
    # Generate 50 sales for better testing
    for i in range(50):
        client = random.choice(CLIENTS)
        produit = random.choice(PRODUITS)
        quantite = random.randint(1, 3)
        montant = round(quantite * produit["prix"], 2)
        
        timestamp = datetime.now().isoformat()

        vente = {
            "vente_id": i + 1,
            "client_id": client["id"],
            "produit_id": produit["id"],
            "timestamp": timestamp,
            "quantite": quantite,
            "montant": montant,
            "client_nom": client["nom"],
            "produit_nom": produit["nom"],
            "categorie": produit["categorie"],
            "pays": client["pays"],
            "segment": client["segment"]
        }

        producer.send(KAFKA_TOPIC, value=vente)
        print(f"✅ Sale {i+1}: {vente['produit_nom']} - {vente['montant']}€")
        time.sleep(0.2)  # Smaller delay for faster production

    producer.flush()
    producer.close()
    print(f"✅ Production completed: 50 sales sent to Kafka topic '{KAFKA_TOPIC}'")



def run_spark_bronze_processing():
    """Run Spark job to process Kafka data to Bronze layer"""
    
    spark_script = '/app/dags/spark_streaming_delta.py'
    
    cmd = [
        'docker', 'exec', 'spark-master',
        'spark-submit',
        '--master', 'spark://spark-master:7077',
        '--jars', '/opt/spark/jars/delta-spark_2.12-3.2.0.jar,/opt/spark/jars/delta-storage-3.2.0.jar,/opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.0.jar,/opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.0.jar,/opt/spark/jars/kafka-clients-3.4.1.jar,/opt/spark/jars/commons-pool2-2.11.1.jar',
        '--conf', 'spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension',
        '--conf', 'spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog',
        '--conf', 'spark.driver.memory=1g',
        '--conf', 'spark.executor.memory=1g',
        spark_script
    ]
    
    print(f"🚀 Submitting Bronze Spark job: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # Increased to 5 minutes
        )
        
        # Always log outputs for debugging
        print(f"🔍 Return code: {result.returncode}")
        
        # Show more output for debugging
        if result.stdout:
            print("="*80)
            print("STDOUT FULL (last 2000 chars):")
            print("="*80)
            print(result.stdout[-2000:])  # Show last 2000 chars
            print("="*80)
        
        if result.stderr:
            print("="*80)
            print("STDERR FULL (last 2000 chars):")
            print("="*80)
            print(result.stderr[-2000:])  # Show last 2000 chars
            print("="*80)
        
        # Check if the job actually succeeded by looking for success messages
        combined_output = (result.stdout or "") + (result.stderr or "")
        
        # Check for success indicators
        success_indicators = [
            "Bronze processing completed successfully",
            "Successfully wrote",
            "Data integrity verified",
            "Created empty Bronze layer structure"
        ]
        
        # Check for real failure indicators (beyond just warnings)
        failure_indicators = [
            "Exception in thread",
            "ERROR Executor:",
            "Caused by:",
            "java.lang.",
            "py4j.protocol.Py4JJavaError",
            "Traceback (most recent call last):",
            "at org.apache.spark"
        ]
        
        has_success = any(indicator in combined_output for indicator in success_indicators)
        has_real_failure = any(indicator in combined_output for indicator in failure_indicators)
        
        if result.returncode == 0:
            print("✅ Bronze Spark job completed successfully (return code 0)")
            return True
        elif has_success and not has_real_failure:
            # Job printed success message but had non-zero exit (common with Spark warnings)
            print(f"⚠️  Spark returned code {result.returncode} but job appears successful")
            print("✅ Treating as success (likely warnings or cleanup operations)")
            return True
        else:
            # Has real error
            print(f"❌ Bronze Spark job failed")
            
            # Extract the actual error from the output
            error_lines = []
            lines = combined_output.split('\n')
            for i, line in enumerate(lines):
                if any(fail_indicator in line for fail_indicator in failure_indicators):
                    # Capture error line and context (5 lines before and after)
                    start = max(0, i - 5)
                    end = min(len(lines), i + 6)
                    error_lines.extend(lines[start:end])
                    error_lines.append("..." if i + 6 < len(lines) else "")
            
            if error_lines:
                error_msg = '\n'.join(error_lines[-50:])  # Last 50 lines of error context
            else:
                error_msg = combined_output[-1500:]  # Last 1500 chars if no specific error found
            
            raise Exception(f"Bronze Spark job failed:\n{error_msg}")
            
    except subprocess.TimeoutExpired:
        print("❌ Bronze Spark job timed out")
        raise
    except Exception as e:
        print(f"❌ Error submitting Bronze Spark job: {e}")
        raise

def check_bronze_data_exists():
    """Check if Bronze layer data exists"""
    bronze_path = "/tmp/delta/bronze/ventes_stream"
    
    # First check locally in Airflow container
    if os.path.exists(bronze_path) and os.path.isdir(bronze_path):
        try:
            files = os.listdir(bronze_path)
            has_data = any(f.endswith('.parquet') or f == '_delta_log' for f in files)
            if has_data:
                print(f"✅ Bronze data available locally at {bronze_path}")
                return True
        except Exception as e:
            print(f"❌ Error checking bronze data: {e}")
    
    # If not found locally, check in Spark container
    try:
        print("Checking bronze data in Spark container...")
        result = subprocess.run([
            'docker', 'exec', 'spark-master',
            'bash', '-c', f'ls -la {bronze_path} 2>/dev/null || echo "Directory not found"'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and '_delta_log' in result.stdout:
            print(f"✅ Bronze data available in Spark container")
            return True
    except Exception as e:
        print(f"❌ Error checking bronze data in container: {e}")
    
    print("⏳ Waiting for Bronze data...")
    return False

def run_spark_silver_processing():
    """Run Spark job to process Bronze to Silver layer"""
    
    spark_script = '/app/dags/bronze_to_silver.py'
    
    cmd = [
        'docker', 'exec', 'spark-master',
        'spark-submit',
        '--master', 'spark://spark-master:7077',
        '--jars', '/opt/spark/jars/delta-spark_2.12-3.2.0.jar,/opt/spark/jars/delta-storage-3.2.0.jar,/opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.0.jar,/opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.0.jar,/opt/spark/jars/kafka-clients-3.4.1.jar,/opt/spark/jars/commons-pool2-2.11.1.jar',
        '--conf', 'spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension',
        '--conf', 'spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog',
        '--conf', 'spark.driver.memory=1g',
        '--conf', 'spark.executor.memory=1g',
        spark_script
    ]
    
    print(f"🚀 Submitting Silver Spark job: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # Increased to 5 minutes
        )
        
        # Show output for debugging
        print(f"🔍 Return code: {result.returncode}")
        
        if result.stdout:
            print("="*80)
            print("STDOUT FULL (last 2000 chars):")
            print("="*80)
            print(result.stdout[-2000:])
            print("="*80)
        
        if result.stderr:
            print("="*80)
            print("STDERR FULL (last 2000 chars):")
            print("="*80)
            print(result.stderr[-2000:])
            print("="*80)
        
        # Check for success indicators
        combined_output = (result.stdout or "") + (result.stderr or "")
        
        success_indicators = [
            "SILVER TRANSFORMATION COMPLETED SUCCESSFULLY",
            "Successfully wrote",
            "Verification:",
            "Created empty Silver layer structure"
        ]
        
        failure_indicators = [
            "Exception in thread",
            "ERROR Executor:",
            "Caused by:",
            "java.lang.",
            "py4j.protocol.Py4JJavaError",
            "Traceback (most recent call last):"
        ]
        
        has_success = any(indicator in combined_output for indicator in success_indicators)
        has_real_failure = any(indicator in combined_output for indicator in failure_indicators)
        
        if result.returncode == 0:
            print("✅ Silver Spark job completed successfully (return code 0)")
            return True
        elif has_success and not has_real_failure:
            print(f"⚠️  Spark returned code {result.returncode} but job appears successful")
            print("✅ Treating as success")
            return True
        else:
            print(f"❌ Silver Spark job failed with return code {result.returncode}")
            
            # Extract error
            error_lines = []
            lines = combined_output.split('\n')
            for i, line in enumerate(lines):
                if any(fail_indicator in line for fail_indicator in failure_indicators):
                    start = max(0, i - 5)
                    end = min(len(lines), i + 6)
                    error_lines.extend(lines[start:end])
                    error_lines.append("..." if i + 6 < len(lines) else "")
            
            if error_lines:
                error_msg = '\n'.join(error_lines[-50:])
            else:
                error_msg = combined_output[-2000:]
            
            raise Exception(f"Silver Spark job failed:\n{error_msg}")
            
    except subprocess.TimeoutExpired:
        print("❌ Silver Spark job timed out")
        raise
    except Exception as e:
        print(f"❌ Error submitting Silver Spark job: {e}")
        raise

    
def verify_final_output():
    """Verify that both Bronze and Silver layers were created successfully"""
    bronze_path = "/tmp/delta/bronze/ventes_stream"
    silver_path = "/tmp/delta/silver/ventes_aggreges"
    
    print(f"🔍 Verifying output at: {bronze_path}")
    print(f"🔍 Verifying output at: {silver_path}")
    
    # Check locally first
    bronze_exists = os.path.exists(bronze_path) and os.path.isdir(bronze_path)
    silver_exists = os.path.exists(silver_path) and os.path.isdir(silver_path)
    
    # If not found locally, check in Spark container
    if not bronze_exists or not silver_exists:
        print("Checking in Spark container...")
        try:
            # Check bronze
            result = subprocess.run([
                'docker', 'exec', 'spark-master',
                'bash', '-c', f'ls -la {bronze_path} 2>/dev/null | head -5'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                bronze_exists = True
                print(f"✅ Bronze found in container")
            
            # Check silver
            result = subprocess.run([
                'docker', 'exec', 'spark-master',
                'bash', '-c', f'ls -la {silver_path} 2>/dev/null | head -5'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                silver_exists = True
                print(f"✅ Silver found in container")
                
        except Exception as e:
            print(f"⚠️ Error checking container: {e}")
    
    if bronze_exists:
        try:
            if os.path.exists(bronze_path):
                bronze_files = os.listdir(bronze_path)
            else:
                # Get from container
                result = subprocess.run([
                    'docker', 'exec', 'spark-master',
                    'bash', '-c', f'ls {bronze_path} 2>/dev/null | wc -l'
                ], capture_output=True, text=True)
                bronze_files_count = result.stdout.strip() if result.returncode == 0 else "?"
                bronze_files = [f"Found {bronze_files_count} files in container"]
            print(f"✅ Bronze layer: {len(bronze_files)} files/folders")
        except Exception as e:
            print(f"⚠️ Error listing bronze: {e}")
    else:
        print("❌ Bronze layer missing")
        
    if silver_exists:
        try:
            if os.path.exists(silver_path):
                silver_files = os.listdir(silver_path)
            else:
                result = subprocess.run([
                    'docker', 'exec', 'spark-master',
                    'bash', '-c', f'ls {silver_path} 2>/dev/null | wc -l'
                ], capture_output=True, text=True)
                silver_files_count = result.stdout.strip() if result.returncode == 0 else "?"
                silver_files = [f"Found {silver_files_count} files in container"]
            print(f"✅ Silver layer: {len(silver_files)} files/folders")
        except Exception as e:
            print(f"⚠️ Error listing silver: {e}")
    else:
        print("❌ Silver layer missing")
    
    success = bronze_exists and silver_exists
    if success:
        print("🎉 Pipeline completed successfully! All data layers created.")
    else:
        print("⚠️  Pipeline completed with warnings - some layers missing")
    
    return success

def cleanup_temp_files():
    """Optional cleanup of temporary files"""
    try:
        import shutil
        temp_dirs = ["/tmp/delta/bronze", "/tmp/delta/silver"]
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"🧹 Cleaned up: {temp_dir}")
                
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'email_on_failure': False,
    'email_on_retry': False,
}

dag = DAG(
    'unified_sales_pipeline',
    default_args=default_args,
    description='Unified sales data pipeline: Kafka -> Bronze -> Silver',
    schedule_interval=None,
    catchup=False,
    tags=['sales', 'pipeline', 'kafka', 'spark', 'delta'],
    max_active_runs=1,
)

# Define tasks
start_task = DummyOperator(task_id='start_pipeline', dag=dag)

check_infra_task = PythonOperator(
    task_id='check_infrastructure',
    python_callable=check_infrastructure,
    dag=dag,
)

produce_data_task = PythonOperator(
    task_id='produce_sales_data',
    python_callable=produce_sales_data,
    dag=dag,
)

bronze_processing_task = PythonOperator(
    task_id='run_bronze_processing',
    python_callable=run_spark_bronze_processing,
    dag=dag,
)

check_bronze_sensor = PythonSensor(
    task_id='check_bronze_data_ready',
    python_callable=check_bronze_data_exists,
    timeout=300,
    mode='reschedule',
    poke_interval=20,
    dag=dag,
)

silver_processing_task = PythonOperator(
    task_id='run_silver_processing',
    python_callable=run_spark_silver_processing,
    dag=dag,
)

verify_output_task = PythonOperator(
    task_id='verify_final_output',
    python_callable=verify_final_output,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='optional_cleanup',
    python_callable=cleanup_temp_files,
    dag=dag,
)

end_task = DummyOperator(task_id='end_pipeline', dag=dag)

# Define workflow
start_task >> check_infra_task >> produce_data_task >> bronze_processing_task
bronze_processing_task >> check_bronze_sensor >> silver_processing_task
silver_processing_task >> verify_output_task >> cleanup_task >> end_task