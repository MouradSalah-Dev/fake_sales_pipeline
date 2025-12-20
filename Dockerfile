# Use official Spark image as base
FROM apache/spark:3.5.5-java17-python3

# Switch to root to install additional packages
USER root

# Install Python packages
RUN pip3 install --no-cache-dir \
    delta-spark==3.2.0 \
    kafka-python \
    pandas \
    numpy \
    matplotlib \
    seaborn

ENV MPLBACKEND=Agg

# CRITICAL FIX: The base image has a 'spark' user but we need to ensure UID 1001 works
# Create a spark user with UID 1001 if it doesn't exist, or just set the username mapping
RUN (getent passwd 1001 && echo "User 1001 already exists") || \
    (userdel spark 2>/dev/null || true && \
     useradd -u 1001 -g 0 -m -s /bin/bash spark)

# Create necessary directories with proper permissions
RUN mkdir -p /tmp/delta \
             /app/dags \
             /opt/spark/conf \
             /opt/spark/logs \
             /opt/spark/work \
             /tmp/spark-warehouse \
             /tmp/spark-events && \
    # CHANGE 1: Set FULL permissions (777) for /tmp/delta
    chmod -R 777 /tmp/delta && \
    # CHANGE 2: Also set ownership to spark user
    chown -R 1001:0 /tmp/delta && \
    chown -R 1001:0 /app/dags \
                    /opt/spark/logs \
                    /opt/spark/work \
                    /tmp/spark-warehouse \
                    /tmp/spark-events && \
    chmod -R 775 /opt/spark/logs \
                 /opt/spark/work \
                 /tmp/spark-warehouse \
                 /tmp/spark-events

# Download Delta Lake JARs
RUN curl -L --retry 3 --retry-delay 5 --max-time 60 \
    https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.2.0/delta-spark_2.12-3.2.0.jar \
    -o /opt/spark/jars/delta-spark_2.12-3.2.0.jar && \
    curl -L --retry 3 --retry-delay 5 --max-time 60 \
    https://repo1.maven.org/maven2/io/delta/delta-storage/3.2.0/delta-storage-3.2.0.jar \
    -o /opt/spark/jars/delta-storage-3.2.0.jar

# Download Kafka JARs - INCLUDING THE MISSING spark-token-provider-kafka!
RUN curl -L --retry 3 --retry-delay 5 --max-time 60 \
    https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.0/spark-sql-kafka-0-10_2.12-3.5.0.jar \
    -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.0.jar && \
    curl -L --retry 3 --retry-delay 5 --max-time 60 \
    https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.0/spark-token-provider-kafka-0-10_2.12-3.5.0.jar \
    -o /opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.0.jar && \
    curl -L --retry 3 --retry-delay 5 --max-time 60 \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar \
    -o /opt/spark/jars/kafka-clients-3.4.1.jar && \
    curl -L --retry 3 --retry-delay 5 --max-time 60 \
    https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar \
    -o /opt/spark/jars/commons-pool2-2.11.1.jar

# Configure Spark defaults
RUN echo "# Delta Lake Configuration" > /opt/spark/conf/spark-defaults.conf && \
    echo "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.jars=/opt/spark/jars/delta-spark_2.12-3.2.0.jar,/opt/spark/jars/delta-storage-3.2.0.jar,/opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.0.jar,/opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.0.jar,/opt/spark/jars/kafka-clients-3.4.1.jar,/opt/spark/jars/commons-pool2-2.11.1.jar" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.databricks.delta.retentionDurationCheck.enabled=false" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.sql.warehouse.dir=/tmp/spark-warehouse" >> /opt/spark/conf/spark-defaults.conf && \
    echo "" >> /opt/spark/conf/spark-defaults.conf && \
    echo "# Security Configuration (Disabled for local development)" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.authenticate=false" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.hadoop.security.authentication=simple" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.hadoop.security.authorization=false" >> /opt/spark/conf/spark-defaults.conf && \
    echo "" >> /opt/spark/conf/spark-defaults.conf && \
    echo "# Network Configuration" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.network.timeout=600s" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.executor.heartbeatInterval=60s" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.rpc.askTimeout=600s" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.rpc.lookupTimeout=600s" >> /opt/spark/conf/spark-defaults.conf && \
    echo "" >> /opt/spark/conf/spark-defaults.conf && \
    echo "# Event Log Configuration" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.eventLog.enabled=false" >> /opt/spark/conf/spark-defaults.conf && \
    echo "" >> /opt/spark/conf/spark-defaults.conf && \
    echo "# Master/Worker Configuration" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.deploy.recoveryMode=NONE" >> /opt/spark/conf/spark-defaults.conf

