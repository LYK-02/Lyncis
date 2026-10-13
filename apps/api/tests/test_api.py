"""
Unit and Integration Tests for Lyncis Core API (Phase 1 Gate)
"""

import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db
from app.schemas.events import Event, EventType, Severity, Confidence, EvidenceRef, Mode
from app.sources.sanctions_matcher import check_sanctions

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_readyz(client):
    response = client.get("/readyz")
    assert response.status_code == 200

def test_sanctions_matcher_direct():
    # Test target vessel SEAPRIDE (IMO 9187643, MMSI 572467210)
    match = check_sanctions(mmsi="572467210")
    assert match is not None
    assert match["caption"] == "SEAPRIDE"
    assert "ofac" in match["datasets"].lower()
    assert match["imo"] == "9187643"

def test_banned_terms_language_rule():
    # Rule P3 & §2: banned words must raise ValueError
    with pytest.raises(ValueError) as excinfo:
        Event(
            id="test-1",
            type=EventType.OBSERVATION,
            source="ghostwake",
            title="Vessel is guilty of smuggling goods",  # Contains banned words
            summary="Observed vessel",
            evidence=[EvidenceRef(id="1", source="ais", label="AIS", retrieved_at="2026-10-13T00:00:00Z")]
        )
    assert "Language Rule Violation" in str(excinfo.value)

def test_replay_lifecycle(client):
    # 1. Reset
    r_reset = client.post("/replay/reset")
    assert r_reset.status_code == 200
    
    # 2. Status
    r_status = client.get("/replay/status")
    assert r_status.status_code == 200
    status = r_status.json()
    assert status["is_playing"] is False
    assert status["total_events"] > 0
    
    # 3. Start at 20x speed
    r_start = client.post("/replay/start", json={"speed": 20.0})
    assert r_start.status_code == 200
    assert r_start.json()["replay"]["is_playing"] is True
    
    # 4. Pause
    r_pause = client.post("/replay/pause")
    assert r_pause.status_code == 200
    assert r_pause.json()["replay"]["is_playing"] is False

def test_sources_endpoint(client):
    res = client.get("/sources")
    assert res.status_code == 200
    sources = res.json()
    source_ids = [s["source_id"] for s in sources]
    assert "opensanctions" in source_ids
    assert "aisstream" in source_ids

def test_websocket_stream_initial_hello(client):
    with client.websocket_connect("/ws/events") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "hello"
        assert "data" in data
        assert "vessels" in data["data"]
        assert "replay" in data["data"]
