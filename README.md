# 🚀 Fake Sales Pipeline - Real-time Sales Analytics Platform

[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-3.x-black?logo=apache-kafka)](https://kafka.apache.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5.0-orange?logo=apache-spark)](https://spark.apache.org/)
[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.10.5-blue?logo=apache-airflow)](https://airflow.apache.org/)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.2.0-green)](https://delta.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://www.docker.com/)

A production-ready, end-to-end **real-time data engineering platform** that demonstrates modern data stack best practices. This project simulates an e-commerce sales pipeline, processing streaming transactions through a medallion architecture (Bronze → Silver layers), with automated orchestration, monitoring, and interactive dashboards.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Monitoring & Observability](#-monitoring--observability)
- [Troubleshooting](#-troubleshooting)
- [Advanced Topics](#-advanced-topics)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Fake Sales Pipeline** is a comprehensive data engineering project that showcases:

- **Real-time data streaming** with Apache Kafka
- **Distributed data processing** using Apache Spark
- **Workflow orchestration** via Apache Airflow
- **ACID-compliant data lake** powered by Delta Lake
- **Interactive analytics dashboard** built with Flask
- **Production-grade monitoring** using Prometheus & Grafana
- **Containerized deployment** with Docker Compose

This project serves as an excellent learning resource for data engineers and demonstrates enterprise-grade data pipeline patterns.

### What Does It Do?

1. **Generates** fake sales transactions (clients, products, purchases)
2. **Streams** data through Kafka message broker
3. **Processes** data in real-time using Spark Structured Streaming
4. **Stores** data in a medallion architecture (Bronze → Silver layers)
5. **Aggregates** metrics for fast analytics queries
6. **Visualizes** insights through a web dashboard
7. **Monitors** pipeline health with metrics and dashboards

---

## ✨ Key Features

### Data Engineering Capabilities

✅ **Real-time Stream Processing**
- Kafka 3-broker cluster for high-throughput messaging
- Structured Streaming with Spark for micro-batch processing
- Checkpointing for fault tolerance and exactly-once semantics

✅ **Medallion Architecture**
- **Bronze Layer**: Raw, immutable data for audit trail
- **Silver Layer**: Cleaned, validated, and aggregated data
- Supports data quality checks and schema evolution

✅ **Workflow Orchestration**
- Airflow DAGs for end-to-end pipeline automation
- Task dependencies and error handling
- CeleryExecutor for distributed task execution

✅ **Production-Ready Infrastructure**
- Containerized services with Docker Compose
- Health checks and auto-restart policies
- Service discovery and networking

✅ **Analytics & Visualization**
- Flask REST APIs for data access
- Pre-computed aggregations for fast queries
- Real-time dashboard updates

✅ **Monitoring & Observability**
- Prometheus for metrics collection
- Grafana for visualization
- Airflow UI for pipeline monitoring
- Spark UI for job execution details

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FAKE SALES PIPELINE SYSTEM                   │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────┐
│   DATA GENERATION  │
│  • Fake clients    │──┐
│  • Products        │  │
│  • Transactions    │  │
└────────────────────┘  │
                        ▼
        ┌───────────────────────────────┐
        │   KAFKA MESSAGE BROKER        │
        │   Topic: ventes_stream        │
        │   3 Brokers (HA Cluster)      │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   APACHE AIRFLOW              │
        │   Workflow Orchestration      │
        │   • Check infrastructure      │
        │   • Produce data              │
        │   • Trigger Spark jobs        │
        │   • Monitor execution         │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   APACHE SPARK CLUSTER        │
        │   Distributed Processing      │
        │   • Master + 3 Workers        │
        │   • Structured Streaming      │
        │   • Delta Lake integration    │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   DELTA LAKE STORAGE          │
        │   ├─ Bronze: Raw data         │
        │   └─ Silver: Aggregated data  │
        │   • ACID transactions         │
        │   • Time travel               │
        │   • Schema enforcement        │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   FLASK DASHBOARD             │
        │   Analytics & APIs            │
        │   • Real-time metrics         │
        │   • Product rankings          │
        │   • Time-series analysis      │
        └───────────────────────────────┘
```

### Data Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Produce    │───▶│    Kafka     │───▶│    Bronze    │───▶│    Silver    │
│   Sales      │    │   Streaming  │    │   Raw Data   │    │  Aggregated  │
│   Data       │    │              │    │              │    │   Metrics    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                      │
                                                                      ▼
                                                            ┌──────────────┐
                                                            │  Dashboard   │
                                                            │   & APIs     │
                                                            └──────────────┘
```

### Medallion Architecture

| Layer | Purpose | Data Characteristics | Update Mode |
|-------|---------|---------------------|-------------|
| **Bronze** | Raw data storage | Unmodified, immutable, audit trail | Append-only |
| **Silver** | Analytics-ready data | Cleaned, validated, aggregated | Overwrite |

---

## 🛠️ Technology Stack

### Core Data Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Apache Kafka** | 3.x | Real-time event streaming and message brokering |
| **Apache Spark** | 3.5.0 | Distributed data processing and transformations |
| **Delta Lake** | 3.2.0 | ACID transactions, versioning, and time travel |
| **Apache Airflow** | 2.10.5 | Workflow orchestration and scheduling |

### Infrastructure & Storage

| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 13 | Airflow metadata database |
| **Redis** | 7.2 | Celery message broker and caching |
| **Flask** | Latest | Web dashboard and REST APIs |

### Monitoring & Observability

| Technology | Version | Purpose |
|------------|---------|---------|
| **Prometheus** | Latest | Metrics collection and time-series storage |
| **Grafana** | Latest | Metrics visualization and dashboards |
| **Nginx** | Latest | Reverse proxy and load balancing |

### Development & Deployment

| Technology | Version | Purpose |
|------------|---------|---------|
| **Docker** | Latest | Container runtime |
| **Docker Compose** | 3.x | Multi-container orchestration |
| **Python** | 3.10+ | Primary programming language |

---

## 🚀 Quick Start

Get the pipeline running in **5 minutes**:

```bash
# 1. Clone the repository
git clone https://github.com/MouradSalah-Dev/fake_sales_pipeline.git
cd fake_sales_pipeline

# 2. Build and start all services
docker-compose up --build -d

# 3. Wait for services to initialize (2-3 minutes)
docker-compose ps

# 4. Access the services
# Airflow UI: http://localhost:8080 (username: airflow, password: airflow)
# Flask Dashboard: http://localhost:5000
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

### Trigger the Pipeline

**Option 1: Via Airflow UI**
1. Navigate to http://localhost:8080
2. Login with credentials: `airflow` / `airflow`
3. Find the DAG named `unified_sales_pipeline`
4. Click the play button to trigger the DAG

**Option 2: Via CLI**
```bash
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline
```

### View Results

1. **Airflow UI** (http://localhost:8080): Monitor pipeline execution
2. **Flask Dashboard** (http://localhost:5000): View sales analytics
3. **Grafana** (http://localhost:3000): Infrastructure metrics

---

## 📦 Installation

### Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **8GB+ RAM** recommended
- **20GB+ free disk space**
- **WSL2** (for Windows users)

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/MouradSalah-Dev/fake_sales_pipeline.git
cd fake_sales_pipeline

# 2. Create required directories (if not exist)
mkdir -p logs delta/{bronze,silver} plugins

# 3. Set environment variables (optional)
cp .env.example .env  # If you have custom settings

# 4. Build Docker images
docker-compose build

# 5. Initialize Airflow database
docker-compose up airflow-init

# 6. Start all services
docker-compose up -d

# 7. Verify services are running
docker-compose ps
```

### Verify Installation

Check that all services are healthy:

```bash
# Check service status
docker-compose ps

# Expected output: All services should be "running" and "healthy"
```

---

## 💡 Usage

### Running the Pipeline

The pipeline is orchestrated by an Airflow DAG named `unified_sales_pipeline` that:

1. **Checks Infrastructure**: Validates Kafka and Spark connectivity
2. **Produces Sales Data**: Generates 50 fake transactions to Kafka
3. **Bronze Processing**: Ingests data from Kafka to Delta Lake (Bronze layer)
4. **Silver Processing**: Transforms and aggregates data (Silver layer)
5. **Verification**: Validates output data

### Manual Pipeline Trigger

```bash
# Trigger via Airflow CLI
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline

# Check DAG status
docker-compose exec airflow-scheduler airflow dags list-runs -d unified_sales_pipeline

# View task logs
docker-compose logs -f airflow-scheduler
```

### Accessing Services

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Airflow UI** | http://localhost:8080 | airflow/airflow | Pipeline orchestration |
| **Flask Dashboard** | http://localhost:5000 | None | Sales analytics |
| **Grafana** | http://localhost:3000 | admin/admin | Infrastructure monitoring |
| **Prometheus** | http://localhost:9090 | None | Metrics collection |
| **Spark Master UI** | http://localhost:8081 | None | Spark job monitoring |

### View Delta Lake Data

```bash
# Access Spark container
docker-compose exec spark-master bash

# Launch Spark shell
spark-shell

# Query Bronze data
val bronzeDF = spark.read.format("delta").load("/tmp/delta/bronze/ventes_raw")
bronzeDF.show()

# Query Silver aggregations
val silverDF = spark.read.format("delta").load("/tmp/delta/silver/ventes_aggreges")
silverDF.show()
```

---

## 📊 API Documentation

The Flask dashboard exposes RESTful APIs for querying sales data.

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Get Aggregated Sales

```http
GET /api/aggregated_sales
```

**Description**: Returns sales aggregated by product and country

**Response**:
```json
[
  {
    "produit_nom": "Ordinateur portable",
    "categorie": "Electronique",
    "pays": "France",
    "mois": 12,
    "nombre_ventes": 10,
    "chiffre_affaires": 8999.90,
    "panier_moyen": 899.99,
    "clients_uniques": 5
  },
  ...
]
```

#### 2. Get Top Products

```http
GET /api/top_products
```

**Description**: Returns top 10 products ranked by revenue

**Response**:
```json
[
  {
    "produit_nom": "Ordinateur portable",
    "categorie": "Electronique",
    "ventes_count": 16,
    "revenue_total": 14499.40,
    "quantite_moyenne": 2.1
  },
  ...
]
```

#### 3. Get Hourly Sales

```http
GET /api/hourly_sales
```

**Description**: Returns sales aggregated by hour

**Response**:
```json
[
  {
    "heure": "2025-12-22T10:00:00",
    "ventes_count": 20,
    "revenue_total": 1500.00
  },
  ...
]
```

#### 4. Get Overall Statistics

```http
GET /api/overall_statistics
```

**Description**: Returns overall pipeline statistics

**Response**:
```json
{
  "total_revenue": 25000.00,
  "total_sales": 50,
  "unique_products": 5,
  "unique_customers": 5
}
```

---

## 📁 Project Structure

```
fake_sales_pipeline/
├── dags/                              # Airflow DAGs
│   ├── unified_sales_pipeline_dag.py  # Main orchestration DAG
│   ├── spark_streaming_delta.py       # Bronze layer ingestion
│   └── bronze_to_silver.py            # Silver layer transformation
│
├── app/                               # Flask application
│   └── web/
│       ├── app.py                     # Flask APIs
│       └── templates/
│           └── index.html             # Dashboard UI
│
├── delta/                             # Delta Lake storage
│   ├── bronze/                        # Raw data layer
│   │   └── ventes_raw/
│   ├── silver/                        # Processed data layer
│   │   ├── ventes_clean/
│   │   ├── ventes_aggreges/
│   │   ├── top_produits/
│   │   └── hourly_sales/
│   └── checkpoints/                   # Streaming checkpoints
│
├── kafka/                             # Kafka configuration
│   └── jmx-exporter/
│       └── config.yml
│
├── spark/                             # Spark configuration
│   └── conf/
│       └── metrics.properties
│
├── prometheus/                        # Prometheus config
│   └── prometheus.yml
│
├── logs/                              # Airflow logs
│
├── docker-compose.yml                 # Container orchestration
├── Dockerfile                         # Base image
├── Dockerfile.airflow                 # Airflow image
├── Dockerfile.flask                   # Flask image
├── ARCHITECTURE.md                    # Architecture details
├── PIPELINE_FOCUS.md                  # Pipeline guide
├── AGGREGATION_STRATEGY.md            # Aggregation guide
└── README.md                          # This file
```

---

## 📈 Monitoring & Observability

### Airflow Monitoring

**Access**: http://localhost:8080

**Features**:
- DAG execution history and status
- Task logs and error messages
- XCom (cross-communication) between tasks
- SLA and execution time tracking
- Task retry and failure handling

### Spark Monitoring

**Access**: http://localhost:8081

**Features**:
- Job execution timeline
- Stage and task details
- Executor and storage information
- Query execution plans
- Event timeline

### Grafana Dashboards

**Access**: http://localhost:3000 (admin/admin)

**Features**:
- Real-time pipeline metrics
- Infrastructure health monitoring
- Kafka throughput metrics
- Spark job performance
- Custom dashboard creation

### Prometheus Metrics

**Access**: http://localhost:9090

**Metrics Available**:
- Kafka JMX metrics (broker stats, topic metrics)
- Spark metrics (executors, jobs, stages)
- System metrics (CPU, memory, disk)
- Custom application metrics

### Logs

```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f spark-master
docker-compose logs -f flask-dashboard

# View Airflow task logs
docker-compose exec airflow-scheduler cat /opt/airflow/logs/dag_id=unified_sales_pipeline/...
```

---

## 🔧 Troubleshooting

### Common Issues

#### Services Won't Start

```bash
# Check logs for errors
docker-compose logs <service-name>

# Rebuild specific service
docker-compose build --no-cache <service-name>

# Restart service
docker-compose restart <service-name>

# Full restart
docker-compose down
docker-compose up -d
```

#### No Data in Bronze Layer

**Symptoms**: Dashboard shows no data or errors

**Solution**:
```bash
# 1. Verify Kafka is running
docker-compose exec broker1 kafka-topics --list --bootstrap-server localhost:19092

# 2. Check if data is being produced
docker-compose logs airflow-worker | grep "produce_sales_data"

# 3. Verify Spark job executed
docker-compose logs spark-master | grep "bronze"

# 4. Check Delta Lake files
ls -lh delta/bronze/ventes_raw/

# 5. Trigger pipeline again
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline
```

#### Flask Dashboard Shows Errors

**Symptoms**: HTTP 500 errors when accessing APIs

**Solution**:
```bash
# 1. Check Flask logs
docker-compose logs flask-dashboard

# 2. Verify Silver tables exist
ls -lh delta/silver/

# 3. Ensure Spark is accessible
docker-compose exec flask-dashboard spark-submit --version

# 4. Restart Flask
docker-compose restart flask-dashboard
```

#### Airflow Tasks Fail

**Symptoms**: Tasks show red in Airflow UI

**Solution**:
```bash
# 1. Check task logs in Airflow UI
# Navigate to DAG > Task > Logs

# 2. Check infrastructure connectivity
docker-compose exec airflow-scheduler airflow dags trigger check_infrastructure

# 3. Verify environment variables
docker-compose exec airflow-scheduler env | grep KAFKA

# 4. Clear failed task and retry
docker-compose exec airflow-scheduler airflow tasks clear unified_sales_pipeline
```

#### Memory Issues

**Symptoms**: Services crashing or OOM errors

**Solution**:
```bash
# 1. Check Docker resources
docker stats

# 2. Increase Docker Desktop memory allocation
# Settings > Resources > Memory > 8GB+

# 3. Reduce Spark memory in docker-compose.yml
# spark.driver.memory: 512m
# spark.executor.memory: 512m

# 4. Reduce worker count
# Comment out spark-worker-3 in docker-compose.yml
```

#### Port Conflicts

**Symptoms**: Cannot bind to port errors

**Solution**:
```bash
# 1. Check what's using the port
lsof -i :8080  # Airflow
lsof -i :5000  # Flask

# 2. Stop conflicting services or change ports in docker-compose.yml
```

---

## 🎓 Advanced Topics

### Customizing the Pipeline

#### Add New Products or Clients

Edit `/dags/unified_sales_pipeline_dag.py`:

```python
PRODUITS = [
    {"id": 101, "nom": "Your Product", "categorie": "Category", "prix": 99.99},
    # Add more products
]

CLIENTS = [
    {"id": 1, "nom": "Customer Name", "pays": "Country", "segment": "Segment"},
    # Add more clients
]
```

#### Modify Aggregations

Edit `/dags/bronze_to_silver.py` to add custom aggregations:

```python
# Add new aggregation
custom_agg = df_clean.groupBy("your_dimension").agg(
    F.sum("montant").alias("total"),
    F.count("*").alias("count")
)

# Write to Silver
custom_agg.write.format("delta").mode("overwrite").save("/delta/silver/custom_agg")
```

#### Schedule Pipeline

Edit `/dags/unified_sales_pipeline_dag.py`:

```python
default_args = {
    'start_date': datetime(2025, 1, 1),
    'schedule_interval': '@hourly',  # Run every hour
    # Or use cron: '0 */4 * * *'  # Every 4 hours
}
```

### Scaling Considerations

#### Horizontal Scaling

```yaml
# Add more Spark workers in docker-compose.yml
spark-worker-4:
  <<: *spark-worker-common
  container_name: spark-worker-4
  environment:
    SPARK_WORKER_CORES: 2
    SPARK_WORKER_MEMORY: 2g
```

#### Kafka Partitions

```bash
# Increase partitions for better parallelism
docker-compose exec broker1 kafka-topics \
  --alter --topic ventes_stream \
  --partitions 6 \
  --bootstrap-server localhost:19092
```

#### Delta Lake Optimization

```python
# Optimize Delta tables periodically
spark.sql("OPTIMIZE delta.`/delta/silver/ventes_aggreges`")

# Vacuum old versions
spark.sql("VACUUM delta.`/delta/bronze/ventes_raw` RETAIN 168 HOURS")
```

### Data Quality Checks

Add data quality tests using Great Expectations or custom validators:

```python
# Example: Add to bronze_to_silver.py
def validate_data_quality(df):
    # Check for nulls
    null_count = df.filter(F.col("montant").isNull()).count()
    if null_count > 0:
        raise ValueError(f"Found {null_count} null values in montant")
    
    # Check for negative amounts
    negative_count = df.filter(F.col("montant") < 0).count()
    if negative_count > 0:
        raise ValueError(f"Found {negative_count} negative values")
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes** with clear commit messages
4. **Test your changes** thoroughly
5. **Submit a pull request** with a detailed description

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/fake_sales_pipeline.git
cd fake_sales_pipeline

# Create feature branch
git checkout -b feature/my-feature

# Make changes and test
docker-compose up --build -d

# Commit and push
git add .
git commit -m "Add: my awesome feature"
git push origin feature/my-feature
```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and small

### Testing

```bash
# Run pipeline end-to-end
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline

# Verify results
curl http://localhost:5000/api/aggregated_sales
curl http://localhost:5000/api/top_products
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Apache Software Foundation** for Kafka, Spark, and Airflow
- **Delta Lake** community for ACID storage layer
- **Docker** for containerization platform
- **Open Source Community** for amazing tools and libraries

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/MouradSalah-Dev/fake_sales_pipeline/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MouradSalah-Dev/fake_sales_pipeline/discussions)

---

## 🎯 Learning Resources

### Documentation
- 📚 [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- 📚 [PIPELINE_FOCUS.md](PIPELINE_FOCUS.md) - Pipeline deep dive
- 📚 [AGGREGATION_STRATEGY.md](AGGREGATION_STRATEGY.md) - Aggregation strategy

### External Resources
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

---

**Built with ❤️ for the Data Engineering Community**

*Last Updated: February 2026*
