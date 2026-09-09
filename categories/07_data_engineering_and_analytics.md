# 📊 CATEGORY 07: Data Engineering, Analytics & Lakehouses

## 1. Scope & Architectural Mandate
Governs petabyte-scale data pipelines, streaming ingestion, federated lakehouse catalogs, analytical data models, and automated data quality validation.

- **Domains**: Google Cloud BigQuery, DuckDB (embedded OLAP), ClickHouse, Apache Arrow/Parquet columnar storage, DBT transformations, ETL/ELT DAGs, schema evolution governance.
- **Key Constraints**: Exactly-once processing semantics, idempotent ingestion, deterministic schema validation, automated data quality anomaly checks, sub-second query latency for analytical slices.

---

## 2. Polyglot Technology Stack
- **Languages**: Python (pipelines, PySpark, Polars), SQL (DBT, BigQuery, ClickHouse), Rust (fast data parsers & native Arrow extensions).
- **Storage & Formats**: Apache Parquet, Apache Iceberg, Delta Lake, Arrow IPC.
- **Orchestration**: Dagster, Apache Airflow, Temporal.

---

## 3. Core Invariants & Fail-Closed Boundaries
1. **Schema Evolution Invariant**:
   - Ingested records must conform to the current schema or an authorized backward-compatible evolution.
   - Malformed, type-mismatched, or unparseable rows must be quarantined to a Dead Letter Queue (DLQ) with error metadata—never dropped silently and never halting the healthy pipeline batch.
2. **Data Freshness & Null Invariants**:
   - Primary key uniqueness and non-null constraints must be validated at ingestion boundaries.
3. **Refusal Reason Codes**:
   - `ERR_DATA_SCHEMA_MISMATCH`: Incoming records violated expected schema types or required columns.
   - `ERR_DATA_NULL_CONSTRAINT_VIOLATION`: Primary key or non-nullable column contained null values.
   - `ERR_DATA_DLQ_OVERFLOW`: Quarantined record count exceeded acceptable anomaly threshold.
   - `ERR_DATA_PIPELINE_STALENESS`: Ingestion lag exceeded SLA threshold.

---

## 4. Stage-by-Stage Implementation Guide

### Stage 0: Contracting
- Define data sources, ingestion frequency (batch vs streaming), throughput expectations (rows/sec), and data retention policies.
- Define data contract with upstream producers: exact schema and acceptable null rates.

### Stage 1: Architectural Modeling
- Design Medallion Architecture: Bronze (raw, immutable) $\to$ Silver (cleaned, deduplicated) $\to$ Gold (aggregated, business metrics).
- Define partitioning and clustering strategies (e.g., partition by day, cluster by customer ID).

### Stage 2: Pro-Code Implementation
- Use columnar operations (Arrow / Polars) rather than iterative row processing.
- Implement automated DLQ quarantine routing.

### Stage 3: Adversarial Verification
- Inject malformed records (strings in integer fields, corrupted timestamps, massive payload sizes).
- Verify healthy records process successfully while malformed records route cleanly to DLQ.

---

## 5. Reference Pattern: Fail-Closed Columnar Ingestion Validator
```python
from typing import Dict, Any, List, Tuple
import datetime

class IngestionValidator:
    def __init__(self, schema: Dict[str, type]):
        self.schema = schema
        self.dlq: List[Dict[str, Any]] = []

    def validate_and_route(self, batch: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        clean_records = []
        rejected_records = []

        for row in batch:
            errors = []
            for col, expected_type in self.schema.items():
                if col not in row or row[col] is None:
                    errors.append(f"Missing required field: {col}")
                elif not isinstance(row[col], expected_type):
                    errors.append(f"Type mismatch for {col}: expected {expected_type.__name__}, got {type(row[col]).__name__}")

            if errors:
                rejected = {
                    "raw_row": row,
                    "errors": errors,
                    "quarantined_at": datetime.datetime.utcnow().isoformat(),
                    "code": "ERR_DATA_SCHEMA_MISMATCH"
                }
                self.dlq.append(rejected)
                rejected_records.append(rejected)
            else:
                clean_records.append(row)

        return clean_records, rejected_records
```
