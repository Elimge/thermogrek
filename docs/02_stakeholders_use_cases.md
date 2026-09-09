# Phase 2: Stakeholders, Personas & Use Cases

## 1. Stakeholder & User Personas

### Persona 1: Plant Operator / Control Room Specialist
- **Name Archetype:** Carlos (Operations Shift Technician)
- **Role:** Real-time process monitoring, shift-based surveillance, immediate incident response.
- **Primary Goals:**
  - Ensure heat exchanger and cooling tower run within safe physical envelopes.
  - Quickly detect abnormal thermal deviations or hydraulic pressure spikes.
  - Acknowledge operational alarms during the shift.
- **Key Pain Points:**
  - Cluttered screens with confusing raw engineering formulas.
  - Delayed alarm notifications that appear only after process trip.
- **Platform Interaction Needs:**
  - Live HMI/SCADA dashboard view with instantaneous status updates (WebSocket).
  - Clear visual indicators (Normal, Warning, Critical).
  - Minimal latency in telemetry display (< 1 second).

---

### Persona 2: Reliability & Thermal Maintenance Engineer
- **Name Archetype:** Elena (Predictive Maintenance Engineer)
- **Role:** Asset health management, degradation analysis, planned maintenance scheduling.
- **Primary Goals:**
  - Track degradation progression (fouling factor, heat transfer coefficient decay).
  - Distinguish between hydraulic fouling (tube blockage) and thermal fouling (boundary layer scaling).
  - Schedule cleaning overhauls during planned turnarounds rather than emergency stops.
- **Key Pain Points:**
  - Lack of continuous telemetry; reliance on sparse manual log sheets.
  - Inability to correlate ambient wet-bulb conditions with cooling tower performance.
- **Platform Interaction Needs:**
  - Multi-variable historical trend graphs ($\Delta P$, $U$, $Approach$).
  - Predictive health indicators and anomaly detection flags.
  - Data export capabilities for thermodynamic reporting.

---

## 2. MVP Use Cases (UC)

### UC-01: Monitor Real-Time Thermal & Hydraulic Telemetry
- **Primary Actor:** Plant Operator (Carlos)
- **Preconditions:** Telemetry simulator and ingestion service are active.
- **Main Flow:**
  1. Operator navigates to the Process Overview / Live Dashboard.
  2. System displays current values for:
     - Heat Exchanger: $T_{hot,in}$, $T_{hot,out}$, $T_{cold,in}$, $T_{cold,out}$, $P_{in}$, $P_{out}$, Flow.
     - Cooling Tower: $T_{water,in}$, $T_{water,out}$, $T_{ambient}$, Relative Humidity, Fan Status.
  3. UI updates continuously via WebSocket stream without full page refreshes.
- **Postconditions:** Operator maintains complete situational awareness of plant state.

---

### UC-02: Compute & Display Live Thermodynamic KPIs
- **Primary Actor:** Plant Operator & Reliability Engineer
- **Preconditions:** Process telemetry is ingested and validated.
- **Main Flow:**
  1. Ingestion/Analytics engine processes raw sensor payloads.
  2. Engine calculates derived engineering parameters:
     - $\Delta T_{hot} = T_{hot,in} - T_{hot,out}$
     - $\Delta T_{cold} = T_{cold,out} - T_{cold,in}$
     - $\Delta P = P_{in} - P_{out}$
     - Heat Duty: $Q = \dot{m} \cdot C_p \cdot \Delta T$
     - Cooling Tower Approach: $Approach = T_{water,out} - T_{wet\_bulb}$
  3. System renders KPIs in dedicated visual cards with engineering units.
- **Postconditions:** Operational performance is quantified in thermodynamic terms.

---

### UC-03: Early Detection of Heat Exchanger Fouling
- **Primary Actor:** Reliability Engineer (Elena)
- **Preconditions:** Telemetry history spans baseline to degraded operating cycles.
- **Main Flow:**
  1. Analytics engine tracks normalized $\Delta P$ and overall heat transfer coefficient ($U$).
  2. As hydraulic resistance increases and $U$ drops beyond threshold bounds, engine raises a predictive event: `FOULING_INCIPIENT` or `FOULING_CRITICAL`.
  3. Dashboard flags asset status to Warning/Maintenance Needed and generates an actionable alert.
- **Postconditions:** Maintenance team schedules tube bundle cleaning prior to process trip.

---

### UC-04: Evaluate Cooling Tower Degradation
- **Primary Actor:** Reliability Engineer (Elena)
- **Preconditions:** Weather/psychrometric telemetry and water temperatures available.
- **Main Flow:**
  1. System determines wet-bulb temperature ($T_{wb}$) from ambient dry-bulb and relative humidity.
  2. System continuously evaluates $Approach = T_{water,out} - T_{wb}$.
  3. If $Approach$ increases systematically under constant thermal load, engine flags cooling tower performance drop (nozzle clogging / fill scaling).
- **Postconditions:** Engineer isolates cooling tower efficiency losses from heat exchanger degradation.

---

### UC-05: Historical Trend Analysis for Root Cause Diagnosis
- **Primary Actor:** Reliability Engineer (Elena)
- **Preconditions:** Historical telemetry and KPIs are persisted in the time-series database.
- **Main Flow:**
  1. Engineer selects asset (HE-01 or CT-01) and sets time window (Last 1 hour, 24 hours, 7 days, 30 days).
  2. System queries database and renders interactive time-series charts.
  3. Engineer correlates pressure drop rise with thermal duty decline to confirm fouling mechanism.
- **Postconditions:** Root cause analysis completed with verifiable empirical data.
