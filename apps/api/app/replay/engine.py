"""
Replay Engine (Lyncis Core)
Loads JSONL AIS captures, simulates real-time stream at 1x/5x/20x speed,
detects gaps, matches sanctions, and broadcasts events through the event bus.
"""

import os
import json
import time
import asyncio
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from app.config import settings
from app.schemas.events import Event, EventType, Severity, Confidence, EvidenceRef, Mode, ReplayStatus
from app.bus.event_bus import event_bus
from app.db.database import update_vessel_state, reset_database
from app.sources.sanctions_matcher import check_sanctions

class ReplayEngine:
    def __init__(self):
        self.is_playing: bool = False
        self.speed: float = 5.0  # Default 5x for demo per 06-APPFLOW.md
        self.current_time_sec: float = 0.0
        self.scenario_name: str = settings.DEFAULT_SCENARIO
        self.total_duration_sec: float = 1800.0
        self.events_cache: List[Dict[str, Any]] = []
        self.current_index: int = 0
        self._task: Optional[asyncio.Task] = None
        
        # State tracking during playback
        self._vessel_last_seen: Dict[str, float] = {}   # mmsi -> last report sim_time_sec
        self._vessel_last_speed: Dict[str, float] = {}  # mmsi -> last sog
        self._vessel_gap_flagged: Dict[str, bool] = {}  # mmsi -> bool
        self._vessel_sanctions_cached: Dict[str, Dict[str, Any]] = {}
        self._emitted_event_ids: set = set()

    def load_scenario(self, filename: Optional[str] = None) -> bool:
        name = filename or self.scenario_name
        path = os.path.join(settings.REPLAY_DIR, name)
        if not os.path.exists(path):
            print(f"[-] Replay scenario file not found: {path}")
            return False
            
        self.events_cache.clear()
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        self.events_cache.append(json.loads(line))
                    except Exception:
                        pass
                        
        self.scenario_name = name
        self.current_index = 0
        self.current_time_sec = 0.0
        self.total_duration_sec = 1800.0
        print(f"[+] Loaded replay scenario '{name}' ({len(self.events_cache)} raw records)")
        return True

    def get_status(self) -> ReplayStatus:
        return ReplayStatus(
            is_playing=self.is_playing,
            speed=self.speed,
            current_time_sec=self.current_time_sec,
            total_duration_sec=self.total_duration_sec,
            total_events=len(self.events_cache),
            current_event_index=self.current_index,
            scenario_name=self.scenario_name
        )

    def start(self, speed: Optional[float] = None, scenario: Optional[str] = None):
        if speed is not None:
            self.speed = max(0.5, min(100.0, speed))
            
        if scenario and scenario != self.scenario_name:
            self.load_scenario(scenario)
        elif not self.events_cache:
            self.load_scenario()
            
        self.is_playing = True
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run_loop())
        print(f"[+] Replay started (speed: {self.speed}x)")

    def pause(self):
        self.is_playing = False
        print("[*] Replay paused")

    def seek(self, seconds: float):
        self.current_time_sec = max(0.0, min(self.total_duration_sec, seconds))
        # Recalculate index
        # Assuming 60 steps over 1800 seconds (30s intervals)
        target_step = int(self.current_time_sec / 30.0)
        self.current_index = min(len(self.events_cache) - 1, target_step * 9)
        print(f"[*] Replay seek to {self.current_time_sec:.1f}s (index {self.current_index})")

    def reset(self):
        self.pause()
        self.current_time_sec = 0.0
        self.current_index = 0
        self._vessel_last_seen.clear()
        self._vessel_last_speed.clear()
        self._vessel_gap_flagged.clear()
        self._vessel_sanctions_cached.clear()
        self._emitted_event_ids.clear()
        reset_database()
        print("[*] Replay reset to t=0")

    async def _run_loop(self):
        tick_interval = 0.2  # 200ms tick
        while self.is_playing and self.current_index < len(self.events_cache):
            sim_advance = tick_interval * self.speed
            self.current_time_sec += sim_advance
            
            # Process records up to current_time_sec
            while self.current_index < len(self.events_cache):
                record = self.events_cache[self.current_index]
                meta = record.get("MetaData", {})
                time_utc_str = meta.get("time_utc", "")
                
                # Check simulated timestamp
                # First record is at t=0
                # Approximate 9 records per 30-sec step
                record_sim_sec = (self.current_index // 9) * 30.0
                if record_sim_sec > self.current_time_sec:
                    break
                    
                await self._process_record(record, record_sim_sec)
                self.current_index += 1

            # Anomaly check: evaluate vessels for gaps at current simulated time
            await self._check_gap_anomalies(self.current_time_sec)
            
            await asyncio.sleep(tick_interval)

        if self.current_index >= len(self.events_cache):
            self.is_playing = False
            print("[+] Replay reached end of scenario")

    async def _process_record(self, record: Dict[str, Any], sim_sec: float):
        msg_type = record.get("MessageType")
        meta = record.get("MetaData", {})
        mmsi = str(meta.get("MMSI") or meta.get("MMSI_String") or "")
        ship_name = meta.get("ShipName", "").strip() or "Unknown Vessel"
        imo = str(meta.get("IMO") or "")
        
        pos_data = record.get("Message", {}).get("PositionReport", {})
        lat = pos_data.get("Latitude", meta.get("latitude", 0.0))
        lon = pos_data.get("Longitude", meta.get("longitude", 0.0))
        sog = pos_data.get("Sog")
        cog = pos_data.get("Cog")
        heading = pos_data.get("TrueHeading")
        
        if not mmsi or (lat == 0.0 and lon == 0.0):
            return

        # Check sanctions in SQLite index
        is_sanctioned = False
        sanction_match = self._vessel_sanctions_cached.get(mmsi)
        if sanction_match is None:
            sanction_match = check_sanctions(mmsi=mmsi, imo=imo, name=ship_name)
            if sanction_match:
                self._vessel_sanctions_cached[mmsi] = sanction_match
                # Emit Sanction Match Event once per vessel
                ev_id = f"sanction_{mmsi}"
                if ev_id not in self._emitted_event_ids:
                    self._emitted_event_ids.add(ev_id)
                    datasets = sanction_match.get("datasets", "sanctions_list")
                    url = sanction_match.get("url") or f"https://www.opensanctions.org/entities/{sanction_match.get('id')}"
                    
                    event = Event(
                        id=ev_id,
                        type=EventType.SANCTIONS_MATCH,
                        source="sanctionweb",
                        rule_id="R2",
                        entity_id=mmsi,
                        entity_name=ship_name,
                        entity_type="vessel",
                        lat=lat,
                        lon=lon,
                        sog=sog,
                        cog=cog,
                        severity=Severity.HIGH,
                        confidence=Confidence.HIGH,
                        title=f"Vessel identifier matches sanctions-list record: {ship_name}",
                        summary=f"MMSI {mmsi} / IMO {imo} matches active sanction dataset ({datasets}).",
                        brief=f"Vessel {ship_name} observed in corridor. Identifier corresponds to official designated entity under {datasets}. Review source record.",
                        is_fallback=True,
                        reasoning=[
                            f"Exact match on MMSI {mmsi} against OpenSanctions registry.",
                            f"Designated under dataset: {datasets}.",
                            "No assertion of current wrongdoing; verification required via cited record."
                        ],
                        evidence=[
                            EvidenceRef(
                                id=f"ev_sanction_{mmsi}",
                                source="opensanctions",
                                url=url,
                                label=f"OpenSanctions Entity {sanction_match.get('id')}",
                                retrieved_at=datetime.now(timezone.utc).isoformat()
                            )
                        ],
                        mode=Mode.REPLAY,
                        timestamp=meta.get("time_utc", datetime.now(timezone.utc).isoformat())
                    )
                    await event_bus.publish(event)
                    
        is_sanctioned = bool(sanction_match)
        
        # Check if vessel was in a gap that has now closed
        has_gap = self._vessel_gap_flagged.get(mmsi, False)
        if has_gap and (sim_sec - self._vessel_last_seen.get(mmsi, sim_sec)) > 300.0:
            # Vessel reappeared!
            elapsed_min = int((sim_sec - self._vessel_last_seen.get(mmsi, sim_sec)) / 60.0)
            self._vessel_gap_flagged[mmsi] = False
            ev_id = f"gap_close_{mmsi}_{int(sim_sec)}"
            if ev_id not in self._emitted_event_ids:
                self._emitted_event_ids.add(ev_id)
                event = Event(
                    id=ev_id,
                    type=EventType.OBSERVATION,
                    source="ghostwake",
                    rule_id="R1_CLOSED",
                    entity_id=mmsi,
                    entity_name=ship_name,
                    entity_type="vessel",
                    lat=lat,
                    lon=lon,
                    sog=sog,
                    cog=cog,
                    severity=Severity.INFO,
                    confidence=Confidence.HIGH,
                    title=f"AIS transmission resumed for {ship_name}",
                    summary=f"Vessel reported new position after {elapsed_min} min without AIS reports.",
                    brief=f"Vessel {ship_name} resumed AIS transmissions after {elapsed_min} minutes. Observed speed {sog} kn, heading {heading}°.",
                    is_fallback=True,
                    reasoning=[
                        f"Previous transmission was at t={int(self._vessel_last_seen.get(mmsi, 0))}s.",
                        f"Reappearance coordinates: lat {lat:.3f}, lon {lon:.3f}."
                    ],
                    evidence=[
                        EvidenceRef(
                            id=f"ev_resume_{mmsi}",
                            source="aisstream",
                            url=None,
                            label="AISStream PositionReport",
                            retrieved_at=datetime.now(timezone.utc).isoformat()
                        )
                    ],
                    mode=Mode.REPLAY,
                    timestamp=meta.get("time_utc", datetime.now(timezone.utc).isoformat())
                )
                await event_bus.publish(event)

        # Update tracking state
        self._vessel_last_seen[mmsi] = sim_sec
        if sog is not None:
            self._vessel_last_speed[mmsi] = sog

        # Update DB vessel state
        update_vessel_state(
            mmsi=mmsi,
            lat=lat,
            lon=lon,
            name=ship_name,
            imo=imo,
            sog=sog,
            cog=cog,
            heading=heading,
            is_sanctioned=is_sanctioned,
            has_gap=self._vessel_gap_flagged.get(mmsi, False),
            timestamp=meta.get("time_utc")
        )

    async def _check_gap_anomalies(self, current_sim_sec: float):
        # Scan vessels that have stopped transmitting while cruising
        # Gap threshold: 6 minutes (360 seconds) without report if previous speed > 5 kn
        for mmsi, last_seen in self._vessel_last_seen.items():
            silence_sec = current_sim_sec - last_seen
            last_sog = self._vessel_last_speed.get(mmsi, 0.0)
            
            if silence_sec >= 360.0 and last_sog >= 5.0 and not self._vessel_gap_flagged.get(mmsi, False):
                self._vessel_gap_flagged[mmsi] = True
                elapsed_min = int(silence_sec / 60.0)
                ev_id = f"ais_gap_{mmsi}_{int(last_seen)}"
                
                if ev_id not in self._emitted_event_ids:
                    self._emitted_event_ids.add(ev_id)
                    
                    # 1. Emit AIS Gap Event
                    gap_event = Event(
                        id=ev_id,
                        type=EventType.AIS_GAP,
                        source="ghostwake",
                        rule_id="R1",
                        entity_id=mmsi,
                        entity_name=self._get_vessel_name(mmsi),
                        entity_type="vessel",
                        sog=last_sog,
                        severity=Severity.MEDIUM,
                        confidence=Confidence.LOW,
                        title=f"Possible AIS gap of {elapsed_min} min; reason unknown: {self._get_vessel_name(mmsi)}",
                        summary=f"Vessel was underway at {last_sog} kn. No AIS transmissions received for {elapsed_min} minutes.",
                        brief=f"Observed AIS gap for {self._get_vessel_name(mmsi)} in navigation corridor. Last reported speed was {last_sog} kn. Reasons may include receiver coverage, interference, or equipment failure.",
                        is_fallback=True,
                        reasoning=[
                            f"Vessel was moving at {last_sog} knots when transmissions halted.",
                            f"Duration exceeds 6-minute threshold ({elapsed_min} min elapsed).",
                            "Coverage-hole or equipment anomaly cannot be ruled out."
                        ],
                        evidence=[
                            EvidenceRef(
                                id=f"ev_gap_{mmsi}",
                                source="aisstream",
                                url="https://aisstream.io",
                                label="AISStream Transmission Gap Log",
                                retrieved_at=datetime.now(timezone.utc).isoformat()
                            )
                        ],
                        mode=Mode.REPLAY,
                        timestamp=datetime.now(timezone.utc).isoformat()
                    )
                    await event_bus.publish(gap_event)
                    
                    # 2. Check if this vessel has a sanction match -> Fire Rule R3 (Correlated Event)
                    sanction_data = self._vessel_sanctions_cached.get(mmsi)
                    if sanction_data:
                        corr_id = f"corr_gap_sanction_{mmsi}_{int(last_seen)}"
                        if corr_id not in self._emitted_event_ids:
                            self._emitted_event_ids.add(corr_id)
                            corr_event = Event(
                                id=corr_id,
                                type=EventType.CORRELATED,
                                source="correlation_engine",
                                rule_id="R3",
                                entity_id=mmsi,
                                entity_name=self._get_vessel_name(mmsi),
                                entity_type="vessel",
                                sog=last_sog,
                                severity=Severity.MEDIUM,
                                confidence=Confidence.MEDIUM,
                                title=f"Correlated Signal: Possible AIS gap on vessel matching sanctions record",
                                summary=f"Signal correlation: vessel {self._get_vessel_name(mmsi)} exhibits {elapsed_min} min AIS gap and matches designated entity registry.",
                                brief=f"Correlated observation for {self._get_vessel_name(mmsi)}. Vessel matches sanctions registry ({sanction_data.get('datasets')}) and exhibited an unannounced AIS gap while cruising at {last_sog} kn. Verification recommended.",
                                is_fallback=True,
                                reasoning=[
                                    f"Parent 1: AIS transmission interruption of {elapsed_min} min (Rule R1).",
                                    f"Parent 2: Exact identifier match in {sanction_data.get('datasets')} (Rule R2).",
                                    "Both signals co-occur within the same operational window.",
                                    "Observation does not prove intent; source review required."
                                ],
                                evidence=[
                                    EvidenceRef(
                                        id=f"ev_corr_ais_{mmsi}",
                                        source="aisstream",
                                        url=None,
                                        label="AISStream Gap Observation",
                                        retrieved_at=datetime.now(timezone.utc).isoformat()
                                    ),
                                    EvidenceRef(
                                        id=f"ev_corr_sanct_{mmsi}",
                                        source="opensanctions",
                                        url=sanction_data.get("url"),
                                        label=f"OpenSanctions Registry Entry ({sanction_data.get('id')})",
                                        retrieved_at=datetime.now(timezone.utc).isoformat()
                                    )
                                ],
                                parents=[gap_event.id, f"sanction_{mmsi}"],
                                mode=Mode.REPLAY,
                                timestamp=datetime.now(timezone.utc).isoformat()
                            )
                            await event_bus.publish(corr_event)

    def _get_vessel_name(self, mmsi: str) -> str:
        s = self._vessel_sanctions_cached.get(mmsi)
        if s and s.get("caption"):
            return s.get("caption")
        return f"MMSI {mmsi}"

# Global singleton
replay_engine = ReplayEngine()
