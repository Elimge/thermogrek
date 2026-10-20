import json
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import paho.mqtt.client as mqtt

from app.core.config import settings
from app.db.session import init_db_pool, close_db_pool
from app.api.v1.router import api_router
from app.websocket.manager import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ThermoGrekBackend")

loop = None

def on_mqtt_message(client, userdata, msg):
    """Bridge incoming MQTT KPI packets directly into connected WebSockets."""
    global loop
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        if loop and not loop.is_closed():
            asyncio.run_coroutine_threadsafe(
                ws_manager.broadcast_json({"type": "KPI_UPDATE", "data": payload}),
                loop
            )
    except Exception as e:
        logger.error("Error bridging MQTT to WebSocket: %s", e)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loop
    loop = asyncio.get_running_loop()
    logger.info("Starting up ThermoGrek Backend API...")
    await init_db_pool()

    # Start lightweight MQTT bridge client
    mqtt_client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="thermogrek-backend-bridge"
    )
    mqtt_client.on_message = on_mqtt_message
    try:
        mqtt_client.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)
        mqtt_client.subscribe("thermogrek/plants/main/assets/+/kpis", qos=1)
        mqtt_client.loop_start()
        logger.info("Backend MQTT bridge subscribed to KPI topics.")
    except Exception as e:
        logger.warning("Could not connect MQTT bridge on startup: %s", e)

    yield

    logger.info("Shutting down ThermoGrek Backend API...")
    try:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    except Exception:
        pass
    await close_db_pool()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Policy for Local Development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep socket alive; clients can send ping
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
