# DECP Data Pipeline

A data engineering project for building an end-to-end pipeline around **DECP (Données Essentielles de la Commande Publique)** data.

The project aims to explore a complete data workflow, from raw data ingestion and cleaning to transformation, storage, and visualization.

## Pipeline

```text
DECP data
   ↓
Ingestion
   ↓
Data cleaning & transformation
   ↓
OLAP storage
   ↓
Analysis & visualization
```

The pipeline is designed to progressively incorporate tools and practices commonly used in data engineering, including **Python, PostgreSQL, Apache Airflow, and Apache Spark**.

## Project Status

🚧 **Work in progress**

The project is currently in its early development stage. The initial focus is on building a reliable data ingestion and transformation pipeline before introducing additional components.

## Goals

- Build a reproducible data pipeline
- Handle and clean real-world public datasets
- Separate ingestion, transformation, and storage concerns
- Experiment with workflow orchestration and distributed processing
- Produce data suitable for analytical use
