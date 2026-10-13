# Lyncis — Memory & Context

## Project Identity
- **Name:** Lyncis ("Every signal. One story.")
- **Scope:** Open-Source Maritime & Infrastructure Intelligence (OSINT) Platform
- **Core Modules:**
  - **GhostWake:** AIS gap detection & speed-aware anomaly tracking.
  - **SanctionWeb:** OpenSanctions cross-matching on IMO/MMSI with entity graph.
  - **AeroThermal:** NASA FIRMS thermal hotspots co-located with maritime tracks.
  - **ShadowTrace:** Passive Certificate Transparency infrastructure mapping.
  - **AI Briefs:** LLM wording generation with strict template fallback and banned-term filtering.
- **Timeline:** 4 days delivery plan.

---

## Phase Status Summary

### Phase 0 — Data Validation: COMPLETED & GATE PASSED ✅
- OpenSanctions: Ingested official `maritime.csv` into SQLite (`data/sanctions/sanctions.db`, 23,651 entities, 0.027ms query latency).
- AISStream: Validator tool `scripts/validate_aisstream.py` tested and functional.
- Golden Scenario Replay: `data/replay/golden_scenario.jsonl` generated (521 events, 30 min, target vessel `SEAPRIDE` exhibiting 14-min AIS gap).
- crt.sh & NASA FIRMS: Assessed, fail-safes established, feature-flagged.
- Docs & Config: `docs/data-sources.md` created; `.env.example` created.

### Phase 1 — Core Skeleton: COMPLETED & GATE PASSED ✅
- **Monorepo Layout**:
  - `apps/api`: FastAPI backend with event bus, SQLite storage, replay engine, and WebSocket streaming. All 7 unit/integration tests passing.
  - `apps/web`: Next.js 16.4 / React 19 / Tailwind CSS 4 console. Production build compiled cleanly without errors.
- **Unified Event Schema**:
  - Pydantic models in Python + TypeScript definitions in frontend. Enforces Rule P1–P5 (neutral terminology, confidence, reasoning, evidence citations).
- **Backend Services**:
  - SQLite event & track store (`apps/api/app/db/database.py`).
  - In-memory async pub/sub Event Bus (`apps/api/app/bus/event_bus.py`).
  - Replay Engine simulating real-time playback at 1x/5x/20x/50x speeds (`apps/api/app/replay/engine.py`).
  - Endpoints: `/healthz`, `/readyz`, `/events`, `/events/{id}`, `/vessels`, `/sources`, `/replay/start`, `/replay/pause`, `/replay/seek`, `/replay/reset`.
  - WebSocket hub `/ws/events` streaming telemetry and heartbeats.
- **Console UI Components**:
  - `TopBar`: Brand mark, LIVE/REPLAY badge, UTC clock, source health telemetry.
  - `FilterRail`: Module selector, severity filtering, search query input, real-time stats count.
  - `MapConsole`: Dark coordinate grid map, real-time vessel markers rotated by heading, motion trails, AIS gap radar pulse, and selection sync.
  - `EventFeed`: Live and replay signal feed with severity color bars, confidence tags, rule IDs.
  - `EventDrawer`: Slide-out inspector with AI-written summary, reasoning caveats, and external evidence links.
  - `ReplayBar`: Timeline scrubber, play/pause, speed selector, reset.
- **Gate Automated Test**: Passed via `scripts/phase1/verify_phase1_gate.py`.

---

## Next Up: Phase 2 — GhostWake (AIS Gap Detection)
From `03-PHASES.md`:
- [ ] AISStream adapter with reconnect and backoff.
- [ ] Vessel state tracker (last seen, last speed).
- [ ] Gap detector with speed-aware thresholds.
- [ ] Port and anchorage polygon filter; coverage-hole mask.
- [ ] STS proximity detector (P1).
- [ ] Vessel track layer and gap pulse on the map.
- [ ] Unit tests with synthetic and recorded fixtures.
- **Gate:** On the recorded session, gaps are flagged with sensible reasoning; false positives manually reviewed and documented.
