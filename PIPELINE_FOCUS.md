# Sales Pipeline - Focus Guide

## 🎯 Dashboard Overview

### What is the Flask Dashboard?
Your **Flask web application** displays real-time sales analytics by querying the **Silver layer** Delta tables.

**Location**: [app/web/app.py](app/web/app.py)  
**Port**: 5000  
**URL**: http://localhost:5000

### Dashboard Features

```
┌─────────────────────────────────────┐
│    SALES ANALYTICS DASHBOARD        │
├─────────────────────────────────────┤
│  📊 Aggregated Sales                │
│  ├─ Total sales by product          │
│  ├─ Sales by country                │
│  └─ Revenue metrics                 │
│                                      │
│  🏆 Top Products                    │
│  ├─ Top 10 products by revenue      │
│  └─ Product performance ranking     │
│                                      │
│  ⏰ Hourly Sales Trends             │
│  ├─ Sales by hour                   │
│  └─ Time-series visualization       │
└─────────────────────────────────────┘
```

### API Endpoints

The dashboard exposes 4 main APIs:

```
1. GET /api/aggregated_sales
   └─ Returns: [{"produit_nom", "pays", "total_montant", "total_quantite"}]
   └─ Source: /delta/silver/ventes_aggreges

2. GET /api/top_products
   └─ Returns: [{"produit_nom", "total_montant", "rank"}]
   └─ Source: /delta/silver/top_produits

3. GET /api/hourly_sales
   └─ Returns: [{"heure", "total_montant", "total_quantite"}]
   └─ Source: /delta/silver/hourly_sales

4. GET /api/product_by_segment
   └─ Returns: [{"produit", "segment", "montant"}]
   └─ Source: /delta/silver/ventes_aggreges
```

### How It Works

```
User visits http://localhost:5000
        ↓
Flask loads HTML template (index.html)
        ↓
JavaScript fetches from /api/aggregated_sales
        ↓
Flask creates Spark session (lazy load)
        ↓
Spark reads Delta table: /delta/silver/ventes_aggreges
        ↓
Returns JSON response
        ↓
Dashboard displays charts & metrics
```

---

## 🏗️ Why Bronze Layer?

### Purpose: **Store Raw, Unmodified Data**

The Bronze layer is your **single source of truth** - it preserves the original data exactly as it arrives.

### Key Reasons

| Reason | Benefit |
|--------|---------|
| **Immutability** | Original data never changes - provides audit trail |
| **Recovery** | If Silver transformations fail, you can reprocess from Bronze |
| **Schema Evolution** | Handle schema changes without losing historical data |
| **Compliance** | Keep raw data for legal/audit requirements |
| **Debugging** | Compare raw data vs transformed data to find bugs |

### Bronze Layer Structure

```
/delta/bronze/ventes_raw/
│
├─ date=2025-12-22/
│  ├─ part-00000.parquet (messages from 00:00-01:00)
│  ├─ part-00001.parquet (messages from 01:00-02:00)
│  └─ ...
│
└─ _delta_log/  (transaction history)
```

### Bronze Data Example

```json
{
  "vente_id": 1,
  "client_id": 1,
  "produit_id": 101,
  "timestamp": "2025-12-22T10:30:45.123456",
  "quantite": 2,
  "montant": 1799.98,
  "client_nom": "Jean Dupont",
  "produit_nom": "Ordinateur portable",
  "categorie": "Electronique",
  "pays": "France",
  "segment": "Particulier"
}
```

**No transformations applied** - exactly as received from Kafka!

### Bronze Processing Step

**File**: [dags/spark_streaming_delta.py](dags/spark_streaming_delta.py)

```python
# Minimal transformation - just add metadata
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
    .option("subscribe", "ventes_stream") \
    .load()

# Parse JSON + add ingestion timestamp
df_parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("data"),
    current_timestamp().alias("ingestion_time")
)

# Write to Bronze (append mode - immutable)
df_parsed.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("date") \
    .save("/delta/bronze/ventes_raw")
```

---

## 🔄 Why Aggregations in Silver Layer?

### Purpose: **Transform Raw Data Into Business Insights**

The Silver layer **cleans, enriches, and aggregates** Bronze data into useful business metrics.

### Key Reasons

