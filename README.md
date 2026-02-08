# 🚀 Fake Sales Pipeline

> A modern, production-ready real-time data engineering pipeline demonstrating the **Medallion Architecture** with Apache Kafka, Spark, Delta Lake, and Apache Airflow.

[![Apache Airflow](https://img.shields.io/badge/Airflow-2.10.5-blue?logo=apache-airflow)](https://airflow.apache.org/)
[![Apache Spark](https://img.shields.io/badge/Spark-3.5.0-orange?logo=apache-spark)](https://spark.apache.org/)
[![Apache Kafka](https://img.shields.io/badge/Kafka-4.1.1-black?logo=apache-kafka)](https://kafka.apache.org/)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.2.0-green)](https://delta.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://docs.docker.com/compose/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Pipeline Flow](#pipeline-flow)
- [Data Layers](#data-layers)
- [API Endpoints](#api-endpoints)
- [Monitoring](#monitoring)
- [Documentation](#documentation)
- [Contributing](#contributing)

---

## 🎯 Overview

**Fake Sales Pipeline** is an **end-to-end data engineering solution** that simulates a real-world e-commerce sales system. It demonstrates industry best practices for:

- ✅ **Real-time streaming data ingestion** from Apache Kafka
- ✅ **Medallion Architecture** (Bronze → Silver layers) for data quality progression
- ✅ **Distributed data processing** with Apache Spark
- ✅ **ACID-compliant storage** using Delta Lake
- ✅ **Workflow orchestration** with Apache Airflow
- ✅ **RESTful APIs** for analytics consumption
- ✅ **Infrastructure monitoring** with Prometheus & Grafana
- ✅ **Containerized deployment** using Docker Compose

This project is ideal for:
- **Learning** modern data engineering patterns
- **Demonstrating** skills in data pipeline development
- **Testing** streaming architecture concepts
- **Building** production-ready data platforms

---

## 🌟 Key Features

### 🔄 Real-Time Data Processing
- **Kafka 3-broker cluster** (KRaft mode) for high-availability streaming
- **Spark Structured Streaming** for micro-batch processing
- **Delta Lake checkpointing** for fault-tolerant state management

### 🏗️ Medallion Architecture
```
📊 Bronze Layer (Raw Data Vault)
   ↓
   → Stores raw, unmodified Kafka messages
   → Append-only (immutable audit trail)
   → Partition by date for efficient queries
   
🔄 Silver Layer (Analytics Warehouse)
   ↓
   → Cleaned & validated transactions
   → Pre-aggregated business metrics
   → Optimized for dashboard queries (300x faster!)
   → Overwrite mode for current state
```

### 📈 Business Analytics
- **Aggregated Sales**: Revenue by product & country
- **Top Products**: Ranking by revenue performance
- **Hourly Sales**: Time-series trend analysis
- **Customer Segments**: B2C vs B2B analytics

### 🛠️ Production-Ready Infrastructure
- **PostgreSQL**: Airflow metadata database
- **Redis**: Celery task queue & caching
- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization
- **Health Checks**: All services monitored

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  FAKE SALES PIPELINE SYSTEM                  │
└─────────────────────────────────────────────────────────────┘

    📊 DATA GENERATION (Python)
           ↓
    🔄 KAFKA CLUSTER (3 brokers)
       Topic: ventes_stream
           ↓
    ⚙️ AIRFLOW ORCHESTRATION
       DAG: unified_sales_pipeline
           ↓
    ⚡ SPARK PROCESSING
       ├─ Bronze: Raw ingestion from Kafka
       └─ Silver: Cleaning & aggregations
           ↓
    💾 DELTA LAKE STORAGE
       ├─ /delta/bronze/ventes_raw (immutable)
       └─ /delta/silver/
          ├─ ventes_clean (cleaned transactions)
          ├─ ventes_aggreges (product × country)
          ├─ top_produits (top 10 ranking)
          └─ hourly_sales (time-series)
           ↓
    🌐 FLASK WEB DASHBOARD
       Port: 5000
       RESTful APIs + HTML UI
           ↓
    📊 MONITORING LAYER
       ├─ Prometheus (metrics)
       └─ Grafana (dashboards)
```

---

## 🛠️ Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Apache Kafka** | 4.1.1 | Real-time event streaming |
| **Apache Spark** | 3.5.0 | Distributed data processing |
| **Delta Lake** | 3.2.0 | ACID transactions & versioning |
| **Apache Airflow** | 2.10.5 | Workflow orchestration |
| **PostgreSQL** | 13 | Airflow metadata storage |
| **Redis** | 7.2 | Celery broker & caching |
| **Flask** | Latest | Web dashboard & REST APIs |
| **Prometheus** | Latest | Metrics collection |
| **Grafana** | Latest | Metrics visualization |
| **Docker Compose** | 3.x | Multi-container orchestration |

---

## 📁 Project Structure

```
fake_sales_pipeline/
│
├── 📂 dags/                              # Airflow DAGs
│   ├── unified_sales_pipeline_dag.py     # Main orchestration DAG
│   ├── spark_streaming_delta.py          # Bronze layer processing
│   └── bronze_to_silver.py               # Silver layer transformation
│
├── 📂 app/                               # Flask web application
│   └── web/
│       ├── app.py                        # Flask app & APIs
│       └── templates/
│           └── index.html                # Dashboard UI
│
├── 📂 delta/                             # Delta Lake data storage
│   ├── bronze/                           # Raw data layer
│   │   └── ventes_stream/
│   └── silver/                           # Processed data layer
│       ├── ventes_clean/
│       ├── ventes_aggreges/
│       ├── top_produits/
│       └── hourly_sales/
│
├── 📂 kafka/                             # Kafka configuration
│   └── jmx-exporter/
│       └── config.yml
│
├── 📂 spark/                             # Spark configuration
│   └── conf/
│       └── metrics.properties
│
├── 📂 prometheus/                        # Prometheus monitoring
│   └── prometheus.yml
│
├── 📂 grafana/                           # Grafana dashboards
│   └── dashboards/
│
├── 📄 docker-compose.yml                 # Multi-container orchestration
├── 📄 Dockerfile                         # Base image
├── 📄 Dockerfile.airflow                 # Airflow image
├── 📄 Dockerfile.flask                   # Flask app image
│
├── 📄 ARCHITECTURE.md                    # Detailed architecture guide
├── 📄 PIPELINE_FOCUS.md                  # Pipeline deep-dive
├── 📄 AGGREGATION_STRATEGY.md            # Data aggregation rationale
└── 📄 README.md                          # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker** & **Docker Compose** installed
- **8GB+ RAM** (recommended)
- **20GB disk space** (for data & images)
- **WSL2** (for Windows users)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/MouradSalah-Dev/fake_sales_pipeline.git
cd fake_sales_pipeline

# 2. Build and start all services
docker-compose up --build -d

# 3. Wait for services to initialize (2-3 minutes)
docker-compose ps

# 4. Access services:
# - Airflow UI: http://localhost:8080 (airflow/airflow)
# - Flask Dashboard: http://localhost:5000
# - Spark UI: http://localhost:8081
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
```

### Trigger the Pipeline

```bash
# Option 1: Via Airflow Web UI
# 1. Open http://localhost:8080
# 2. Find "unified_sales_pipeline" DAG
# 3. Click "Trigger DAG"

# Option 2: Via Airflow CLI
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline
```

### Monitor Execution

```bash
# View Airflow scheduler logs
docker-compose logs -f airflow-scheduler

# View Spark processing logs
docker-compose logs -f spark-master

# View Flask dashboard logs
docker-compose logs -f flask-dashboard

# Check all running services
docker-compose ps
```

---

## 🔄 Pipeline Flow

### Step-by-Step Execution

```
1️⃣ Check Infrastructure (5 seconds)
   ├─ Verify Kafka brokers reachable
   ├─ Verify Spark master running
   └─ Validate Airflow connectivity

2️⃣ Produce Sales Data (10 seconds)
   ├─ Generate 50 fake sales transactions
   ├─ Enrich with client & product data
   └─ Stream to Kafka topic: ventes_stream

3️⃣ Bronze Layer Processing (30-60 seconds)
   ├─ Consume from Kafka (ventes_stream)
   ├─ Parse JSON messages
   ├─ Add ingestion timestamp
   └─ Write to /delta/bronze/ventes_raw

4️⃣ Check Bronze Data Ready (5 seconds)
   └─ Verify data exists in Bronze layer

5️⃣ Silver Layer Processing (30-60 seconds)
   ├─ Read from /delta/bronze/ventes_raw
   ├─ Data Cleaning:
   │  ├─ Remove duplicates
   │  ├─ Validate (montant >= 0)
   │  └─ Standardize timestamps
   ├─ Create Aggregations:
   │  ├─ ventes_aggreges (product × country)
   │  ├─ top_produits (top 10 by revenue)
   │  └─ hourly_sales (time-series)
   └─ Write to /delta/silver/*

6️⃣ Verify Final Output (5 seconds)
   └─ Validate Silver tables created

──────────────────────────────────────────
Total Duration: 1.5 - 2.5 minutes
```

---

## 💾 Data Layers

### 🥉 Bronze Layer: The Data Vault

**Purpose**: Store raw, unmodified data exactly as received

| Aspect | Details |
|--------|---------|
| **Data** | Raw Kafka messages (JSON) |
| **Write Mode** | APPEND (immutable) |
| **Location** | `/delta/bronze/ventes_raw/` |
| **Partitioning** | By date (`jour`) |
| **Use Case** | Audit trail, recovery, debugging |
| **Query Performance** | Slower (30-60 seconds) |

**Example Record:**
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

### 🥈 Silver Layer: The Analytics Warehouse

**Purpose**: Pre-compute business metrics for instant analytics

| Aspect | Details |
|--------|---------|
| **Data** | Cleaned & aggregated metrics |
| **Write Mode** | OVERWRITE (current state) |
| **Location** | `/delta/silver/*` |
| **Tables** | ventes_clean, ventes_aggreges, top_produits, hourly_sales |
| **Use Case** | Dashboard queries, reporting |
| **Query Performance** | Fast (< 100ms) - **300x faster!** |

**Tables:**

1. **ventes_clean**: Cleaned transactions with time dimensions
2. **ventes_aggreges**: Revenue by product × country
   ```
   produit_nom         | pays   | total_montant | total_quantite
   ──────────────────  ┼────────┼───────────────┼────────────────
   Ordinateur portable | France | €8,999.90     | 10
   Souris sans fil     | France | €765.00       | 30
   ```

3. **top_produits**: Top 10 products by revenue
   ```
   rank | produit_nom         | total_montant
   ─────┼─────────────────────┼───────────────
   1    | Ordinateur portable | €14,499.40
   2    | Clavier mecanique   | €3,750.00
   ```

4. **hourly_sales**: Time-series hourly aggregates
   ```
   heure           | total_montant | total_quantite
   ────────────────┼───────────────┼────────────────
   2025-12-22 10:00| €1,500.00     | 20
   2025-12-22 11:00| €2,250.00     | 30
   ```

---

## 🌐 API Endpoints

### Flask Dashboard APIs

Base URL: `http://localhost:5000`

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | HTML Dashboard | Web UI |
| `/api/aggregated_sales` | GET | Revenue by product & country | JSON array |
| `/api/top_products` | GET | Top 10 products by revenue | JSON array |
| `/api/hourly_sales` | GET | Hourly sales time-series | JSON array |

**Example Response:**

```bash
# Get aggregated sales
curl http://localhost:5000/api/aggregated_sales

[
  {
    "produit_nom": "Ordinateur portable",
    "pays": "France",
    "total_montant": 8999.90,
    "total_quantite": 10
  },
  ...
]
```

---

## 📊 Monitoring

### Airflow Dashboard
- **URL**: http://localhost:8080
- **Credentials**: `airflow` / `airflow`
- **Features**:
  - DAG execution history
  - Task logs & debugging
  - XCom data inspection
  - SLA monitoring

### Spark UI
- **URL**: http://localhost:8081
- **Features**:
  - Job execution timeline
  - Stage details
  - Executor information
  - Storage metrics

### Grafana Dashboards
- **URL**: http://localhost:3000
- **Features**:
  - Real-time metrics
  - Pipeline performance
  - Infrastructure health

### Prometheus Metrics
- **URL**: http://localhost:9090
- **Targets**:
  - Kafka JMX metrics
  - Spark metrics
  - Custom application metrics

---

## 📚 Documentation

For detailed technical documentation, see:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture & components
- **[PIPELINE_FOCUS.md](PIPELINE_FOCUS.md)** - Deep-dive into pipeline flow
- **[AGGREGATION_STRATEGY.md](AGGREGATION_STRATEGY.md)** - Data aggregation rationale

---

## 🎯 Key Concepts

### Medallion Architecture
A three-layer data architecture pattern:
- **Bronze**: Raw, unprocessed data (truth of record)
- **Silver**: Cleaned, validated, deduplicated data
- **Gold**: Business-ready aggregated data *(optional future enhancement)*

### Why Pre-Aggregate?

**Without Aggregations** (querying Bronze directly):
```
SELECT produit_nom, SUM(montant) FROM bronze GROUP BY produit_nom
→ Scans 1,000,000 raw records
→ Takes 30-60 seconds ❌
```

**With Aggregations** (using Silver):
```
SELECT produit_nom, total_montant FROM silver.ventes_aggreges
→ Scans 500 pre-computed rows
→ Takes < 100ms ✅
```

**Result**: **300-600x speedup** for dashboard queries! 🚀

### Delta Lake Benefits
- ✅ **ACID Transactions**: Data consistency guarantees
- ✅ **Time Travel**: Query historical versions (`VERSION AS OF`)
- ✅ **Schema Enforcement**: Prevent schema mismatches
- ✅ **Unified Batch/Streaming**: Single API for both modes

---

## 🛑 Stopping the Pipeline

```bash
# Stop all services (keep data volumes)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

---

## 🐛 Troubleshooting

### No Data in Bronze Layer?
```bash
# 1. Check Kafka brokers
docker-compose exec broker1 kafka-broker-api-versions.sh

# 2. Check Spark logs
docker-compose logs spark-master

# 3. Re-trigger pipeline
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline
```

### Flask Dashboard Errors?
```bash
# 1. Check Flask logs
docker-compose logs flask-dashboard

# 2. Verify Delta tables exist
ls -la ./delta/silver/

# 3. Restart Flask service
docker-compose restart flask-dashboard
```

### Memory Issues?
- Increase Docker Desktop memory allocation (Settings → Resources)
- Reduce Spark memory in `docker-compose.yml`
- Reduce number of Kafka partitions

---

## 🚀 Future Enhancements

- [ ] **Gold Layer**: Business-ready aggregations
- [ ] **dbt Integration**: Transformation testing
- [ ] **Real-time Alerts**: Anomaly detection
- [ ] **Schema Registry**: Confluent Schema Registry
- [ ] **Data Catalog**: OpenMetadata for lineage tracking
- [ ] **ML Models**: Predictive analytics
- [ ] **API Authentication**: JWT/OAuth security
- [ ] **Data Retention**: Archival policies

---

## 📖 Learning Resources

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Medallion Architecture Guide](https://www.databricks.com/glossary/medallion-architecture)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is open-source and available for educational purposes.

---

## 👤 Author

**MouradSalah-Dev**

- GitHub: [@MouradSalah-Dev](https://github.com/MouradSalah-Dev)
- Repository: [fake_sales_pipeline](https://github.com/MouradSalah-Dev/fake_sales_pipeline)

---

## 🙏 Acknowledgments

- Built with modern data engineering best practices
- Demonstrates production-ready pipeline architecture
- Inspired by real-world e-commerce data platforms

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ for the Data Engineering community

</div>
