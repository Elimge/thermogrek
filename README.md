# ThermoGrek 🌡️⚡

> **Industrial Thermal Monitoring & Predictive Maintenance Platform**  
> *A physics-informed Industrial IoT (IIoT) digital shadow for continuous thermal utility assets.*

[![Docker](https://img.shields.io/badge/Docker-Orchestrated-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.12-yellow?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue.js-3.4-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MQTT](https://img.shields.io/badge/MQTT-Mosquitto_v2-red?logo=eclipse-mosquitto&logoColor=white)](https://mosquitto.org/)
[![Tests](https://img.shields.io/badge/Tests-12%2F12%20Passed-brightgreen?logo=pytest&logoColor=white)](pytest.ini)

---

## 1. Executive Summary

**ThermoGrek** bridges mechanical and thermal process engineering with modern distributed software architecture. It simulates and monitors a coupled industrial cooling utility circuit:
1. **Primary Shell & Tube Heat Exchanger (`HE-01`):** Recovers heat from critical industrial process oil using circulating water.
2. **Induced Draft Evaporative Cooling Tower (`CT-01`):** Rejects the absorbed thermal load to the atmosphere.

The platform provides end-to-end telemetry ingestion via **MQTT (QoS 1)**, real-time thermodynamic KPI derivation, automated detection of progressive **tube bundle fouling** and **fill degradation**, time-series persistence, and an operator dashboard built according to the **ISA-101** Human-Machine Interface standard.

```
       [ Critical Process ]
               │ (Heat load)
               ▼
   ┌───────────────────────┐
   │ Heat Exchanger (HE-01)│◄──── Cooling Water (Cold) ────┐
   └───────────┬───────────┘                               │
               │ Cooling Water (Warm)                      │
               ▼                                           │
   ┌───────────────────────┐                               │
   │  Cooling Tower (CT-01)│───────────────────────────────┘
   └───────────────────────┘
               │
          (Atmosphere)
```

---

## 2. System Architecture

Built as a lightweight, event-driven multi-container ecosystem:

```
[ Edge Simulation Engine ] (Python 3.12)
           │
      MQTT (QoS 1)
           ▼
[ Eclipse Mosquitto Broker ] (Port 18883)
           │
      MQTT Subscription
           ▼
[ IoT Ingestion Worker ] (Pydantic Validation + Thermodynamic Engine)
           │
           ├──▶ [ PostgreSQL 16 ] (Time-Series & Relational Metadata)
           │
           └──▶ MQTT Broadcast (.../kpis)
                     │
                     ▼
           [ FastAPI Backend ] (Port 8001 / REST & WebSockets)
                     │
                 WebSocket
                     ▼
           [ Vue 3 + TypeScript SPA ] (Port 5174 / ISA-101 Dashboard)
```

---

## 3. Physical & Thermodynamic Modeling

Unlike naive telemetry simulators using unconstrained random walks, ThermoGrek enforces first-principles thermodynamic and hydraulic constraints:

### 3.1. Heat Exchanger Fouling Dynamics
- **Thermal Balance:** $\dot{Q} = \dot{m} \cdot C_p \cdot \Delta T$
- **Degraded Overall Heat Transfer:** $\frac{1}{U(t)} = \frac{1}{U_{clean}} + R_f(t)$
- **Hydraulic Fouling (Darcy-Weisbach Formulation):**  
  As foulant scale reduces effective inner tube diameter $D_{eff}$, pressure drop increases quadratically:
  $$\Delta P(t) = \Delta P_{clean} \cdot \left(\frac{D_i}{D_{eff}(t)}\right)^5 \cdot \left(\frac{\dot{V}}{\dot{V}_{nominal}}\right)^2$$

### 3.2. Cooling Tower Psychrometrics
- **Theoretical Cooling Limit:** Ambient Wet-Bulb Temperature ($T_{wb}$) computed continuously via **Stull's empirical psychrometric equation**:
  $$T_{wb} = f(T_{db}, RH\%)$$
- **Approach Temperature:** $\text{Approach} = T_{water,out} - T_{wb}$ (Drifts upward as fill calcifies or nozzles clog).
- **Effectiveness:** $\eta_{CT} = \frac{T_{water,in} - T_{water,out}}{T_{water,in} - T_{wb}} \cdot 100\%$

---

## 4. Key Performance Indicators & Resource Footprint

| Metric | Target Specification | Measured Performance |
| :--- | :--- | :--- |
| **End-to-End Latency** | $< 1000\text{ ms}$ | **$< 150\text{ ms}$** (Ingestion to Browser WebSocket) |
| **RAM Utilization (Entire Stack)** | $< 4.0\text{ GB}$ | **$\sim 191\text{ MB}$** (All 6 containers running) |
| **CPU Utilization** | $< 15\%$ | **$< 3.5\%$** (Intel Core i5-13500) |
| **Data Ingestion Parity** | $100\%$ | **Zero packet loss** ($> 56,000$ readings verified) |
| **Test Suite Execution** | $100\%$ Pass | **12 / 12 tests passed** (0.36 seconds total run time) |

---

## 5. Repository Structure

```
thermogrek/
├── backend/            # FastAPI async application (REST & WebSockets)
├── ingestion/          # MQTT ingestion worker, Pydantic schemas & KPI engine
├── simulator/          # Edge physical simulation models (HE-01 & CT-01)
├── frontend/           # Vue 3 + TypeScript + Pinia SPA (ISA-101 UI)
├── infrastructure/     # Mosquitto configs & PostgreSQL init DDL scripts
├── tests/              # Pytest automated test suites (Unit & Integration)
├── docs/               # Full engineering documentation & Architecture Decision Records (ADR)
│   ├── adr/            # ADR-001 to ADR-004
│   ├── 01_problem_definition.md
│   ├── 06_system_architecture.md
│   ├── 08_data_model.md
│   ├── 09_mqtt_architecture.md
│   └── 10_physical_simulation_model.md
├── manage.sh           # Operational CLI script (start, stop, status, test, backup)
├── docker-compose.yml  # Multi-container orchestration specification
└── pytest.ini          # Pytest configuration
```

---

## 6. Quickstart Guide

### Prerequisites
- Docker Engine & Docker Compose (or Docker Desktop with WSL2).
- Git.

### 1. Clone & Configure
```bash
git clone git@github.com:Elimge/thermogrek.git
cd thermogrek
cp .env.example .env
```

### 2. Launch Stack
```bash
./manage.sh start
```

### 3. Access Portals
- **Industrial Dashboard (UI):** [http://127.0.0.1:5174](http://127.0.0.1:5174)
- **Interactive API Documentation (Swagger):** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- **Live System Metrics:** [http://127.0.0.1:8001/api/v1/metrics](http://127.0.0.1:8001/api/v1/metrics)

### 4. Operational Commands
```bash
./manage.sh status   # Inspect container health, memory & CPU
./manage.sh test     # Run all unit and integration test suites
./manage.sh backup   # Generate timestamped PostgreSQL disaster recovery backup
./manage.sh stop     # Pause stack and release host memory
```

---

## 7. Author & Technical Profile

**Miguel Canedo Vanegas - Elimge (Mecatronics & Industrial Software Engineer)**  
- Combining industrial field maintenance experience with distributed backend software and Industrial IoT architectures.