| Reason | Benefit |
|--------|---------|
| **Performance** | Pre-aggregated data = faster dashboard queries |
| **Quality** | Remove duplicates, handle nulls, validate |
| **Business Value** | Convert raw transactions into insights |
| **Denormalization** | Optimize for read patterns (dashboard queries) |
| **Separation of Concerns** | Raw data separate from analytics data |

### Silver Layer Structure

```
/delta/silver/
├─ ventes_clean/          ← Cleaned transactions
├─ ventes_aggreges/       ← GROUP BY product + country
├─ top_produits/          ← Ranked products
└─ hourly_sales/          ← GROUP BY hour
```

### Example: Aggregations in Silver

**Table 1: ventes_aggreges (Product × Country)**

```
produit_nom              | pays     | total_montant | total_quantite
─────────────────────────┼──────────┼───────────────┼────────────────
Ordinateur portable      | France   | 8,999.90      | 10
Ordinateur portable      | Spain    | 5,499.50      | 6
Souris sans fil          | France   | 765.00        | 30
Clavier mecanique        | UK       | 2,250.00      | 30
```

**Query Used**:
```python
ventes_aggreges = df_clean.groupBy(
    "produit_nom", "pays"
).agg(
    F.sum("montant").alias("total_montant"),
    F.sum("quantite").alias("total_quantite")
)
```

**Table 2: top_produits (Top 10 by Revenue)**

```
rank | produit_nom              | total_montant
─────┼──────────────────────────┼───────────────
1    | Ordinateur portable      | 14,499.40
2    | Clavier mecanique        | 3,750.00
3    | Casque audio             | 2,999.50
4    | Souris sans fil          | 765.00
5    | Livre Data Science       | 399.80
```

**Table 3: hourly_sales (Time Series)**

```
heure              | total_montant | total_quantite
───────────────────┼───────────────┼────────────────
2025-12-22 10:00   | 1,500.00      | 20
2025-12-22 11:00   | 2,250.00      | 30
2025-12-22 12:00   | 999.90        | 15
```

### Silver Processing Step

**File**: [dags/bronze_to_silver.py](dags/bronze_to_silver.py)

```python
# Step 1: Read from Bronze
df_bronze = spark.read.format("delta").load("/delta/bronze/ventes_raw")

# Step 2: Data Cleaning
df_clean = df_bronze \
    .dropDuplicates() \
    .filter(col("montant") >= 0) \  # Validation
    .filter(col("client_id").isNotNull()) \  # Quality check
    .withColumn("timestamp", to_timestamp("timestamp"))

# Step 3: Create Aggregations
ventes_aggreges = df_clean.groupBy(
    "produit_nom", "pays"
).agg(
    F.sum("montant").alias("total_montant"),
    F.sum("quantite").alias("total_quantite")
)

# Step 4: Write to Silver
ventes_aggreges.write \
    .format("delta") \
    .mode("overwrite") \  # Replace old aggregations
    .save("/delta/silver/ventes_aggreges")
```

---

## 📊 Complete Pipeline Flow

```
┌─────────────────────┐
│   DATA GENERATION   │
│  50 fake sales      │
│  every run          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ 1️⃣  KAFKA INGESTION (Real-time Stream)      │
│                                              │
│ Topic: ventes_stream                         │
│ Brokers: broker1, broker2, broker3           │
│ Message format: JSON (client + product data) │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ 2️⃣  AIRFLOW ORCHESTRATION                   │
│                                              │
│ DAG: unified_sales_pipeline                  │
│ ├─ check_infrastructure                     │
│ ├─ produce_sales_data → Kafka               │
│ ├─ run_bronze_processing → Spark            │
│ ├─ check_bronze_data_ready                  │
│ ├─ run_silver_processing → Spark            │
│ └─ verify_final_output                      │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ 3️⃣  SPARK BRONZE PROCESSING                │
│                                              │
│ Input: Kafka topic "ventes_stream"          │
│ Processing:                                 │
│ ├─ Connect to Kafka                         │
│ ├─ Parse JSON messages                      │
│ ├─ Add ingestion timestamp                  │
│ └─ Handle streaming checkpoints             │
│                                              │
│ Output: /delta/bronze/ventes_raw            │
│ (Raw, unmodified data)                      │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ 4️⃣  SPARK SILVER PROCESSING                │
│                                              │
│ Input: /delta/bronze/ventes_raw             │
│ Transformations:                            │
│ ├─ Remove duplicates                        │
│ ├─ Validate data (montant >= 0)             │
│ ├─ Standardize timestamps                   │
│ ├─ GROUP BY product + country               │
│ ├─ GROUP BY hour                            │
│ └─ Rank products by revenue                 │
│                                              │
│ Output: /delta/silver/                      │
│ ├─ ventes_clean (cleaned transactions)      │
│ ├─ ventes_aggreges (product × country)      │
│ ├─ top_produits (top 10 products)           │
│ └─ hourly_sales (hourly aggregates)         │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ 5️⃣  FLASK DASHBOARD                        │
│                                              │
│ APIs read from Silver layer:                │
│ ├─ /api/aggregated_sales → ventes_aggreges │
│ ├─ /api/top_products → top_produits         │
│ └─ /api/hourly_sales → hourly_sales         │
│                                              │
│ Port: 5000                                  │
│ URL: http://localhost:5000                  │
│                                              │
│ Displays:                                   │
│ ├─ Sales metrics by product/country         │
│ ├─ Top 10 products ranking                  │
│ └─ Time-series hourly trends                │
└─────────────────────────────────────────────┘
```

