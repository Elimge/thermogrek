from typing import List
from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from app.db.session import get_db_connection
from app.db.repositories.alarm_repo import AlarmRepository
from app.schemas.responses import AlarmItem

router = APIRouter()

@router.get("/alarms", response_model=List[AlarmItem], tags=["Alarms"])
async def list_active_alarms(conn: AsyncConnection = Depends(get_db_connection)):
    """Returns active unacknowledged operational alarms."""
    repo = AlarmRepository(conn)
    return await repo.get_active_alarms()

@router.post("/alarms/{alarm_id}/acknowledge", tags=["Alarms"])
async def acknowledge_alarm(alarm_id: str, conn: AsyncConnection = Depends(get_db_connection)):
    """Marks an operational alarm as acknowledged by plant operator."""
    repo = AlarmRepository(conn)
    success = await repo.acknowledge_alarm(alarm_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alarm not found or already acknowledged")
    return {"status": "success", "message": f"Alarm {alarm_id} acknowledged"}
