# Contributing to Fake Sales Pipeline

First off, thank you for considering contributing to Fake Sales Pipeline! 🎉

This document provides guidelines and instructions for contributing to this project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

### Our Standards

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

---

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

**When submitting a bug report, include:**
- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Screenshots (if applicable)
- Environment details (OS, Docker version, etc.)
- Relevant logs

**Example:**
```markdown
**Bug**: Airflow DAG fails at produce_sales_data task

**Steps to Reproduce**:
1. Run `docker-compose up -d`
2. Trigger unified_sales_pipeline DAG
3. Task fails with Kafka connection error

**Environment**:
- OS: Ubuntu 22.04
- Docker: 24.0.5
- Docker Compose: 2.20.2

**Logs**:
[Paste relevant error logs here]
```

### 💡 Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach
- Any alternatives you've considered

### 🔧 Pull Requests

We love pull requests! Here's how to submit one:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

---

## Development Setup

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.10+ (for local development)
- Git

### Local Development Environment

```bash
# 1. Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/fake_sales_pipeline.git
cd fake_sales_pipeline

# 2. Add upstream remote
git remote add upstream https://github.com/MouradSalah-Dev/fake_sales_pipeline.git

# 3. Create a feature branch
git checkout -b feature/my-feature

# 4. Start the development environment
docker-compose up --build -d

# 5. View logs to ensure everything is working
docker-compose logs -f
```

### Making Changes

```bash
# 1. Make your changes to the code

# 2. Test your changes
docker-compose restart <affected-service>

# 3. Check logs
docker-compose logs <affected-service>

# 4. Trigger the pipeline to test end-to-end
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows the project's coding standards
- [ ] All tests pass
- [ ] Documentation is updated (if applicable)
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up to date with main/master

### Submitting Your PR

1. **Title**: Clear and descriptive (e.g., "Add: support for PostgreSQL data source")
2. **Description**: Include:
   - What changes were made
   - Why these changes were necessary
   - How to test the changes
   - Screenshots (for UI changes)
   - Related issue numbers

**Example PR Description:**
```markdown
## Changes
- Added support for PostgreSQL as a data source
- Updated Airflow DAG to handle PostgreSQL connections
- Added new environment variables for PostgreSQL config

## Why
This feature enables users to ingest data from PostgreSQL databases in addition to Kafka.

## Testing
1. Set PostgreSQL connection in .env
2. Run the DAG: `airflow dags trigger postgres_ingestion`
3. Verify data in Bronze layer

## Screenshots
[If applicable]

Closes #123
```

### Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited

---

## Coding Standards

### Python Code Style

Follow **PEP 8** guidelines:

```python
# Good
def process_sales_data(df: DataFrame) -> DataFrame:
    """
    Process sales data by cleaning and validating.
    
    Args:
        df: Input DataFrame with raw sales data
        
    Returns:
        Cleaned DataFrame
    """
    return df.filter(F.col("montant") >= 0)

# Bad
def process(d):
    return d.filter(F.col("montant")>=0)
```

### Key Principles

1. **Meaningful Names**: Use descriptive variable and function names
2. **Small Functions**: Keep functions focused on a single task
3. **Comments**: Add docstrings for functions and classes
4. **Type Hints**: Use type hints for function parameters and returns
5. **Error Handling**: Handle exceptions gracefully with informative messages

### Docker and Infrastructure

```yaml
# Good: Clear service definition with health checks
airflow-scheduler:
  image: custom-airflow:2.10.5
  container_name: airflow-scheduler
  healthcheck:
    test: ["CMD", "airflow", "jobs", "check", "--job-type", "SchedulerJob"]
    interval: 30s
    timeout: 10s
    retries: 5
```

---

## Testing Guidelines

### Manual Testing

Before submitting a PR, ensure:

```bash
# 1. Services start successfully
docker-compose up -d
docker-compose ps  # All should be "healthy"

# 2. Pipeline executes without errors
docker-compose exec airflow-scheduler airflow dags trigger unified_sales_pipeline

# 3. Check all tasks complete successfully
# Monitor in Airflow UI: http://localhost:8080

# 4. Verify data in Delta Lake
docker-compose exec spark-master spark-shell
# scala> spark.read.format("delta").load("/tmp/delta/silver/ventes_aggreges").show()

# 5. Test API endpoints
curl http://localhost:5000/api/aggregated_sales
curl http://localhost:5000/api/top_products
curl http://localhost:5000/api/hourly_sales
```

### Integration Testing

Test the entire pipeline flow:

1. Data production to Kafka
2. Bronze layer ingestion
3. Silver layer transformation
4. Dashboard displays data correctly

### Performance Testing

For performance-related changes:
- Measure execution time before and after
- Monitor resource usage (CPU, memory)
- Document improvements in PR description

---

## Documentation

### When to Update Documentation

Update documentation when:
- Adding new features
- Changing existing behavior
- Adding new configuration options
- Modifying API endpoints
- Changing infrastructure requirements

### Documentation Files

- `README.md`: Main project documentation
- `ARCHITECTURE.md`: System architecture details
- `PIPELINE_FOCUS.md`: Pipeline-specific documentation
- `AGGREGATION_STRATEGY.md`: Aggregation logic documentation
- Code comments: Inline documentation

### Documentation Style

```python
def create_aggregation(df: DataFrame, dimension: str) -> DataFrame:
    """
    Create sales aggregation by specified dimension.
    
    This function groups sales data by the given dimension and computes
    aggregate metrics including total revenue, count, and average.
    
    Args:
        df: Input DataFrame with cleaned sales data
        dimension: Column name to group by (e.g., 'produit_nom', 'pays')
        
    Returns:
        DataFrame with aggregated metrics
        
    Example:
        >>> agg_df = create_aggregation(sales_df, 'produit_nom')
        >>> agg_df.show()
        +-------------+-----------+-------+
        |produit_nom  |total_rev  |count  |
        +-------------+-----------+-------+
        |Laptop       |14499.40   |16     |
        +-------------+-----------+-------+
    """
    return df.groupBy(dimension).agg(
        F.sum("montant").alias("total_revenue"),
        F.count("*").alias("count"),
        F.avg("montant").alias("average")
    )
```

---

## Commit Message Guidelines

### Format

```
Type: Brief description (50 chars or less)

Detailed explanation if necessary. Wrap at 72 characters.
Explain what and why, not how.

- Bullet points are okay
- Use present tense: "Add feature" not "Added feature"
- Reference issues: "Fixes #123" or "Closes #456"
```

### Types

- **Add**: New feature or functionality
- **Fix**: Bug fix
- **Update**: Update existing functionality
- **Refactor**: Code refactoring without changing behavior
- **Docs**: Documentation changes
- **Style**: Code style changes (formatting, etc.)
- **Test**: Adding or updating tests
- **Chore**: Build process, dependencies, etc.

### Examples

```bash
# Good
git commit -m "Add: PostgreSQL data source support

Implements PostgreSQL connection for data ingestion.
Users can now configure PostgreSQL as an additional
data source alongside Kafka.

Fixes #123"

# Bad
git commit -m "fixed stuff"
```

---

## Questions?

If you have questions:

1. Check existing documentation
2. Search existing issues
3. Create a new issue with the "question" label
4. Join discussions in the repository

---

## Recognition

Contributors will be recognized in:
- Pull request comments
- Release notes
- README contributors section (if significant contribution)

---

**Thank you for contributing to Fake Sales Pipeline! 🚀**

Your efforts help make this project better for everyone.
