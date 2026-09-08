# Phase 1: Problem Definition & Product Vision

## 1. Project Identity
- **Project Name:** ThermoGrek
- **Subtitle:** Industrial Thermal Monitoring & Predictive Maintenance Platform
- **Domain:** Industrial Internet of Things (IIoT), Thermal Systems & Predictive Maintenance

---

## 2. Industrial Context & Process Topology
The target industrial scenario represents a continuous cooling circuit composed of two thermally coupled assets:
1. **Shell and Tube Heat Exchanger (HE-01):**
   - Recovers heat from a critical industrial process (e.g., lubricating oil, process fluid) using cooling water.
   - Primary failure mode: **Progressive tube/shell fouling** (scaling, particulate sedimentation, biological growth).
2. **Induced/Forced Draft Cooling Tower (CT-01):**
   - Rejects the absorbed heat from the water circuit to the ambient atmosphere via evaporative cooling.
   - Primary failure mode: **Fill degradation and nozzle clogging**, reducing heat dissipation capability.

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

## 3. The Industrial Problem (Pain Point)
In conventional industrial facilities, thermal assets suffer from significant operational blind spots:
1. **Reactive Maintenance Regimes:** Cleaning and overhaul actions are typically triggered only after downstream equipment trips on over-temperature protection (e.g., turbine oil high temperature, chiller high-pressure cutouts).
2. **Manual & Periodic Log Sheets:** Plant rounds rely on manual manometer and thermometer logging once or twice per shift. This produces sparse, error-prone data insufficient for trend analysis.
3. **Invisible Efficiency Losses (OPEX Penalty):** 
   - A fouled heat exchanger causes higher pumping energy consumption due to increased pressure drops ($\Delta P$) and lower heat duty ($Q$).
   - A degraded cooling tower operates with an increased **Approach Temperature**, returning hotter water to the process and reducing the overall plant thermodynamic efficiency.

---

## 4. Product Vision (Solution)
**ThermoGrek** is an end-to-end Industrial IoT platform that bridges real-time telemetry, thermodynamic modeling, and predictive analytics to eliminate operational blind spots in thermal utility systems.

The platform provides:
1. **Continuous Telemetry Acquisition:** Secure, event-driven sensor data ingestion via standard industrial protocols (MQTT).
2. **First-Principles Thermal & Hydraulic Monitoring:** Real-time calculation of engineering KPIs ($\Delta T$, $\Delta P$, Heat Duty $Q$, Cooling Tower Approach, Overall Heat Transfer Coefficient $U$).
3. **Predictive Degradation Analytics:** Automated detection of progressive fouling and fill degradation before thermal safety thresholds are breached.
4. **Actionable Operations Dashboard:** Modern, real-time visualization tailored for plant operators and reliability engineers, replacing manual log sheets with live telemetry and health index trends.

---

## 5. Scope & MVP Boundaries

### In Scope for MVP:
- Synthetic, physics-informed simulation of 1x Shell and Tube Heat Exchanger and 1x Cooling Tower.
- Deterministic progressive degradation injection (clean state $\to$ incipient fouling $\to$ severe fouling).
- Industrial telemetry ingestion using MQTT protocol.
- Persistent time-series and state storage.
- Real-time KPI computing engine.
- Anomaly/fouling detection logic.
- Web dashboard with real-time process views, operational trends, and alert indicators.

### Out of Scope for MVP (Future Roadmap):
- Closed-loop automated valve/pump control (monitoring only, no SCADA control action).
- Multi-plant enterprise multi-tenancy.
- Edge hardware physical flashing (simulated gateway running in container).
