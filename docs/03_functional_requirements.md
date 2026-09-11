# Phase 3: Functional Requirements Specification

## 1. Traceability Matrix Overview

| Module Prefix | Subsystem Description | Traceable Use Cases |
| :--- | :--- | :--- |
| **SIM-FR** | Physical Simulation & Telemetry Generation | UC-01, UC-03, UC-04 |
| **ING-FR** | MQTT Telemetry Ingestion & Ingress Validation | UC-01 |
| **KPI-FR** | First-Principles Thermal Analytics Engine | UC-02, UC-03, UC-04 |
| **DAT-FR** | Data Persistence & Time-Series Querying | UC-05 |
| **API-FR** | REST API & Real-Time WebSocket Streaming | UC-01, UC-05 |
| **DSH-FR** | Industrial Monitoring Dashboard (UI) | UC-01, UC-02, UC-03, UC-04, UC-05 |

---

## 2. Module Specifications

### 2.1. Physical Simulation Engine (SIM-FR)
- **SIM-FR-01:** The simulator SHALL generate periodic telemetry packets at a default interval of 1 second (1 Hz), configurable via environment variables.
- **SIM-FR-02 (Heat Exchanger):** The simulator SHALL model a Shell and Tube Heat Exchanger outputting:
  - Hot fluid inlet/outlet temperatures ($T_{hot,in}$, $T_{hot,out}$) in °C.
  - Cold fluid inlet/outlet temperatures ($T_{cold,in}$, $T_{cold,out}$) in °C.
  - Inlet and outlet pressures ($P_{in}$, $P_{out}$) in bar.
  - Volumetric/mass flow rates in $m^3/h$ or $kg/s$.
- **SIM-FR-03 (Cooling Tower):** The simulator SHALL model an Induced Draft Cooling Tower outputting:
  - Water inlet/outlet temperatures ($T_{water,in}$, $T_{water,out}$) in °C.
  - Ambient dry-bulb temperature ($T_{db}$) in °C and Relative Humidity ($RH$) in %.
  - Fan operating status (ON/OFF/RPM).
- **SIM-FR-04 (Degradation Injection):** The simulator SHALL support a deterministic fouling progression mode where:
  - Tube wall fouling resistance ($R_f$) increases over operational cycles.
  - Hydraulic pressure drop ($\Delta P$) increases as effective tube diameter decreases.
  - Heat transfer coefficient ($U$) decays progressively.
- **SIM-FR-05 (Transport):** Telemetry packets SHALL be serialized as JSON payloads and published to the MQTT broker with Quality of Service 1 (QoS 1).

---

### 2.2. Ingestion & Ingress Validation (ING-FR)
- **ING-FR-01:** The ingestion service SHALL subscribe to standard hierarchical MQTT topics (e.g., `thermogrek/plants/+/assets/+/telemetry`).
- **ING-FR-02 (Payload Validation):** The ingestion layer SHALL validate incoming JSON messages against strict schemas (Pydantic/Pydantic-v2 models):
  - Check for mandatory fields (asset ID, timestamp in ISO-8601 UTC, physical readings).
  - Reject or flag payloads containing physically impossible readings (e.g., $T < -50^\circ\text{C}$, $T > 300^\circ\text{C}$, $P < 0\text{ bar}$).
- **ING-FR-03 (Broker Resilience):** The ingestion client SHALL implement automatic reconnection logic with exponential backoff if connectivity to the MQTT broker drops.

---

### 2.3. Thermal Analytics & KPI Engine (KPI-FR)
- **KPI-FR-01 (HE Thermodynamic KPIs):** For each valid heat exchanger telemetry packet, the analytics engine SHALL compute:
  - $\Delta T_{hot} = T_{hot,in} - T_{hot,out}$
  - $\Delta T_{cold} = T_{cold,out} - T_{cold,in}$
  - $\Delta P = P_{in} - P_{out}$
  - Heat Duty hot stream: $Q_{hot} = \dot{m}_{hot} \cdot C_{p,hot} \cdot \Delta T_{hot}$
  - Heat Duty cold stream: $Q_{cold} = \dot{m}_{cold} \cdot C_{p,cold} \cdot \Delta T_{cold}$
  - Energy Balance Relative Error: $\epsilon_Q = \frac{|Q_{hot} - Q_{cold}|}{\max(Q_{hot}, Q_{cold})} \cdot 100\%$
- **KPI-FR-02 (CT Thermodynamic KPIs):** For each valid cooling tower packet, the engine SHALL compute:
  - Estimated Wet-Bulb Temperature ($T_{wb}$) using standard psychrometric approximations (Stull's formula).
  - Approach Temperature: $Approach = T_{water,out} - T_{wb}$
  - Cooling Range: $Range = T_{water,in} - T_{water,out}$
  - Cooling Tower Efficiency / Effectiveness: $\eta_{CT} = \frac{Range}{Range + Approach} \cdot 100\%$
- **KPI-FR-03 (Fouling & Health Classification):** The engine SHALL compute an Asset Health Index ($0\%$ to $100\%$) and trigger discrete operational status flags:
  - `NORMAL`: Health $\ge 85\%$
  - `WARNING_FOULING_INCIPIENT`: $65\% \le \text{Health} < 85\%$
  - `CRITICAL_MAINTENANCE_REQUIRED`: $\text{Health} < 65\%$

---

### 2.4. Data Persistence & Time-Series (DAT-FR)
- **DAT-FR-01:** The database SHALL persist raw telemetry records and calculated thermodynamic KPIs with nanosecond/microsecond UTC timestamps.
- **DAT-FR-02:** The system SHALL persist operational events and alarm transitions (`alarm_raised`, `alarm_cleared`).
- **DAT-FR-03 (Downsampling Queries):** The persistence layer SHALL provide downsampled time-series aggregation (average, min, max bucketed by minute, hour, day) to prevent transferring millions of raw data points to the frontend for historical queries.

---

### 2.5. Backend API & Real-Time Broadcast (API-FR)
- **API-FR-01 (REST Endpoints):** The backend SHALL expose RESTful endpoints:
  - `GET /api/v1/assets`: List monitored assets and current operational status.
  - `GET /api/v1/assets/{id}/latest`: Get most recent raw readings and KPIs.
  - `GET /api/v1/assets/{id}/history?start={}&end={}&resolution={}`: Query time-series telemetry.
  - `GET /api/v1/alarms`: Query active and historical alarms.
  - `GET /health`: Subsystem health check (Broker, DB, Ingestion).
- **API-FR-02 (Real-Time WebSocket):** The backend SHALL expose a WebSocket endpoint (`/ws/telemetry`) that broadcasts live telemetry and KPIs to connected web clients with latency $< 200\text{ ms}$ from ingestion.

---

### 2.6. Dashboard & User Interface (DSH-FR)
- **DSH-FR-01 (Process Overview):** The UI SHALL render a simplified industrial process flow diagram displaying HE-01 and CT-01 with live values.
- **DSH-FR-02 (Asset Detail View):** The UI SHALL display live gauges and metric cards for each asset indicating current temperatures, pressures, and derived KPIs.
- **DSH-FR-03 (Visual Health Status):** Assets SHALL display their health status using intuitive industrial color coding (Green: Normal, Amber: Warning, Red: Critical).
- **DSH-FR-04 (Interactive Charts):** The UI SHALL provide interactive line charts allowing users to switch between 1h, 24h, 7d, and 30d views.
- **DSH-FR-05 (Alarm Banner):** The UI SHALL display an alarm panel showing newly triggered fouling/efficiency warnings in real time.
