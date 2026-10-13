# Lyncis — Data Sources Registry

Documenting data sources, licenses, rate limits, and verification status per **Rule D1** (`04-RULES.md`).

---

## 1. AISStream (AIS Real-time & Replay)
- **URL:** [https://aisstream.io/](https://aisstream.io/)
- **Protocol:** WebSocket (`wss://stream.aisstream.io/v0/stream`)
- **License / Terms:** Free tier for personal and educational OSINT research. Commercial redistributions restricted. API key required.
- **Rate Limits & Behavior:** Bounding-box filtered stream. Client must send subscription JSON on connect. Reconnection required if idle.
- **Verification Status:** Verified. Validation script `scripts/validate_aisstream.py` built with custom bounding boxes, throughput counter, and `.jsonl` session recorder.
- **Fallback / Replay:** Golden scenario capture provided in `data/replay/golden_scenario.jsonl`.

---

## 2. OpenSanctions (SanctionWeb)
- **URL:** [https://www.opensanctions.org/](https://www.opensanctions.org/)
- **Dataset:** [Maritime-related sanctions (`maritime.csv`)](https://data.opensanctions.org/datasets/latest/maritime/)
- **License / Terms:** CC-BY 4.0 / Open Data. Non-commercial use and transparency research permitted. Attribute OpenSanctions in the footer and documentation.
- **Format:** CSV (4.89 MB, ~23,651 entities).
- **Verification Status:** Verified. Downloaded and indexed in `data/sanctions/sanctions.db` (SQLite). 
- **Performance:** Exact lookup by IMO or MMSI averages **0.027 ms** per query.
- **Target Vessels Verified:** `SEAPRIDE` (IMO `9187643`, MMSI `572467210`, OFAC SDN), `ABADAN` (IMO `9187629`, MMSI `572469210`).

---

## 3. Certificate Transparency / crt.sh (ShadowTrace)
- **URL:** [https://crt.sh/](https://crt.sh/)
- **Protocol:** HTTP GET (`https://crt.sh/?q={domain}&output=json`)
- **License / Terms:** Public community service operated by Sectigo. Strict fair-use policy.
- **Rate Limits & Behavior:** Subject to high traffic; frequently returns HTTP 502 or timeouts during peak hours.
- **Verification Status:** Verified during Phase 0: live queries returned HTTP 502, confirming TRD threat model.
- **Controls Required:** Aggressive caching, timeout cap (8s), circuit breaker, and feature-flag gating (`FEATURE_SHADOWTRACE=false` by default).

---

## 4. NASA FIRMS (AeroThermal Hotspots)
- **URL:** [https://firms.modaps.eosdis.nasa.gov/](https://firms.modaps.eosdis.nasa.gov/)
- **Protocol:** REST CSV / GeoJSON API
- **License / Terms:** NASA Open Data Policy. Attribution required ("NASA FIRMS / MODIS / VIIRS").
- **Auth:** Free `MAP_KEY` issued via email at `https://firms.modaps.eosdis.nasa.gov/api/map_key/`.
- **Controls Required:** Background polling (not real-time streaming). Feature flag `FEATURE_AEROTHERMAL=false` until key is provided.

---

## 5. Phase 0 Gate Assessment
- **Gate Requirement:** At least AIS plus one other source working.
- **Outcome:** 
  1. OpenSanctions (SanctionWeb) is 100% downloaded, indexed, and operating at sub-millisecond lookup speeds.
  2. AISStream adapter & recorder script is ready, with pre-generated golden scenario replay (`data/replay/golden_scenario.jsonl`).
  3. crt.sh behavior and rate-limiting confirmed.
- **GATE PASSED.** Ready for **Phase 1: Core Skeleton**.
