# Phase 16: Security Architecture & Operational Hardening (IEC 62443 / STRIDE)

## 1. STRIDE Threat Model & Mitigations in ThermoGrek

| Threat Category | Industrial Attack Vector | ThermoGrek Architectural Mitigation |
| :--- | :--- | :--- |
| **Spoofing** | Rogue rogue device impersonating `HE-01` telemetry. | **Dev:** Explicit `asset_id` topic mapping.<br/>**Prod Spec:** X.509 client certificate authentication bound to asset TAGs. |
| **Tampering** | Man-in-the-Middle (MitM) altering pressure readings in transit. | **Dev:** Isolated internal Docker bridge network (`thermogrek-net`).<br/>**Prod Spec:** MQTTS over TLS 1.3 (Port 8883) with cipher suite enforcement. |
| **Repudiation** | Operator denies acknowledging a critical fouling alarm. | Audit trail in `alarms` table recording timestamp, operator context, and immutable event ID. |
| **Information Disclosure** | Corporate LAN snooping sensor telemetry. | **Host Port Pinning:** All exposed ports bind strictly to loopback (`127.0.0.1`), completely blocking LAN interfaces (`CDB1.LOCAL`). |
| **Denial of Service** | Corrupted packets or telemetry flood crashing ingestion. | Strict Pydantic schema validation at ingress rejecting impossible values before hitting database; anti-flooding state-transition alarm logic. |
| **Elevation of Privilege** | Container escape accessing host Windows files. | Docker rootless/unprivileged execution isolation within WSL2 Linux VM. |

---

## 2. Access Control Lists (ACL) Policy Specification (Production Readiness)

In production deployment, Mosquitto disables anonymous access and enforces the following ACL matrix:

```text
# Pattern-based Access Control
user sensor_he_01
topic write thermogrek/plants/main/assets/HE-01/telemetry
topic write thermogrek/plants/main/assets/HE-01/status

user sensor_ct_01
topic write thermogrek/plants/main/assets/CT-01/telemetry
topic write thermogrek/plants/main/assets/CT-01/status

user ingestion_worker
topic read thermogrek/plants/main/assets/+/telemetry
topic write thermogrek/plants/main/assets/+/kpis
topic write thermogrek/plants/main/assets/+/alarms

user backend_bridge
topic read thermogrek/plants/main/assets/+/kpis
```

---

## 3. Secret Management & Git Hygiene Verification
- **Principle:** Zero plaintext secrets in version control.
- **Enforcement:** `.env` is ignored by `.gitignore`. A sanitized template `.env.example` provides parameter names without real operational credentials.
- **Database Hardening:** PostgreSQL password authentication enforced; database port (`5433`) bound strictly to `127.0.0.1`.
