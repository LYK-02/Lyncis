"""
HTTP Route Handlers
RESTful endpoints for events, vessels, sources, and replay controls.
All endpoints are async to properly integrate with asyncio event loop.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.schemas.events import Event, SourceHealth, ReplayStatus
from app.db.database import get_events, get_event_by_id, get_vessel_tracks
from app.sources.manager import source_manager
from app.replay.engine import replay_engine

router = APIRouter()

@router.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "lyncis-api"}

@router.get("/readyz")
async def readyz():
    return {"status": "ready"}

@router.get("/events", response_model=List[Event])
async def list_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    type: Optional[str] = None,
    severity: Optional[str] = None,
    mode: Optional[str] = None
):
    return get_events(limit=limit, offset=offset, event_type=type, severity=severity, mode=mode)

@router.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    ev = get_event_by_id(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return ev

@router.get("/vessels")
async def list_vessels():
    return {"data": get_vessel_tracks()}

@router.get("/sources", response_model=List[SourceHealth])
async def list_sources():
    return source_manager.get_all()

# Replay Control Request Models
class ReplayStartRequest(BaseModel):
    speed: Optional[float] = 5.0
    scenario: Optional[str] = None

class ReplaySeekRequest(BaseModel):
    seconds: float

@router.get("/replay/status", response_model=ReplayStatus)
async def replay_status():
    return replay_engine.get_status()

@router.post("/replay/start")
async def replay_start(req: ReplayStartRequest):
    replay_engine.start(speed=req.speed, scenario=req.scenario)
    return {"status": "started", "replay": replay_engine.get_status()}

@router.post("/replay/pause")
async def replay_pause():
    replay_engine.pause()
    return {"status": "paused", "replay": replay_engine.get_status()}

@router.post("/replay/seek")
async def replay_seek(req: ReplaySeekRequest):
    replay_engine.seek(seconds=req.seconds)
    return {"status": "seeked", "replay": replay_engine.get_status()}

@router.post("/replay/reset")
async def replay_reset():
    replay_engine.reset()
    return {"status": "reset", "replay": replay_engine.get_status()}