# Create log4j2.properties to reduce verbose logging
RUN echo "rootLogger.level = info" > /opt/spark/conf/log4j2.properties && \
    echo "rootLogger.appenderRef.stdout.ref = console" >> /opt/spark/conf/log4j2.properties && \
    echo "appender.console.type = Console" >> /opt/spark/conf/log4j2.properties && \
    echo "appender.console.name = console" >> /opt/spark/conf/log4j2.properties && \
    echo "appender.console.target = SYSTEM_OUT" >> /opt/spark/conf/log4j2.properties && \
    echo "appender.console.layout.type = PatternLayout" >> /opt/spark/conf/log4j2.properties && \
    echo "appender.console.layout.pattern = %d{yy/MM/dd HH:mm:ss} %p %c{1}: %m%n" >> /opt/spark/conf/log4j2.properties

# Set proper ownership for all Spark configuration files
RUN chown -R 1001:0 /opt/spark/conf

# Verify JAR files were downloaded successfully
RUN ls -lh /opt/spark/jars/*.jar | grep -E "(delta|kafka|commons-pool)" || true

# CRITICAL: Set environment variables for Hadoop to use the correct user
ENV HADOOP_USER_NAME=spark
ENV USER=spark

# Switch back to non-root user
USER 1001

# Set working directory
WORKDIR /

# Switch to root to create entrypoint
USER root

# Create a better entrypoint script
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'set -e' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# ========== PERMISSION FIXES ==========' >> /entrypoint.sh && \
    echo 'echo "=== STARTING PERMISSION FIXES ==="' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# 1. Ensure directories exist with 777' >> /entrypoint.sh && \
    echo 'mkdir -p /tmp/delta /tmp/delta/bronze /tmp/delta/silver /tmp/delta/checkpoints /tmp/spark-warehouse /tmp/spark-events' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# 2. Set 777 on ALL DELTA FILES AND DIRECTORIES (aggressive)' >> /entrypoint.sh && \
    echo 'echo "Setting permissions on /tmp/delta..."' >> /entrypoint.sh && \
    echo 'find /tmp/delta -type d -exec chmod 777 {} \; 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'find /tmp/delta -type f -exec chmod 666 {} \; 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'chmod -R 777 /tmp/delta 2>/dev/null || true' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# 3. Set ownership recursively' >> /entrypoint.sh && \
    echo 'chown -R 1001:0 /tmp/delta 2>/dev/null || true' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# 4. Fix Spark directories' >> /entrypoint.sh && \
    echo 'echo "Setting permissions on Spark directories..."' >> /entrypoint.sh && \
    echo 'find /tmp/spark-warehouse -type d -exec chmod 777 {} \; 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'find /tmp/spark-warehouse -type f -exec chmod 666 {} \; 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'find /tmp/spark-events -type d -exec chmod 777 {} \; 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'find /tmp/spark-events -type f -exec chmod 666 {} \; 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'chown -R 1001:0 /tmp/spark-warehouse /tmp/spark-events 2>/dev/null || true' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# 5. Fix /tmp directory in general' >> /entrypoint.sh && \
    echo 'echo "Fixing /tmp permissions..."' >> /entrypoint.sh && \
    echo 'chmod 777 /tmp 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'chown 1001:0 /tmp 2>/dev/null || true' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# 6. Clean up Spark and Hadoop temp files' >> /entrypoint.sh && \
    echo 'echo "Cleaning up old Spark temp files..."' >> /entrypoint.sh && \
    echo 'rm -rf /tmp/spark-* /tmp/hadoop-* /tmp/blockmgr-* 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'rm -rf /tmp/*.parquet /tmp/*.snappy /tmp/*.crc 2>/dev/null || true' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# 7. Force recreate Delta table if metadata is corrupted' >> /entrypoint.sh && \
    echo 'echo "Checking for corrupted Delta tables..."' >> /entrypoint.sh && \
    echo 'for dir in /tmp/delta/bronze/ventes_stream /tmp/delta/silver/ventes_clean /tmp/delta/silver/ventes_aggreges /tmp/delta/silver/top_produits; do' >> /entrypoint.sh && \
    echo '    if [ -d "$dir/_delta_log" ]; then' >> /entrypoint.sh && \
    echo '        echo "Found Delta table at $dir"' >> /entrypoint.sh && \
    echo '        # Check if _delta_log has valid JSON files' >> /entrypoint.sh && \
    echo '        json_count=$(find "$dir/_delta_log" -name "*.json" 2>/dev/null | wc -l)' >> /entrypoint.sh && \
    echo '        if [ "$json_count" -eq "0" ]; then' >> /entrypoint.sh && \
    echo '            echo "WARNING: No JSON files in _delta_log, table might be corrupted"' >> /entrypoint.sh && \
    echo '            echo "Cleaning up possibly corrupted table: $dir"' >> /entrypoint.sh && \
    echo '            rm -rf "$dir" 2>/dev/null || true' >> /entrypoint.sh && \
    echo '            mkdir -p "$dir"' >> /entrypoint.sh && \
    echo '            chmod 777 "$dir"' >> /entrypoint.sh && \
    echo '            chown 1001:0 "$dir"' >> /entrypoint.sh && \
    echo '        fi' >> /entrypoint.sh && \
    echo '    fi' >> /entrypoint.sh && \
    echo 'done' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo 'echo "=== PERMISSION FIXES COMPLETED ==="' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Switch back to non-root user for execution
USER 1001

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]