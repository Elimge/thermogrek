# Phase 5: Domain Model & Ubiquitous Language

## 1. Ubiquitous Language (Industrial Dictionary)

| Term | Domain Definition |
| :--- | :--- |
| **Plant** | The high-level physical or logical installation encompassing cooling circuits, utilities, and assets. |
| **Asset** | An identifiable, maintainable mechanical or thermodynamic unit of equipment (e.g., Heat Exchanger, Cooling Tower). |
| **Telemetry Reading** | An immutable, timestamped observation of physical variables captured by sensors (pressures, temperatures, flow). |
| **Thermodynamic KPI** | A calculated engineering indicator derived from raw telemetry using first-principles thermodynamic equations ($\Delta T$, $\Delta P$, Heat Duty $Q$, Cooling Tower Approach, Overall Heat Transfer Coefficient $U$). |
| **Asset Health Index** | A normalized score ($0\%$ to $100\%$) representing the operating integrity and cleanliness of an asset relative to its clean design baseline. |
| **Degradation State** | Discrete operating classification of an asset based on thermal/hydraulic decay (`NORMAL`, `WARNING_FOULING_INCIPIENT`, `CRITICAL_MAINTENANCE_REQUIRED`). |
| **Operational Alarm** | A discrete domain event raised when physical thresholds or predictive degradation indicators violate safety or efficiency envelopes. |

---

## 2. Core Domain Constructs

```
  ┌────────────────────────────────────────────────────────┐
  │                         Plant                          │
  │                  (Aggregate Root)                      │
  │  - id: UUID                                            │
  │  - name: String                                        │
  │  - location: String                                    │
  └───────────────────────────┬────────────────────────────┘
                              │ 1..* (contains)
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                         Asset                          │
  │                       (Entity)                         │
  │  - id: String (e.g., "HE-01")                          │
  │  - type: AssetType (SHELL_TUBE_HE | COOLING_TOWER)     │
  │  - name: String                                        │
  │  - health_status: HealthStatus                         │
  └─────────────┬────────────────────────────┬─────────────┘
                │ 1 (emits)                  │ 1 (evaluates to)
                ▼                            ▼
  ┌───────────────────────────┐┌───────────────────────────┐
  │     TelemetryReading      ││     ThermodynamicKPI      │
  │       (Value Object)      ││       (Value Object)      │
  │ - timestamp: UTCDateTime  ││ - timestamp: UTCDateTime  │
  │ - asset_id: String        ││ - asset_id: String        │
  │ - raw_metrics: Dictionary ││ - delta_t: Float          │
  │                           ││ - delta_p: Float          │
  │                           ││ - heat_duty_kw: Float     │
  │                           ││ - approach_temp: Float    │
  │                           ││ - effectiveness_pct: Float│
  └───────────────────────────┘└─────────────┬─────────────┘
                                             │ triggers (if abnormal)
                                             ▼
                               ┌───────────────────────────┐
                               │        AlarmEvent         │
                               │      (Domain Event)       │
                               │ - id: UUID                │
                               │ - asset_id: String        │
                               │ - severity: SeverityLevel │
                               │ - code: String            │
                               │ - message: String         │
                               │ - triggered_at: UTCDateTime│
                               │ - acknowledged: Boolean   │
                               └───────────────────────────┘
```

---

## 3. Subsystem Domain Invariants (Business Rules)
1. **Physical Immutability:** Once a `TelemetryReading` is persisted with an ISO UTC timestamp, it CANNOT be modified or deleted (append-only ledger).
2. **KPI Derivation Coupling:** A `ThermodynamicKPI` instance must reference exactly one parent `TelemetryReading` or a synchronized set of multi-stream readings within a valid temporal sliding window ($\Delta t \le 1.0\text{ s}$).
3. **Health State Hysteresis:** An asset transitioning from `WARNING_FOULING_INCIPIENT` back to `NORMAL` requires sustained clean readings for at least $N$ consecutive samples to prevent threshold oscillation (chattering).
4. **Alarm Lifecycle:** An `AlarmEvent` remains active until explicitly acknowledged by an operator or auto-cleared when physical variables return to normal ranges.
