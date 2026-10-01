# Phase 12: Frontend Architecture & UI/UX Design (ISA-101 Standard)

## 1. Technological Stack & Tooling
- **Framework:** Vue 3 (Composition API with `<script setup lang="ts">`)
- **Language:** TypeScript 5+ (Strict Type Checking)
- **Build Engine:** Vite (Lightning-fast HMR and optimized asset bundling)
- **State Management:** Pinia (Modular stores for telemetry, assets, and alarms)
- **Visualization & Charts:** Chart.js with `vue-chartjs` or Apache ECharts (Canvas-based rendering for zero-latency time-series downsampling)
- **Styling Paradigm:** Tailwind CSS with an industrial dark theme adhering to **ISA-101** guidelines.

---

## 2. ISA-101 Industrial UX Philosophy
1. **Low-Saturation Baseline:** Neutral dark slate/charcoal backgrounds (`#0f172a`, `#1e293b`) prevent eye fatigue in control room environments.
2. **Selective Visual Salience:** Vibrant saturated colors are strictly reserved for abnormal process conditions:
   - **Normal Operating State:** Soft Gray / Muted Teal (`#10b981`)
   - **Incipient Warning / Degradation:** Industrial Amber (`#f59e0b`)
   - **Critical Alarm / Trip Risk:** High-Visibility Red (`#ef4444`)
3. **High Data-Ink Ratio:** Eliminates purely decorative 3D gradients and skeuomorphic dials in favor of clear numerical readouts, sparklines, and standard P&ID line diagrams.

---

## 3. Component Hierarchy Tree

```
App.vue
├── TheHeader.vue               # Global plant status, broker connection indicator, clock (UTC)
├── TheNavbar.vue               # Navigation between Process, Assets, Trends, Alarms
└── router-view
    ├── ProcessOverviewView.vue # HMI / Process Flow Diagram (HE-01 <-> CT-01 closed loop)
    │   ├── HeatExchangerNode.vue
    │   ├── CoolingTowerNode.vue
    │   └── ProcessPipeFlow.vue # SVG-based animated flow paths
    ├── AssetDetailView.vue     # Deep-dive engineering KPIs for selected asset
    │   ├── MetricCard.vue      # Reusable KPI tile (Value, Unit, Trend sparkline, Delta)
    │   ├── ThermodynamicGauges.vue
    │   └── FoulingPredictorCard.vue # Health index % and degradation stage
    ├── HistoricalTrendsView.vue # Time-series forensics
    │   ├── RangeSelector.vue   # 1h, 24h, 7d, 30d filter bar
    │   └── TimeSeriesChart.vue # Multi-axis interactive line graph
    └── AlarmsCenterView.vue    # Operational alarm ledger
        ├── ActiveAlarmsBanner.vue
        └── AlarmsTable.vue     # Acknowledge button, timestamp, severity, context
```

---

## 4. State Management (Pinia Stores)

### 4.1. `useTelemetryStore`
- **State:**
  - `liveReadings`: Dictionary mapping `asset_id` $\to$ most recent telemetry payload.
  - `liveKpis`: Dictionary mapping `asset_id` $\to$ latest calculated thermodynamic KPIs.
  - `wsConnected`: Boolean flag tracking live WebSocket connectivity.
- **Actions:**
  - `handleIncomingFrame(frame: WebSocketPayload)`: Ingests real-time frames and triggers reactive UI updates without deep re-renders.

### 4.2. `useAlarmsStore`
- **State:**
  - `activeAlarms`: List of unacknowledged alarms.
  - `alarmHistory`: Array of historical audit events.
- **Actions:**
  - `acknowledgeAlarm(alarmId: string)`: Sends asynchronous `POST` to backend and updates local status optimistically.

---

## 5. WebSocket Ingestion & Performance Guardrails
1. **Frame Throttling:** Even if the broker transmits telemetry at frequencies $> 10\text{ Hz}$, the frontend batches DOM updates using `requestAnimationFrame`, guaranteeing that the main thread never drops below **60 FPS**.
2. **Auto-Reconnection Lifecycle:**
   - If the WebSocket closes unexpectedly, an automatic reconnect loop initiates with an exponential backoff schedule: $1\text{s} \to 2\text{s} \to 4\text{s} \to \max 10\text{s}$.
   - Displays an unobtrusive visual status pill in `TheHeader.vue` (`LIVE STREAM` in green vs `RECONNECTING...` in pulsing amber).
