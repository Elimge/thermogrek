# ADR-001: Selection of MQTT as Industrial Telemetry Transport

## Status
Accepted

## Context
ThermoGrek requires an ingestion protocol to transmit continuous synthetic sensor readings from the plant simulation layer to the ingestion service at frequencies between 1 Hz and 10 Hz.

## Alternatives Considered
1. **HTTP REST Polling / Webhooks:**
   - *Pros:* Universal support, simple debugging.
   - *Cons:* Heavy TCP connection overhead, significant HTTP header bloat per sample (hundreds of bytes of headers for 50 bytes of sensor payload), synchronous coupling.
2. **Apache Kafka:**
   - *Pros:* Massive enterprise throughput (millions of msgs/sec), distributed log replay.
   - *Cons:* Extreme resource consumption (requires JVM / Zookeeper / KRaft, idling at 1.5+ GB RAM), severe operational complexity. Violates requirement `RES-NFR-01` (4.0 GB total stack limit).
3. **Eclipse Mosquitto (MQTT v3.1.1 / v5):**
   - *Pros:* The de facto IIoT standard. Ultra-lightweight footprint (< 30 MB RAM), binary header overhead of only 2 bytes, native publish/subscribe decoupling, QoS 1 delivery guarantees, hierarchical topic semantics (`plants/+/assets/+/telemetry`).

## Decision
We select **MQTT (Eclipse Mosquitto)** as the messaging backbone for all sensor telemetry.

## Consequences & Trade-offs
- **Gains:** Minimal CPU/RAM footprint, realistic OT-to-IT industrial architecture, native topic routing.
- **Sacrifices:** MQTT is not designed for long-term historical query storage; downstream persistence must be handled by a dedicated database.
