# Phase 9: Industrial IoT & MQTT Architecture Specification

## 1. Broker Configuration Baseline
- **Broker Engine:** Eclipse Mosquitto (v2.0+)
- **Protocol Version:** MQTT v3.1.1 / v5.0
- **Default Port (Internal Docker):** `1883`
- **Host Port Mapping (Loopback Only):** `127.0.0.1:18883`
- **Anonymous Access:** Allowed for local development; authentication hooks configured for production.
- **Persistence:** In-memory queue with append-only local storage disabled for MVP.

---

## 2. Topic Taxonomy

ThermoGrek enforces a predictable, hierarchical namespace:
```
thermogrek / {scope} / {plant_id} / assets / {asset_id} / {channel}
```

### Monitored Channels:

| Topic Pattern | Direction | Purpose | QoS | Retain |
| :--- | :--- | :--- | :--- | :--- |
| `thermogrek/plants/main/assets/+/telemetry` | Publisher $\to$ Broker $\to$ Ingestion | Raw physical sensor streams | 1 | False |
| `thermogrek/plants/main/assets/+/kpis` | Ingestion $\to$ Broker $\to$ Backend | Calculated thermodynamic metrics | 1 | False |
| `thermogrek/plants/main/assets/+/status` | Device / Broker (LWT) $\to$ All | Connection lifecycle (`ONLINE` / `OFFLINE`) | 1 | **True** |
| `thermogrek/plants/main/assets/+/alarms` | Ingestion $\to$ Broker $\to$ Backend | Operational and predictive alerts | 1 | False |

---

## 3. Telemetry Payload Contracts (JSON Schema)

### 3.1. Shell & Tube Heat Exchanger (`HE-01`) Telemetry
- **Topic:** `thermogrek/plants/main/assets/HE-01/telemetry`
- **Publish Frequency:** 1.0 Hz (1 sample / sec)
- **JSON Payload Specification:**
```json
{
  "asset_id": "HE-01",
  "timestamp": "2026-09-04T18:30:00.000Z",
  "metrics": {
    "t_hot_in_c": 85.2,
    "t_hot_out_c": 55.4,
    "t_cold_in_c": 28.0,
    "t_cold_out_c": 42.1,
    "p_in_bar": 4.5,
    "p_out_bar": 3.8,
    "flow_rate_m3h": 25.0
  },
  "operational_mode": "NORMAL"
}
```

### 3.2. Cooling Tower (`CT-01`) Telemetry
- **Topic:** `thermogrek/plants/main/assets/CT-01/telemetry`
- **Publish Frequency:** 1.0 Hz (1 sample / sec)
- **JSON Payload Specification:**
```json
{
  "asset_id": "CT-01",
  "timestamp": "2026-09-04T18:30:00.000Z",
  "metrics": {
    "t_water_in_c": 42.1,
    "t_water_out_c": 28.0,
    "t_ambient_db_c": 32.5,
    "relative_humidity_pct": 65.0,
    "fan_speed_rpm": 1450.0,
    "water_flow_m3h": 25.0
  },
  "operational_mode": "NORMAL"
}
```

### 3.3. Calculated Thermodynamic KPI Broadcast
- **Topic:** `thermogrek/plants/main/assets/{asset_id}/kpis`
- **JSON Payload Specification:**
```json
{
  "asset_id": "HE-01",
  "timestamp": "2026-09-04T18:30:00.000Z",
  "kpis": {
    "delta_t_c": 29.8,
    "delta_p_bar": 0.70,
    "heat_duty_kw": 345.8,
    "approach_temp_c": null,
    "effectiveness_pct": 78.4,
    "health_index_pct": 98.2
  },
  "status": "NORMAL"
}
```

---

## 4. Resilience & Reliability Mechanisms

1. **Last Will and Testament (LWT):**
   - When the simulator or a physical gateway establishes an MQTT connection, it registers an LWT message on:
     `thermogrek/plants/main/assets/{asset_id}/status`
   - LWT Payload: `{"asset_id": "{asset_id}", "status": "OFFLINE", "reason": "UNEXPECTED_DISCONNECT"}`
   - If the network drops or the process crashes, Mosquitto automatically broadcasts this payload to all subscribers.
2. **Online Announcement:**
   - Immediately upon successful connection, the device publishes to the same topic:
     `{"asset_id": "{asset_id}", "status": "ONLINE", "connected_at": "..."}` with `retain = true`.
3. **Ingestion Reconnection Strategy:**
   - Ingestion worker uses exponential backoff: if Mosquitto is unreachable, retry after 1s, 2s, 4s, 8s up to a maximum of 30s.