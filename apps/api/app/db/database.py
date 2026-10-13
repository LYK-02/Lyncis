"""
SQLite Storage for Events and Vessel Tracks
Provides thread-safe persistence and query interfaces.
"""

import os
import re
import json
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.config import settings
from app.schemas.events import Event, EvidenceRef

def get_connection():
    db_path = re.sub(r"^sqlite(\+[a-zA-Z0-9_]+)?:///*", "", settings.DATABASE_URL)
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            source TEXT NOT NULL,
            rule_id TEXT,
            entity_id TEXT,
            entity_name TEXT,
            entity_type TEXT,
            lat REAL,
            lon REAL,
            sog REAL,
            cog REAL,
            heading REAL,
            severity TEXT NOT NULL,
            confidence TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            brief TEXT,
            is_fallback INTEGER DEFAULT 0,
            reasoning TEXT,
            evidence TEXT,
            parents TEXT,
            mode TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            raw_data TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp DESC);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_entity ON events(entity_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vessel_tracks (
            mmsi TEXT NOT NULL,
            imo TEXT,
            name TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            sog REAL,
            cog REAL,
            heading REAL,
            status TEXT DEFAULT 'underway',
            is_sanctioned INTEGER DEFAULT 0,
            has_gap INTEGER DEFAULT 0,
            last_seen TEXT NOT NULL,
            track_points TEXT,
            PRIMARY KEY(mmsi)
        )
    """)
    conn.commit()
    conn.close()

def save_event(event: Event) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO events (
            id, type, source, rule_id, entity_id, entity_name, entity_type,
            lat, lon, sog, cog, heading, severity, confidence, title, summary,
            brief, is_fallback, reasoning, evidence, parents, mode, timestamp, raw_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event.id,
        event.type.value,
        event.source,
        event.rule_id,
        event.entity_id,
        event.entity_name,
        event.entity_type,
        event.lat,
        event.lon,
        event.sog,
        event.cog,
        event.heading,
        event.severity.value,
        event.confidence.value,
        event.title,
        event.summary,
        event.brief,
        1 if event.is_fallback else 0,
        json.dumps(event.reasoning),
        json.dumps([e.model_dump() for e in event.evidence]),
        json.dumps(event.parents),
        event.mode.value,
        event.timestamp,
        json.dumps(event.raw_data) if event.raw_data else None
    ))
    conn.commit()
    conn.close()

def get_events(
    limit: int = 50,
    offset: int = 0,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    mode: Optional[str] = None
) -> List[Event]:
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM events WHERE 1=1"
    params = []
    
    if event_type:
        query += " AND type = ?"
        params.append(event_type)
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    if mode:
        query += " AND mode = ?"
        params.append(mode)
        
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    events = []
    for r in rows:
        evidence_list = [EvidenceRef(**e) for e in json.loads(r["evidence"] or "[]")]
        events.append(Event(
            id=r["id"],
            type=r["type"],
            source=r["source"],
            rule_id=r["rule_id"],
            entity_id=r["entity_id"],
            entity_name=r["entity_name"],
            entity_type=r["entity_type"],
            lat=r["lat"],
            lon=r["lon"],
            sog=r["sog"],
            cog=r["cog"],
            heading=r["heading"],
            severity=r["severity"],
            confidence=r["confidence"],
            title=r["title"],
            summary=r["summary"],
            brief=r["brief"],
            is_fallback=bool(r["is_fallback"]),
            reasoning=json.loads(r["reasoning"] or "[]"),
            evidence=evidence_list,
            parents=json.loads(r["parents"] or "[]"),
            mode=r["mode"],
            timestamp=r["timestamp"],
            raw_data=json.loads(r["raw_data"]) if r["raw_data"] else None
        ))
    return events

def get_event_by_id(event_id: str) -> Optional[Event]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    evidence_list = [EvidenceRef(**e) for e in json.loads(r["evidence"] or "[]")]
    return Event(
        id=r["id"],
        type=r["type"],
        source=r["source"],
        rule_id=r["rule_id"],
        entity_id=r["entity_id"],
        entity_name=r["entity_name"],
        entity_type=r["entity_type"],
        lat=r["lat"],
        lon=r["lon"],
        sog=r["sog"],
        cog=r["cog"],
        heading=r["heading"],
        severity=r["severity"],
        confidence=r["confidence"],
        title=r["title"],
        summary=r["summary"],
        brief=r["brief"],
        is_fallback=bool(r["is_fallback"]),
        reasoning=json.loads(r["reasoning"] or "[]"),
        evidence=evidence_list,
        parents=json.loads(r["parents"] or "[]"),
        mode=r["mode"],
        timestamp=r["timestamp"],
        raw_data=json.loads(r["raw_data"]) if r["raw_data"] else None
    )

def update_vessel_state(
    mmsi: str,
    lat: float,
    lon: float,
    name: Optional[str] = None,
    imo: Optional[str] = None,
    sog: Optional[float] = None,
    cog: Optional[float] = None,
    heading: Optional[float] = None,
    is_sanctioned: bool = False,
    has_gap: bool = False,
    timestamp: Optional[str] = None
):
    conn = get_connection()
    cur = conn.cursor()
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    
    cur.execute("SELECT track_points, name, imo FROM vessel_tracks WHERE mmsi = ?", (mmsi,))
    existing = cur.fetchone()
    
    track = []
    if existing and existing["track_points"]:
        track = json.loads(existing["track_points"])
    
    # Append current position (capped at last 50 points)
    track.append({"lat": lat, "lon": lon, "ts": ts})
    if len(track) > 50:
        track = track[-50:]
        
    resolved_name = name or (existing["name"] if existing else "Unknown")
    resolved_imo = imo or (existing["imo"] if existing else None)
    
    cur.execute("""
        INSERT INTO vessel_tracks (
            mmsi, imo, name, lat, lon, sog, cog, heading, is_sanctioned, has_gap, last_seen, track_points
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(mmsi) DO UPDATE SET
            lat = excluded.lat,
            lon = excluded.lon,
            name = COALESCE(excluded.name, vessel_tracks.name),
            imo = COALESCE(excluded.imo, vessel_tracks.imo),
            sog = excluded.sog,
            cog = excluded.cog,
            heading = excluded.heading,
            is_sanctioned = MAX(vessel_tracks.is_sanctioned, excluded.is_sanctioned),
            has_gap = excluded.has_gap,
            last_seen = excluded.last_seen,
            track_points = excluded.track_points
    """, (
        mmsi, resolved_imo, resolved_name, lat, lon, sog, cog, heading,
        1 if is_sanctioned else 0, 1 if has_gap else 0, ts, json.dumps(track)
    ))
    conn.commit()
    conn.close()

def get_vessel_tracks() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vessel_tracks")
    rows = cur.fetchall()
    conn.close()
    vessels = []
    for r in rows:
        vessels.append({
            "mmsi": r["mmsi"],
            "imo": r["imo"],
            "name": r["name"],
            "lat": r["lat"],
            "lon": r["lon"],
            "sog": r["sog"],
            "cog": r["cog"],
            "heading": r["heading"],
            "status": r["status"],
            "is_sanctioned": bool(r["is_sanctioned"]),
            "has_gap": bool(r["has_gap"]),
            "last_seen": r["last_seen"],
            "track_points": json.loads(r["track_points"] or "[]")
        })
    return vessels

def reset_database():
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM events")
    cur.execute("DELETE FROM vessel_tracks")
    conn.commit()
    conn.close()
