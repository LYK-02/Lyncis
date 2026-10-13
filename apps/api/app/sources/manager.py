"""
Source Health Telemetry & Status Tracker
Provides health statuses for all OSINT adapters.
"""

from typing import List, Dict
from datetime import datetime, timezone
from app.schemas.events import SourceHealth, Mode

class SourceManager:
    def __init__(self):
        self._sources: Dict[str, SourceHealth] = {
            "opensanctions": SourceHealth(
                source_id="opensanctions",
                name="OpenSanctions (Maritime)",
                status="ok",
                mode=Mode.REPLAY,
                last_success=datetime.now(timezone.utc).isoformat(),
                error_count=0,
                message_count=23651,
                latency_ms=0.03
            ),
            "aisstream": SourceHealth(
                source_id="aisstream",
                name="AISStream (GhostWake)",
                status="ok",
                mode=Mode.REPLAY,
                last_success=datetime.now(timezone.utc).isoformat(),
                error_count=0,
                message_count=521,
                latency_ms=12.0
            ),
            "firms": SourceHealth(
                source_id="firms",
                name="NASA FIRMS",
                status="degraded",  # Flagged / key optional
                mode=Mode.SAMPLE,
                last_success=None,
                error_count=0,
                message_count=0,
                latency_ms=None
            ),
            "crtsh": SourceHealth(
                source_id="crtsh",
                name="crt.sh (ShadowTrace)",
                status="degraded",  # Peak load timeouts
                mode=Mode.SAMPLE,
                last_success=None,
                error_count=1,
                message_count=0,
                latency_ms=None
            )
        }

    def get_all(self) -> List[SourceHealth]:
        return list(self._sources.values())

    def update_status(self, source_id: str, status: str, error: bool = False):
        if source_id in self._sources:
            s = self._sources[source_id]
            s.status = status
            if error:
                s.error_count += 1
            else:
                s.last_success = datetime.now(timezone.utc).isoformat()

source_manager = SourceManager()
