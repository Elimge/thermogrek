# ADR-003: Selection of FastAPI for Application Backend

## Status
Accepted

## Context
The backend service must expose RESTful endpoints for historical analysis, serve WebSocket streams with sub-second latency to the UI, and validate complex numerical sensor payloads.

## Alternatives Considered
1. **Django + Django REST Framework:**
   - *Pros:* Mature ecosystem, built-in ORM and admin panel.
   - *Cons:* Heavy monolithic architecture, complex async WebSocket integration (requires Django Channels, Redis, and ASGI configuration).
2. **Flask:**
   - *Pros:* Lightweight and familiar.
   - *Cons:* Synchronous by default, lacks native WebSocket handling without third-party extensions, manual schema validation.
3. **FastAPI (Python 3.12+):**
   - *Pros:* Native asynchronous architecture (Starlette / ASGI), first-class WebSocket support, automatic high-performance validation via Pydantic v2 (Rust-backed core), automated OpenAPI documentation (`/docs`).

## Decision
We select **FastAPI** as the backend framework.

## Consequences & Trade-offs
- **Gains:** High async throughput for WebSockets, unified Pydantic validation between ingestion and API, self-documenting Swagger UI.
- **Sacrifices:** Requires asynchronous programming discipline (`async/await`) across database and socket handlers.
