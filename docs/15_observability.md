# Phase 15: Observability, Logging & Operational Metrics

## 1. Architectural Strategy: The Three Pillars in ThermoGrek

### 1.1. Structured Logging
All microservices (`simulator`, `ingestion`, `backend`) follow standardized logging conventions:
- **Format:** `%(asctime)s [%(levelname)s] %(name)s: %(message)s` (ISO-8601 UTC).
- **Levels:**
  - `DEBUG`: Verbose packet traces (disabled in production).
  - `INFO`: Normal state lifecycle events (connections, periodic degradation milestones).
  - `WARNING`: Recoverable network reconnects, threshold excursions, incipient fouling.
  - `ERROR`: Message serialization failures, database query exceptions.

### 1.2. Operational & Business Metrics
Rather than introducing heavy third-party daemons (Prometheus/Grafana) that violate the 4.0 GB RAM constraint (`RES-NFR-01`), ThermoGrek exposes native JSON metrics via `GET /api/v1/metrics`:
- **Data Throughput:** Cumulative telemetry readings persisted.
- **Incident Load:** Active unacknowledged operational alarms.
- **Concurrency:** Real-time active WebSocket client sessions.
- **Infrastructure Health:** PostgreSQL connection pool saturation and MQTT bridge status.

### 1.3. Health Probes
- `GET /api/v1/health`: Lightweight probe for container orchestration.
  - Returns `status: healthy` when both API runtime and DB pool respond in $< 10\text{ ms}$.
  - Returns `status: degraded` if the DB connection drops.
