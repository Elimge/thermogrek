# ADR-002: Selection of PostgreSQL as Unified Relational & Time-Series Engine

## Status
Accepted

## Context
The system needs to store two distinct categories of data:
1. Relational metadata: Plant hierarchy, Asset tags, operational states, alarm logs.
2. Time-series measurements: Continuous sensor readings and calculated thermodynamic KPIs indexed by UTC timestamp.

## Alternatives Considered
1. **Polyglot Persistence (PostgreSQL + InfluxDB):**
   - *Pros:* InfluxDB provides native time-series compression and automatic retention policies.
   - *Cons:* Introduces a second database engine to maintain, double container memory overhead, requires dual-write consistency logic. Unjustified for an MVP with 2-10 assets.
2. **Document Store (MongoDB):**
   - *Pros:* Flexible schema for arbitrary JSON telemetry.
   - *Cons:* Poor relational integrity for asset hierarchies and alarm lifecycles, higher memory footprint.
3. **PostgreSQL 16 (Single Relational Store):**
   - *Pros:* ACID compliant, industry-standard SQL, exceptional performance for moderate time-series throughput (easily handles 10,000+ writes/sec with B-Tree indexes on `(asset_id, timestamp DESC)`).

## Decision
We select **PostgreSQL 16** as the single unified persistence engine for the MVP.

## Consequences & Trade-offs
- **Gains:** Single database container, zero dual-write operational complexity, minimal RAM footprint (< 150 MB idle), robust relational constraints for asset tags and alarms.
- **Sacrifices:** If data volume scales to hundreds of assets over multiple years, we will need to enable table partitioning by month or install the TimescaleDB extension. This is a clean, backward-compatible migration path.
