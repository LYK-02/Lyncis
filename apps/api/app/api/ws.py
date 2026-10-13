"""
WebSocket Stream Hub (/ws/events)
Streams real-time events, heartbeat, and vessels updates.
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone

from app.bus.event_bus import event_bus
from app.db.database import get_events, get_vessel_tracks
from app.replay.engine import replay_engine

ws_router = APIRouter()

@ws_router.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # 1. Send initial hello & state snapshot
    recent_events = [e.model_dump() for e in get_events(limit=25)]
    active_vessels = get_vessel_tracks()
    replay_status = replay_engine.get_status().model_dump()
    
    await websocket.send_json({
        "type": "hello",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "replay" if replay_status["is_playing"] else "live",
        "data": {
            "recent_events": recent_events,
            "vessels": active_vessels,
            "replay": replay_status
        }
    })
    
    # 2. Subscribe to event bus
    queue = event_bus.subscribe()
    
    # 3. Concurrent streaming loop + heartbeat
    async def heartbeat_sender():
        try:
            while True:
                await asyncio.sleep(15)
                # Send periodic vessel positions and heartbeat
                vessels = get_vessel_tracks()
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "replay": replay_engine.get_status().model_dump(),
                    "vessels": vessels
                })
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    heartbeat_task = asyncio.create_task(heartbeat_sender())
    
    try:
        while True:
            # Wait for event from bus
            event_data = await queue.get()
            # Send to client
            await websocket.send_json({
                "type": "event",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": event_data,
                "vessels": get_vessel_tracks()
            })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[-] WS Exception: {e}")
    finally:
        heartbeat_task.cancel()
        event_bus.unsubscribe(queue)
