# Fake Sales Pipeline - Architecture & Project Overview

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Data Pipeline Flow](#data-pipeline-flow)
5. [Services & Components](#services--components)
6. [Data Structure](#data-structure)
7. [Running the Project](#running-the-project)
8. [Monitoring & Observability](#monitoring--observability)

---

## Project Overview

**Fake Sales Pipeline** is a modern, production-ready data engineering project that demonstrates a complete real-time data pipeline architecture. It simulates an e-commerce sales system, streaming transaction data through multiple processing layers, and exposing insights via a web dashboard.

### Key Features
- ✅ Real-time data ingestion from Apache Kafka
- ✅ Medallion architecture (Bronze → Silver layers) for data transformation
- ✅ Apache Airflow for workflow orchestration
- ✅ Apache Spark for distributed data processing
- ✅ Delta Lake for versioned, ACID-compliant data storage
- ✅ Flask web dashboard for data visualization
- ✅ Prometheus & Grafana for infrastructure monitoring
- ✅ PostgreSQL for Airflow metadata
- ✅ Redis for caching and task queue
- ✅ Docker Compose for containerized deployment

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FAKE SALES PIPELINE SYSTEM                   │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────┐
│   DATA SOURCES     │
├────────────────────┤
│  • Fake Sales Data │
│  • Random Clients  │
│  • Product Catalog │
└─────────┬──────────┘
          │
          ▼
┌────────────────────────────────────────────────────────────────┐
│              REAL-TIME DATA INGESTION LAYER                    │
├────────────────────────────────────────────────────────────────┤
│  Kafka (3-broker cluster)                                      │
│  Topic: ventes_stream (Sales Transaction Stream)              │
│  Partitions: Multiple for parallel consumption                 │
└─────────────┬──────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────────┐
│        ORCHESTRATION & WORKFLOW LAYER                          │
├────────────────────────────────────────────────────────────────┤
│  Apache Airflow (CeleryExecutor)                               │
│  • Unified Sales Pipeline DAG (unified_sales_pipeline_dag.py) │
│  • Scheduling & Monitoring                                    │
│  • Backend: PostgreSQL + Redis                                │
└─────────────┬──────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────────┐
│      DISTRIBUTED PROCESSING & TRANSFORMATION LAYER             │
├────────────────────────────────────────────────────────────────┤
│  Apache Spark Cluster (Master + Workers)                       │
│  • spark_streaming_delta.py → Bronze ingestion                 │
│  • bronze_to_silver.py → Data cleaning & aggregation          │
│  • Delta Lake integration                                      │
└─────────────┬──────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────────┐
│           DATA STORAGE & VERSIONING LAYER                      │
├────────────────────────────────────────────────────────────────┤
│  Delta Lake (ACID Transactions, Time Travel)                   │
│  ├─ Bronze Layer: /delta/bronze/                              │
│  │  └─ Raw Kafka data (minimal transformation)               │
│  │                                                             │
│  └─ Silver Layer: /delta/silver/                              │
│     ├─ ventes_clean (cleaned data)                            │
│     ├─ ventes_aggreges (aggregated metrics)                   │
│     ├─ top_produits (product rankings)                        │
│     └─ hourly_sales (time-series analytics)                   │
└─────────────┬──────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────────┐
│          PRESENTATION & API LAYER                              │
├────────────────────────────────────────────────────────────────┤
│  Flask Web Dashboard (port 5000)                               │
│  • RESTful APIs for data queries                               │
│  • HTML templates for visualization                           │
│  • Spark integration for direct queries                        │
└─────────────┬──────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────────┐
│          MONITORING & OBSERVABILITY LAYER                      │
├────────────────────────────────────────────────────────────────┤
│  • Prometheus: Metrics collection                              │
│  • Grafana: Dashboard visualization                            │
│  • Airflow UI: DAG execution monitoring                        │
│  • Spark UI: Job execution details                             │
└────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Data Technologies
| Component | Version | Purpose |
|-----------|---------|---------|
| Apache Kafka | 3.x | Real-time event streaming |
| Apache Spark | 3.5.0 | Distributed data processing |
| Delta Lake | 3.2.0 | ACID transactions & versioning |
| Apache Airflow | 2.10.5 | Workflow orchestration |

### Data Storage & Infrastructure
| Component | Version | Purpose |
|-----------|---------|---------|
| PostgreSQL | 13 | Airflow metadata database |
| Redis | 7.2 | Cache & message broker |
| Delta Checkpoints | - | Streaming state management |

### Presentation & Monitoring
| Component | Version | Purpose |
|-----------|---------|---------|
| Flask | Latest | Web dashboard & REST APIs |
| Grafana | Latest | Metrics visualization |
| Prometheus | Latest | Metrics collection |
| Nginx | Latest | Reverse proxy & load balancing |

### Containerization
| Component | Version | Purpose |
|-----------|---------|---------|
| Docker | Latest | Container runtime |
| Docker Compose | 3.x | Multi-container orchestration |

---

## Data Pipeline Flow

### 1️⃣ Data Generation & Ingestion

**File**: [dags/unified_sales_pipeline_dag.py](dags/unified_sales_pipeline_dag.py)

```
Step 1: Check Infrastructure
├─ Verify Kafka brokers are reachable
├─ Verify Spark master is running
└─ Validate Airflow connectivity

Step 2: Produce Sales Data
├─ Generate 50 fake sales transactions
├─ Enrich with client & product information
└─ Stream to Kafka topic: ventes_stream
   └─ Each record contains:
      - vente_id, client_id, produit_id
      - timestamp, quantite, montant
      - client_nom, produit_nom, categorie
      - pays, segment

Step 3: Check Data Readiness
└─ Verify Bronze data exists in Delta Lake
```

### 2️⃣ Bronze Layer Processing

**File**: [dags/spark_streaming_delta.py](dags/spark_streaming_delta.py)

```
Kafka Stream → Spark Structured Streaming
├─ Consumer Group: airflow-bronze-processor
├─ Topics: ventes_stream
├─ Processing:
│  ├─ Parse JSON messages
│  ├─ Add ingestion timestamp
│  └─ Detect schema changes
└─ Output: /delta/bronze/ventes_raw
   ├─ Partition by: date
   ├─ Format: Delta
   └─ Mode: Append (immutable raw data)
```

**Key Characteristics**:
- ✅ Minimal transformations (raw data preservation)
- ✅ Schema inference from streaming data
- ✅ Checkpoint management for fault tolerance
- ✅ Idempotent writes with deduplication

### 3️⃣ Silver Layer Transformation

**File**: [dags/bronze_to_silver.py](dags/bronze_to_silver.py)

```
Bronze → Silver Processing
├─ Data Cleaning:
│  ├─ Remove duplicates
│  ├─ Handle null values
│  ├─ Type conversions
│  └─ Timestamp standardization
│
├─ Aggregations:
│  ├─ ventes_aggreges: Sum by product & country
│  ├─ top_produits: Top 10 products by revenue
│  └─ hourly_sales: Time-series hourly aggregates
│
└─ Output: /delta/silver/
   ├─ ventes_clean (cleaned transactions)
   ├─ ventes_aggreges (business metrics)
   ├─ top_produits (product analytics)
   └─ hourly_sales (temporal analytics)
```

**Transformations**:
```python
# Example transformations:
- Montant >= 0 validation
- Client ID foreign key validation
- Product categorization
- Revenue segmentation
- Geographic aggregation
```

### 4️⃣ Analytics & Reporting

**File**: [app/web/app.py](app/web/app.py)

```
Flask Application
├─ API Endpoints:
│  ├─ GET /api/aggregated_sales → Aggregated metrics
│  ├─ GET /api/top_products → Top product ranking
│  ├─ GET /api/hourly_sales → Time-series data
│  └─ GET / → HTML Dashboard
│
├─ Data Source: Delta Lake (Silver tables)
├─ Compute Engine: Spark SQL
└─ Visualization: HTML + Charts
```

---

## Services & Components

### 🚀 Running Services

#### 1. **PostgreSQL** (Database)
- **Container**: postgres
- **Port**: 5432 (internal)
- **Purpose**: Airflow metadata storage
- **Credentials**: airflow/airflow
- **Database**: airflow
- **Healthcheck**: pg_isready

#### 2. **Redis** (Cache & Message Queue)
- **Container**: redis
- **Port**: 6379 (internal)
- **Purpose**: Celery executor backend
- **Healthcheck**: redis-cli ping

#### 3. **Kafka Cluster** (Message Broker)
- **Containers**: broker1, broker2, broker3
- **Ports**: 19092, 19093, 19094 (advertised)
- **Purpose**: Real-time event streaming
- **Topics**: ventes_stream (auto-created)
- **Replication Factor**: 3

#### 4. **Spark Cluster** (Processing Engine)
- **Master**: spark-master (7077, 8080)
- **Workers**: spark-worker-1, spark-worker-2, spark-worker-3
- **Configuration**: Custom metrics, Delta Lake support
- **Memory**: 1GB driver, 1GB per executor

#### 5. **Airflow** (Orchestration)
- **Scheduler**: airflow-scheduler
- **Webserver**: airflow-webserver (8080)
- **Worker**: airflow-worker (Celery)
- **Purpose**: DAG orchestration and scheduling
- **Executor**: CeleryExecutor

#### 6. **Flask Dashboard** (Web UI)
- **Container**: flask-dashboard
- **Port**: 5000 (external)
- **Purpose**: Sales analytics dashboard
- **APIs**: RESTful endpoints for data queries

#### 7. **Grafana** (Monitoring)
- **Port**: 3000 (external)
- **Purpose**: Metrics visualization
- **Data Source**: Prometheus

#### 8. **Prometheus** (Metrics Collection)
- **Port**: 9090 (external)
- **Purpose**: Time-series metrics
- **Configuration**: [prometheus/prometheus.yml](prometheus/prometheus.yml)

#### 9. **Nginx** (Reverse Proxy)
- **Port**: 80 (external)
- **Purpose**: Load balancing & routing
- **Config**: [nginx/conf.d/default.conf](nginx/conf.d/default.conf)

---

## Data Structure

### Source Data (Kafka)

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

### Sample Clients

| ID | Name | Country | Segment |
|----|------|---------|---------|
| 1 | Jean Dupont | France | Particulier |
| 2 | Maria Garcia | Spain | Particulier |
| 3 | John Smith | UK | Enterprise |
| 4 | Anna Mueller | Germany | Particulier |
| 5 | Paolo Rossi | Italy | Enterprise |

### Sample Products

| ID | Name | Category | Price |
|----|------|----------|-------|
| 101 | Ordinateur portable | Electronics | €899.99 |
| 102 | Souris sans fil | Electronics | €25.50 |
| 103 | Clavier mecanique | Electronics | €75.00 |
| 104 | Casque audio | Electronics | €59.99 |
| 105 | Livre Data Science | Books | €19.99 |

### Delta Lake Tables

#### Bronze Layer
```
/delta/bronze/ventes_raw/
├─ _delta_log/
├─ date=2025-12-22/
│  ├─ part-00000.parquet
│  ├─ part-00001.parquet
│  └─ ...
└─ Schema: Raw JSON fields + processing metadata
```

#### Silver Layer
```
/delta/silver/
├─ ventes_clean/          # Cleaned transactions
├─ ventes_aggreges/       # Revenue by product & country
├─ top_produits/          # Top 10 products
└─ hourly_sales/          # Hourly aggregated metrics
```

---

## Running the Project

### Prerequisites
- Docker & Docker Compose installed
- WSL2 (Windows Subsystem for Linux 2) for Windows users
- 8GB+ RAM, 20GB disk space recommended

### Quick Start

```bash
# 1. Navigate to project directory
cd /path/to/fake_sales_pipeline

# 2. Build and start all services
docker-compose up --build -d

# 3. Wait for services to initialize (2-3 minutes)
docker-compose ps

# 4. Access services:
# - Airflow UI: http://localhost:8080
# - Flask Dashboard: http://localhost:5000
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
# - Kafka JMX: http://localhost:5556
```

### Trigger Pipeline Manually

```bash
# Via Airflow CLI
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline

# Or via Airflow Web UI
# 1. Navigate to http://localhost:8080
# 2. Find "unified_sales_pipeline" DAG
# 3. Click "Trigger DAG"
```

### Monitor Execution

```bash
# Check Airflow logs
docker-compose logs -f airflow-scheduler

# Check Spark job logs
docker-compose logs -f spark-master

# Check Flask application logs
docker-compose logs -f flask-dashboard

# List running containers
docker-compose ps

# View specific container logs
docker-compose logs -f <service-name>
```

### Stop Services

```bash
# Stop all services (keep volumes)
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Monitoring & Observability

### 📊 Airflow Dashboard
- **URL**: http://localhost:8080
- **Username**: airflow
- **Password**: airflow
- **Features**:
  - DAG execution history
  - Task logs and debugging
  - XCom (inter-task communication)
  - SLA monitoring

### 📈 Spark UI
- **URL**: http://spark-master:8080 (internal)
- **Features**:
  - Job execution timeline
  - Stage details
  - Executor information
  - Storage metrics

### 📉 Grafana Dashboards
- **URL**: http://localhost:3000
- **Features**:
  - Real-time metrics
  - Pipeline performance
  - Infrastructure health
  - Custom dashboards

### 🔍 Prometheus Metrics
- **URL**: http://localhost:9090
- **Scraped Targets**:
  - Kafka JMX metrics
  - Spark metrics
  - Custom application metrics

### 📋 Flask APIs

#### Get Aggregated Sales
```
GET /api/aggregated_sales
Response:
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

#### Get Top Products
```
GET /api/top_products
Response:
[
  {
    "produit_nom": "Ordinateur portable",
    "total_montant": 8999.90
  },
  ...
]
```

#### Get Hourly Sales
```
GET /api/hourly_sales
Response:
[
  {
    "heure": "2025-12-22 10:00:00",
    "total_montant": 1500.00,
    "total_quantite": 20
  },
  ...
]
```

---

## Troubleshooting

### Service Won't Start
```bash
# Check logs for specific service
docker-compose logs <service-name>

# Rebuild service
docker-compose build --no-cache <service-name>

# Restart service
docker-compose restart <service-name>
```

### No Data in Bronze Layer
1. Verify Kafka is running: `docker-compose exec broker1 kafka-broker-api-versions.sh`
2. Check Spark job logs: `docker-compose logs spark-master`
3. Trigger pipeline again: `docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline`

### Flask Dashboard Returns Errors
1. Check Flask logs: `docker-compose logs flask-dashboard`
2. Verify Delta tables exist: Check `/tmp/delta/silver/` directory
3. Ensure Spark is accessible: `docker-compose exec flask-dashboard spark-shell --version`

### Memory Issues
1. Reduce Spark memory: Modify `docker-compose.yml` Spark configuration
2. Increase Docker desktop memory allocation
3. Reduce number of Kafka partitions

---

## Project Structure

```
fake_sales_pipeline/
├── dags/                          # Airflow DAGs
│   ├── unified_sales_pipeline_dag.py  # Main pipeline orchestration
│   ├── spark_streaming_delta.py       # Bronze layer processing
│   └── bronze_to_silver.py            # Silver layer transformation
│
├── app/                           # Flask web application
│   └── web/
│       ├── app.py                 # Flask app & APIs
│       └── templates/
│           └── index.html         # Dashboard UI
│
├── delta/                         # Delta Lake data storage
│   ├── bronze/                    # Raw data layer
│   ├── silver/                    # Processed data layer
│   └── checkpoints/               # Spark streaming checkpoints
│
├── kafka/                         # Kafka configuration
│   └── jmx-exporter/
│       └── config.yml
│
├── spark/                         # Spark configuration
│   └── conf/
│       └── metrics.properties
│
├── prometheus/                    # Prometheus monitoring
│   └── prometheus.yml
│
├── grafana/                       # Grafana dashboards
│   ├── dashboards/
│   │   ├── dashboard.yml
│   │   └── sales_streaming_dashboard.json
│   └── provisioning/
│
├── nginx/                         # Nginx reverse proxy
│   └── conf.d/
│       └── default.conf
│
├── logs/                          # Airflow execution logs
│   └── dag_id=unified_sales_pipeline/
│
├── docker-compose.yml             # Multi-container orchestration
├── Dockerfile                     # Base image
├── Dockerfile.airflow             # Airflow image
├── Dockerfile.flask               # Flask app image
└── ARCHITECTURE.md                # This file
```

---

## Key Concepts

### 🏗️ Medallion Architecture
A three-layer data architecture pattern:
- **Bronze**: Raw, unprocessed data (truth of record)
- **Silver**: Cleaned, validated, deduplicated data
- **Gold**: Business-ready aggregated data (optional in this project)

### ⚙️ Orchestration with Airflow
- **DAGs**: Directed Acyclic Graphs define task dependencies
- **Tasks**: Individual units of work (Python operators, Spark jobs)
- **Scheduling**: Automated execution on schedule or triggers
- **Monitoring**: Built-in logging and error handling

### 📊 Spark Structured Streaming
- **Micro-batch processing**: Processes data in small batches
- **Checkpointing**: Maintains state for fault tolerance
- **Watermarking**: Handles late-arriving data
- **Integration**: Native Delta Lake support

### 💾 Delta Lake Benefits
- **ACID Transactions**: Data consistency guarantees
- **Time Travel**: Query historical versions
- **Schema Enforcement**: Prevent schema mismatches
- **Unified Batch/Streaming**: Single API for both modes

---

## Performance Considerations

- **Kafka Partitions**: 3 brokers with multiple partitions for parallelism
- **Spark Configuration**: 1GB driver + executor memory (adjust based on data volume)
- **Delta Optimization**: Partitioning by date, compaction strategies
- **Caching**: Redis for API response caching
- **Monitoring**: Prometheus scrapes every 15 seconds

---

## Future Enhancements

1. **Gold Layer**: Add business aggregations (Gold layer)
2. **Data Quality**: Implement dbt for transformation testing
3. **Real-time Alerts**: Add monitoring on anomalies
4. **Schema Registry**: Confluent Schema Registry for Kafka
5. **Data Catalog**: Implement OpenMetadata for lineage tracking
6. **Advanced Analytics**: Add ML models for predictions
7. **API Authentication**: JWT/OAuth for production security
8. **Data Retention**: Implement data archival policies

---

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Last Updated**: December 22, 2025  
**Project Status**: Active Development  
**Version**: 1.0
