"""
Lyncis Event Schema (Source of Truth)
Binding schema for observations, gap events, sanctions matches, and correlated alerts.
Strictly adheres to 04-RULES.md (Rules P1, P2, P3, P4, P5, A4, A7).
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator

class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EventType(str, Enum):
    OBSERVATION = "observation"
    AIS_GAP = "ais_gap"
    SANCTIONS_MATCH = "sanctions_match"
    CORRELATED = "correlated"
    HOTSPOT = "hotspot"
    DOMAIN_EXPOSURE = "domain_exposure"

class Mode(str, Enum):
    LIVE = "live"
    REPLAY = "replay"
    SAMPLE = "sample"

class EvidenceRef(BaseModel):
    id: str = Field(..., description="Unique ID for this evidence reference")
    source: str = Field(..., description="Source name (e.g., opensanctions, aisstream, firms)")
    url: Optional[str] = Field(None, description="External verification URL")
    label: str = Field(..., description="Human-readable title/description of the source record")
    retrieved_at: str = Field(..., description="ISO-8601 UTC timestamp")

# Banned terms list per 04-RULES.md §2 (Language Rules)
BANNED_TERMS = [
    "dark fleet", "smuggling", "illegal", "guilty", "criminal", 
    "confirmed violation", "evading sanctions", "sanction evasion"
]

class Event(BaseModel):
    id: str = Field(..., description="Deterministic hash or UUID")
    type: EventType
    source: str = Field(..., description="Detector or module (ghostwake, sanctionweb, aerothermal, etc.)")
    rule_id: Optional[str] = Field(None, description="Rule identifier (e.g., R1, R2, R3)")
    
    # Target entity details
    entity_id: Optional[str] = Field(None, description="MMSI, IMO, Domain, or Region identifier")
    entity_name: Optional[str] = Field(None, description="Vessel name, org name, or entity label")
    entity_type: Optional[str] = Field("vessel", description="vessel, organization, infrastructure, etc.")
    
    # Coordinates & Motion
    lat: Optional[float] = None
    lon: Optional[float] = None
    sog: Optional[float] = Field(None, description="Speed over ground in knots")
    cog: Optional[float] = Field(None, description="Course over ground in degrees")
    heading: Optional[float] = None
    
    # Classification
    severity: Severity = Severity.INFO
    confidence: Confidence = Confidence.LOW
    
    # Textual Content
    title: str = Field(..., description="Short hedged summary title")
    summary: str = Field(..., description="Factual description of what was observed")
    brief: Optional[str] = Field(None, description="AI or template generated synthesis brief")
    is_fallback: bool = Field(False, description="True if brief was produced by deterministic fallback template")
    
    # Evidence & Audit
    reasoning: List[str] = Field(default_factory=list, description="Step-by-step reasoning points and caveats")
    evidence: List[EvidenceRef] = Field(default_factory=list, description="Mandatory evidence citations per Rule P2")
    parents: List[str] = Field(default_factory=list, description="Parent event IDs if correlated")
    
    # Metadata
    mode: Mode = Mode.REPLAY
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_data: Optional[Dict[str, Any]] = None

    @field_validator("title", "summary", "brief")
    @classmethod
    def validate_no_banned_terms(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        lower_v = v.lower()
        for banned in BANNED_TERMS:
            if banned in lower_v:
                raise ValueError(f"Language Rule Violation: text contains prohibited term '{banned}'")
        return v

class SourceHealth(BaseModel):
    source_id: str
    name: str
    status: str = Field("ok", description="ok, degraded, or down")
    mode: Mode = Mode.REPLAY
    last_success: Optional[str] = None
    error_count: int = 0
    message_count: int = 0
    latency_ms: Optional[float] = None

class ReplayStatus(BaseModel):
    is_playing: bool = False
    speed: float = 1.0
    current_time_sec: float = 0.0
    total_duration_sec: float = 1800.0
    total_events: int = 0
    current_event_index: int = 0
    scenario_name: str = "golden_scenario.jsonl"
