# Phase 11: Backend & Ingestion Internal Software Design

## 1. Architectural Pattern: Layered Clean Architecture

To enforce separation of concerns and testability, backend code is organized into four strictly isolated layers:

```
┌────────────────────────────────────────────────────────┐
│                   Presentation Layer                   │
│   FastAPI Routers (REST)  │   WebSocket Handlers (WS)  │
└───────────────────────────┬────────────────────────────┘
                            │ depends on
                            ▼
┌────────────────────────────────────────────────────────┐
│                    Application Layer                   │
│      TelemetryService     │       AnalyticsService     │
│       AlarmService        │      ConnectionManager     │
└───────────────────────────┬────────────────────────────┘
                            │ depends on
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Domain / Core Layer                  │
│    Thermodynamic Physics  │     Pydantic Schemas/DTOs  │
│       Domain Enums        │       Custom Exceptions    │
└───────────────────────────┬────────────────────────────┘
                            │ implemented by
                            ▼
┌────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                  │
│     SQLAlchemy ORM Repos  │    PostgreSQL Database     │
│    Async Paho-MQTT Client │   Config & Environment     │
└────────────────────────────────────────────────────────┘
```

---

## 2. Directory & Package Layout

```
backend/
├── app/
│   ├── api/                     # Presentation Layer (REST & WS)
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── assets.py    # GET /assets, GET /assets/{id}
│   │   │   │   ├── telemetry.py # GET /history, GET /latest
│   │   │   │   ├── alarms.py    # GET /alarms, POST /alarms/{id}/ack
│   │   │   │   └── health.py    # GET /health
│   │   │   └── router.py        # Aggregated v1 API router
│   │   └── websocket/
│   │       ├── manager.py       # WebSocket ConnectionManager
│   │       └── endpoint.py      # /ws/telemetry stream
│   ├── core/                    # Core & Domain Layer
│   │   ├── config.py            # Pydantic Settings (ENV variables)
│   │   ├── constants.py         # Physical constants (Cp, density)
│   │   └── physics/             # Pure thermodynamic formulas
│   │       ├── heat_exchanger.py
│   │       └── cooling_tower.py
│   ├── schemas/                 # Data Transfer Objects (Pydantic models)
│   │   ├── telemetry.py
│   │   ├── kpi.py
│   │   ├── asset.py
│   │   └── alarm.py
│   ├── db/                      # Infrastructure: Persistence
│   │   ├── session.py           # Async SQLAlchemy engine & sessionmaker
│   │   ├── models/              # Declarative SQLAlchemy models
│   │   │   ├── asset.py
│   │   │   ├── telemetry.py
│   │   │   └── alarm.py
│   │   └── repositories/        # Repository Pattern implementations
│   │       ├── base.py
│   │       ├── asset_repo.py
│   │       ├── telemetry_repo.py
│   │       └── alarm_repo.py
│   └── services/                # Application Layer (Use Cases)
│       ├── asset_service.py
│       ├── analytics_service.py
│       └── alarm_service.py
├── main.py                      # FastAPI Application Entrypoint
└── Dockerfile                   # Container definition
```

---

## 3. Core Software Patterns

### 3.1. Repository Pattern Interface
The Presentation Layer never writes raw SQL queries. Instead, it accesses data via repositories:

```python
class TelemetryRepository:
    async def get_latest_by_asset(self, asset_id: str) -> Optional[TelemetryReading]: ...
    async def get_history_range(
        self, asset_id: str, start: datetime, end: datetime, downsample_mins: int = 1
    ) -> List[TelemetryDataPoint]: ...
    async def insert_reading(self, reading: TelemetryCreateSchema) -> None: ...
```

### 3.2. WebSocket Connection Manager
Maintains concurrent browser connections and safely distributes MQTT broadcast packets:

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast_json(self, data: dict) -> None:
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)
```

---

## 4. REST API Endpoint Specifications

| Method | Route | Description | Response Model |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Subsystem liveness and DB probe | `HealthStatusResponse` |
| `GET` | `/api/v1/assets` | List all active assets with latest health | `List[AssetSummaryResponse]` |
| `GET` | `/api/v1/assets/{id}` | Detailed asset metadata and design parameters | `AssetDetailResponse` |
| `GET` | `/api/v1/assets/{id}/latest` | Most recent telemetry reading and calculated KPIs | `LiveReadingResponse` |
| `GET` | `/api/v1/assets/{id}/history` | Historical time-series query (`?start=&end=&resolution=`) | `TimeSeriesResponse` |
| `GET` | `/api/v1/alarms` | List active unacknowledged operational alarms | `List[AlarmResponse]` |
| `POST`| `/api/v1/alarms/{id}/acknowledge` | Mark an alarm as reviewed by operator | `AlarmResponse` |
| `WS`  | `/ws/telemetry` | Real-time bi-directional streaming pipe | `LiveTelemetryFrame` |