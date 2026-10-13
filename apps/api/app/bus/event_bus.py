"""
In-Memory Event Bus & WebSocket Dispatcher
Supports asynchronous publish-subscribe with bounded queues.
"""

import asyncio
from typing import Set, Dict, Any, Callable
from app.schemas.events import Event
from app.db.database import save_event

class EventBus:
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()
        self._handlers = []

    def subscribe(self) -> asyncio.Queue:
        # Bounded queue (max 1000 items) to prevent memory leaks
        q: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._subscribers:
            self._subscribers.remove(q)

    def register_handler(self, handler: Callable[[Event], Any]):
        self._handlers.append(handler)

    async def publish(self, event: Event):
        # 1. Persist to database
        try:
            save_event(event)
        except Exception as e:
            print(f"[-] Failed to persist event {event.id}: {e}")

        # 2. Trigger synchronous/async pipeline handlers
        for handler in self._handlers:
            try:
                res = handler(event)
                if asyncio.iscoroutine(res):
                    await res
            except Exception as e:
                print(f"[-] Handler error on event {event.id}: {e}")

        # 3. Broadcast to all active WebSocket subscriber queues
        dead_queues = set()
        payload = event.model_dump()
        for q in self._subscribers:
            try:
                if q.full():
                    # Drop oldest if congested
                    try:
                        q.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                q.put_nowait(payload)
            except Exception:
                dead_queues.add(q)

        for dead in dead_queues:
            self._subscribers.discard(dead)

# Global singleton
event_bus = EventBus()
