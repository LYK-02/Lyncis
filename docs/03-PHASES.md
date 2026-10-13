# 03 — Delivery Phases

**Principle:** build the thinnest end-to-end slice first, then widen. Never start a phase before the previous gate passes.

---

## Phase Overview

| Phase | Name | Outcome | Gate |
|---|---|---|---|
| 0 | Data validation | Know which sources really work | 2 live sources returning data |
| 1 | Core skeleton | Map, feed, event bus, replay | Replay file plays on the map |
| 2 | GhostWake | AIS gap detection live | Gap events appear with reasoning |
| 3 | SanctionWeb + correlation | Cross-source linking | Golden scenario passes |
| 4 | AI briefs + polish | Briefs, design, animation | Demo runs 3 min with no errors |
| 5 | Stretch modules | AeroThermal, ShadowTrace | Each behind a feature flag |
| 6 | Hardening | Security, tests, docs, deploy | Production checklist complete |
| 7 | Roadmap | NarrativeEcho, watchlists, exports | Post-hackathon |

---

## Phase 0 — Data Validation (2–3 h)

**Do not skip.** Earlier research overclaimed several sources.

Tasks:
- [x] Register for the AISStream key; read the current terms and limits.
- [x] Write a ~30-line script that connects and prints messages for the chosen bounding box for 10 minutes.
- [x] Count distinct vessels and the average reports per vessel. If coverage is thin, pick another box.
- [x] Request a NASA FIRMS key and pull one day of hotspots for the same region.
- [x] Download the OpenSanctions bulk file; confirm the license for your use.
- [x] Test crt.sh for one domain you own; note timeouts.
- [x] Record a 30–60 min AIS capture to a file (check the terms before committing it to Git).

**Gate:** at least AIS plus one other source working. Otherwise re-plan: ShadowTrace-first is the fallback because it needs no stream.

## Phase 1 — Core Skeleton (4–6 h)

Tasks:
- [x] Monorepo, lint, format, CI (lint + tests).
- [x] Pydantic Event schema and TS types (generated from one source of truth).
- [x] FastAPI app, event bus, SQLite, `/events`, `/healthz`, `/ws/events`.
- [x] Replay engine and a fake source that emits test events.
- [x] Next.js console: MapLibre dark map, event feed, detail drawer.
- [x] Design tokens and base UI components (see DESIGN.md).

**Gate:** replaying a file shows markers moving on the map and the feed filling in.

## Phase 2 — GhostWake (6–8 h)

Tasks:
- [ ] AISStream adapter with reconnect and backoff.
- [ ] Vessel state tracker (last seen, last speed).
- [ ] Gap detector with speed-aware thresholds.
- [ ] Port and anchorage polygon filter; coverage-hole mask.
- [ ] STS proximity detector (P1).
- [ ] Vessel track layer and gap pulse on the map.
- [ ] Unit tests with synthetic and recorded fixtures.

**Gate:** on the recorded session, gaps are flagged with sensible reasoning; false positives manually reviewed and documented.

## Phase 3 — SanctionWeb + Correlation (5–7 h)

Tasks:
- [ ] Load OpenSanctions into SQLite; build lookup indexes on IMO and MMSI.
- [ ] Exact matcher, then fuzzy matcher (label **needs review**).
- [ ] YAML rule loader and engine; rules R1–R4.
- [ ] Entity graph endpoint and React Flow view.
- [ ] Build the **golden scenario** in a replay file.

**Gate:** the golden scenario test passes: gap → sanctions match → correlated event with parents.

## Phase 4 — AI Briefs, Design and Animation (6–8 h)

Tasks:
- [ ] LLM adapter, prompt, output validation, banned-term filter, template fallback.
- [ ] Landing page from the Lyncis theme.
- [ ] Console polish: glass cards, glow, severity colors.
- [ ] Animation pass (see ANIMATION.md), including reduced-motion.
- [ ] Demo script and slides; rehearse with the replay mode.

**Gate:** a full 3-minute demo with no console errors; works with the network off.

## Phase 5 — Stretch Modules (each time-boxed 4 h)

- **AeroThermal:** FIRMS poll, hotspot layer, wind arrows, rule R1.
- **ShadowTrace:** domain ownership check, crt.sh with caching, graph nodes, rule R6.

Each ships behind a feature flag. If a module is not demo-ready, it stays on the roadmap slide.

## Phase 6 — Hardening (post-demo, 1–2 weeks)

- Security review against SECURITY.md.
- Test coverage targets in PRODUCTION-PRACTICES.md.
- Observability, alerts, runbooks.
- Deploy to a persistent free host **(VERIFY current limits)**.
- Documentation and ADRs.

## Phase 7 — Roadmap

- NarrativeEcho (GDELT).
- Watchlists and email or webhook alerts.
- Report export (PDF).
- Postgres migration and multi-user auth.
- Additional regions and AIS sources.

---

## 48-Hour Hackathon Schedule (suggested)

| Hours | Focus |
|---|---|
| 0–3 | Phase 0 data validation, choose region |
| 3–10 | Phase 1 core |
| 10–20 | Phase 2 GhostWake |
| 20–28 | Phase 3 SanctionWeb + correlation |
| 28–38 | Phase 4 briefs, design, animation |
| 38–44 | Demo scenario, rehearsal, slides |
| 44–48 | Buffer, bug fixes, submission |

Sleep is scheduled. Tired teams ship bugs.

## 24-Hour Cut

Core + GhostWake + one SanctionWeb exact match + template briefs. Everything else goes on the roadmap slide.

## Scope-Cut Order (cut from the top)

1. ShadowTrace
2. AeroThermal
3. Entity graph (keep the list view)
4. Fuzzy sanctions matching
5. LLM briefs (keep templates)
6. STS detection
7. **Never cut:** replay mode, evidence links, confidence labels.

## Risks per Phase

| Phase | Top risk | Response |
|---|---|---|
| 0 | AIS coverage is thin | Change the bounding box or pivot to ShadowTrace-first |
| 1 | Over-engineering | Time-box to 6 h; use fake events early |
| 2 | Too many false positives | Increase thresholds, add masks, label "possible" |
| 3 | Name-matching noise | Exact-only for the demo; fuzzy flagged as review |
| 4 | Animation hurts performance | Transform/opacity only; disable on low-power devices |
