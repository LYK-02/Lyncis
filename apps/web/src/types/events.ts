export type Severity = "info" | "low" | "medium" | "high";
export type Confidence = "low" | "medium" | "high";
export type EventType = "observation" | "ais_gap" | "sanctions_match" | "correlated" | "hotspot" | "domain_exposure";
export type Mode = "live" | "replay" | "sample";

export interface EvidenceRef {
  id: string;
  source: string;
  url?: string | null;
  label: string;
  retrieved_at: string;
}

export interface Event {
  id: string;
  type: EventType;
  source: string;
  rule_id?: string | null;
  entity_id?: string | null;
  entity_name?: string | null;
  entity_type?: string | null;
  lat?: number | null;
  lon?: number | null;
  sog?: number | null;
  cog?: number | null;
  heading?: number | null;
  severity: Severity;
  confidence: Confidence;
  title: string;
  summary: string;
  brief?: string | null;
  is_fallback?: boolean;
  reasoning: string[];
  evidence: EvidenceRef[];
  parents: string[];
  mode: Mode;
  timestamp: string;
  raw_data?: Record<string, unknown> | null;
}

export interface TrackPoint {
  lat: number;
  lon: number;
  ts: string;
}

export interface VesselTrack {
  mmsi: string;
  imo?: string | null;
  name: string;
  lat: number;
  lon: number;
  sog?: number | null;
  cog?: number | null;
  heading?: number | null;
  status: string;
  is_sanctioned: boolean;
  has_gap: boolean;
  last_seen: string;
  track_points: TrackPoint[];
}

export interface SourceHealth {
  source_id: string;
  name: string;
  status: "ok" | "degraded" | "down";
  mode: Mode;
  last_success?: string | null;
  error_count: number;
  message_count: number;
  latency_ms?: number | null;
}

export interface ReplayStatus {
  is_playing: boolean;
  speed: number;
  current_time_sec: number;
  total_duration_sec: number;
  total_events: number;
  current_event_index: number;
  scenario_name: string;
}
