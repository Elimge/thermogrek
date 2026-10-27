# Phase 17: Deployment, Containerization & Operational Lifecycle

## 1. Multi-Container Orchestration Architecture
ThermoGrek runs five isolated services managed via Docker Compose on the bridge network `thermogrek-net`:

| Container Name | Base Image | Service Responsibility | Resource Profile |
| :--- | :--- | :--- | :--- |
| `thermogrek-mqtt` | `eclipse-mosquitto:2.0` | Event-driven pub/sub messaging | < 30 MB RAM |
| `thermogrek-db` | `postgres:16-alpine` | Relational & time-series persistence | < 120 MB RAM |
| `thermogrek-simulator` | `python:3.12-slim` | First-principles telemetry generation | < 50 MB RAM |
| `thermogrek-ingestion` | `python:3.12-slim` | Pydantic validation & KPI processing | < 60 MB RAM |
| `thermogrek-backend` | `python:3.12-slim` | FastAPI REST & WebSocket streaming | < 80 MB RAM |
| `thermogrek-frontend` | `node:20-alpine` | Vue 3 + TypeScript dev server | < 90 MB RAM |

Total steady-state footprint: **~430 MB of RAM** (strictly compliant with requirement `RES-NFR-01` < 4.0 GB).

---

## 2. Disaster Recovery & Backup Strategy
- **Persistence Guarantee:** Time-series tables and metadata reside in a named volume (`postgres-data`).
- **Cold/Warm Backups:** Backups are generated using `pg_dump` in custom tar/sql format, timestamped in UTC:
  ```bash
  ./manage.sh backup
  ```
- **Disaster Restore Procedure:**
  ```bash
  cat backups/backup_YYYYMMDD_HHMMSS.sql | docker exec -i thermogrek-db psql -U thermogrek_user -d thermogrek_db
  ```
