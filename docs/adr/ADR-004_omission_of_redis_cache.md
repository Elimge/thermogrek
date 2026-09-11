# ADR-004: Deliberate Omission of In-Memory Cache (Redis) in MVP

## Status
Accepted

## Context
Initial design proposals suggested adding Redis to cache the "latest telemetry reading" of each asset and to act as a pub/sub message broker between backend worker processes.

## Alternatives Considered
1. **Adding Redis Container:**
   - *Pros:* Sub-millisecond key-value lookups (`GET asset:HE-01:latest`).
   - *Cons:* Adds an extra container consuming 100-200 MB of RAM, adds another moving part and point of failure in Docker Compose.
2. **Eliminating Redis by Leveraging Existing Stack:**
   - *Direct DB Query:* A PostgreSQL query on `(asset_id, timestamp DESC) LIMIT 1` executes in $< 2\text{ ms}$ on indexed tables.
   - *Live Streaming via MQTT:* The backend can subscribe directly to the Mosquitto MQTT broker to receive live telemetry events, eliminating the need for Redis Pub/Sub.

## Decision
We **deliberately omit Redis** from the MVP architecture.

## Consequences & Trade-offs
- **Gains:** Reduced RAM footprint, simpler infrastructure, lower complexity. Aligns strictly with the Principle of Minimalism.
- **Sacrifices:** If hundreds of concurrent web clients start querying the latest state simultaneously, we might introduce Redis as a read-through cache in a future phase.
