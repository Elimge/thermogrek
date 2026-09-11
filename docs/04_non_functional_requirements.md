# Phase 4: Non-Functional Requirements Specification (NFR)

## 1. Quality Attributes (ISO/IEC 25010)

### 1.1. Performance & Latency (PERF-NFR)
- **PERF-NFR-01 (End-to-End Latency):** The total time elapsed from the physical simulator publishing an MQTT packet to its visual rendering on the web dashboard SHALL NOT exceed **1000 ms** (Target: $< 300\text{ ms}$ under local network conditions).
- **PERF-NFR-02 (Ingestion Throughput):** The ingestion pipeline SHALL effortlessly sustain a minimum of **50 telemetry packets per second** without buffer overflow or message dropping.
- **PERF-NFR-03 (API Query Response Time):** REST API endpoints querying up to 24 hours of aggregated historical data SHALL respond within **500 ms** (95th percentile).
- **PERF-NFR-04 (UI Rendering Frame Rate):** The dashboard interface SHALL maintain a minimum rendering rate of **60 FPS** during real-time streaming, ensuring no UI freezing during high telemetry updates.

---

### 1.2. Reliability, Resilience & Fault Tolerance (REL-NFR)
- **REL-NFR-01 (At-Least-Once Delivery):** Telemetry communication between simulator and ingestion service SHALL utilize **MQTT QoS 1** to prevent packet loss during brief transport flickers.
- **REL-NFR-02 (Self-Healing Connection):** In the event of an MQTT broker or database restart, the ingestion and backend services SHALL automatically reconnect using exponential backoff without requiring manual container restarts.
- **REL-NFR-03 (Graceful Degradation):** If the time-series database is temporarily unavailable, the ingestion layer SHALL continue streaming live telemetry to WebSockets while buffering critical alarm transitions.

---

### 1.3. Resource Efficiency & Footprint (RES-NFR)
- **RES-NFR-01 (Memory Footprint Cap):** The entire local containerized stack (Mosquitto + Postgres + Ingestion + Backend + Frontend) SHALL NOT exceed **4.0 GB of RAM** in steady-state operation, preserving host memory for corporate workloads.
- **RES-NFR-02 (CPU Throttling):** Steady-state simulation, ingestion, and KPI computing SHALL consume $< 15\%$ of host CPU (Intel Core i5-13500) under normal 1 Hz operation.

---

### 1.4. Security & Isolation (SEC-NFR)
- **SEC-NFR-01 (Local Network Isolation):** All published container ports (PostgreSQL, MQTT, HTTP API, Frontend) SHALL explicitly bind to the loopback interface (`127.0.0.1`) on the host. Binding to `0.0.0.0` is STRICTLY PROHIBITED to prevent exposing telemetry or internal endpoints to the corporate LAN (`CDB1.LOCAL`).
- **SEC-NFR-02 (Zero Hardcoded Secrets):** No database passwords, broker tokens, or encryption keys SHALL exist in source code or Git history. All sensitive configurations MUST be injected via `.env` files ignored by `.gitignore`.
- **SEC-NFR-03 (Ingress Sanitization):** All payloads received over MQTT or HTTP MUST undergo strict schema validation and range sanity checks to prevent injection attacks and numerical poisoning of analytical models.

---

### 1.5. Portability & Reproducibility (PORT-NFR)
- **PORT-NFR-01 (Zero-Install Host):** The entire application stack SHALL be fully reproducible and executable with a single orchestration command (`docker compose up --build`), requiring only Docker and WSL2 on the host machine.
- **PORT-NFR-02 (Multi-Platform Compatibility):** All Dockerfiles and configuration files SHALL adhere to POSIX standards and run identically on Linux (x86_64/ARM64) and Windows WSL2.

---

### 1.6. Maintainability & Code Quality (MAINT-NFR)
- **MAINT-NFR-01 (Strict Typing):** All Python code SHALL use strict type hints (`typing` module) validated via `mypy` or modern linters (Ruff). All frontend code SHALL use TypeScript in strict mode (`"strict": true`).
- **MAINT-NFR-02 (Modular Separation):** Codebase SHALL enforce separation of concerns: thermodynamic physics, transport layer, database persistence, and API logic MUST be isolated in independent modules.
- **MAINT-NFR-03 (Automated Test Coverage):** Core mathematical and analytical functions (KPI calculations, fouling detection) SHALL maintain a minimum automated unit test coverage of **80%**.

---

### 1.7. Observability (OBS-NFR)
- **OBS-NFR-01 (Structured Logging):** All backend and ingestion services SHALL output structured JSON logs containing: UTC ISO timestamp, log level (`INFO`, `WARNING`, `ERROR`), service name, and execution context.
- **OBS-NFR-02 (Health Probes):** The system SHALL expose standardized health-check endpoints (`/health`) reporting the operational readiness of the broker, database connection pool, and ingestion daemon.