---

## ⏱️ Pipeline Timing

```
Step 1: Check Infrastructure        → 5 seconds
Step 2: Produce 50 Sales to Kafka   → 10 seconds
Step 3: Check Data Ready            → 5 seconds
Step 4: Bronze Processing           → 30-60 seconds (Spark job)
Step 5: Silver Processing           → 30-60 seconds (Aggregations)
Step 6: Verify Output               → 5 seconds
─────────────────────────────────────────────────
Total Duration                      → 1.5 - 2.5 minutes
```

---

## 🔍 Key Differences: Bronze vs Silver

| Aspect | Bronze | Silver |
|--------|--------|--------|
| **Data** | Raw, unchanged | Cleaned, aggregated |
| **Source** | Kafka stream | Bronze layer |
| **Write Mode** | Append (immutable) | Overwrite (updated) |
| **Use Case** | Audit trail, recovery | Analytics, reporting |
| **Query Performance** | Slower (raw data) | Fast (pre-aggregated) |
| **Schema** | Schema may evolve | Fixed, validated schema |
| **Data Volume** | Large (all raw records) | Small (aggregated metrics) |

---

## 📈 Why This Architecture?

```
Kafka (streaming)
    ↓
    └─→ Bronze (store everything)
         └─→ Silver (compute aggregations)
             └─→ Dashboard (serve analytics)
```

**Benefits**:
1. ✅ **Scalability**: Kafka handles high-volume streaming
2. ✅ **Reliability**: Bronze layer is immutable backup
3. ✅ **Performance**: Silver aggregations are pre-computed
4. ✅ **Flexibility**: Can reprocess Bronze if needed
5. ✅ **Auditability**: Full data lineage preserved

---

## 🚀 Running Just the Pipeline

```bash
# Start all services
docker-compose up --build -d

# View Airflow logs
docker-compose logs -f airflow-scheduler

# Trigger pipeline manually
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline

# Monitor Spark job
docker-compose logs -f spark-master

# Access dashboard
# Open browser: http://localhost:5000
```

---

## 📊 Expected Dashboard Output

After running the pipeline, you'll see:

**Aggregated Sales** (by product & country):
```
Ordinateur portable    | France      | €8,999.90   | 10 units
Souris sans fil        | France      | €765.00     | 30 units
Clavier mecanique      | UK          | €2,250.00   | 30 units
...
```

**Top Products**:
```
1. Ordinateur portable  | €14,499.40
2. Clavier mecanique    | €3,750.00
3. Casque audio         | €2,999.50
```

**Hourly Sales**:
```
2025-12-22 10:00 | €1,500.00 | 20 units
2025-12-22 11:00 | €2,250.00 | 30 units
2025-12-22 12:00 | €999.90   | 15 units
```

---

## 🎯 Summary

| Component | Purpose | Output |
|-----------|---------|--------|
| **Kafka** | Real-time data ingestion | Stream of sales events |
| **Bronze** | Raw data storage | /delta/bronze/ventes_raw |
| **Silver** | Data transformation & aggregation | /delta/silver/* (analytics-ready) |
| **Dashboard** | Visualization & reporting | Web UI at port 5000 |

**The magic**: Bronze stores everything, Silver computes useful metrics, Dashboard displays them in real-time! 🎉
