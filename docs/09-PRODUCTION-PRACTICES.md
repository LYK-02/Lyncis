# 09 — Production Rules and Good Practices

A checklist-style reference for taking Lyncis from a hackathon build to something you would trust in front of real users.

---

## 1. Production Readiness Levels

| Level | Meaning | Required |
|---|---|---|
| **L0 Demo** | Works on the presenter's laptop in replay mode | Golden scenario, replay, labels |
| **L1 Alpha** | Hosted, a few trusted users | CI, auth on control endpoints, backups, health checks |
| **L2 Beta** | Public with known limitations | Security checklist, monitoring, rate limits, limitations page |
| **L3 v1.0** | Reliable for routine use | SLOs, on-call runbooks, test coverage targets, accessibility audit |

State the current level in the README.

## 2. Reliability

### 2.1 Service Level Objectives (starting targets, hobby tier)
| SLI | SLO |
|---|---|
| API availability | 99% monthly |
| `/events` p95 latency | < 300 ms |
| Live event-to-UI latency p95 | < 5 s |
| Brief generation success (LLM or fallback) | 100% (fallback guarantees it) |

Do not promise source freshness; it depends on third parties.

### 2.2 Failure Handling Patterns
- **Retry with exponential backoff and jitter** for every external call; cap attempts.
- **Circuit breaker** per source: open after N consecutive failures, half-open probe every 60 s.
- **Timeouts** on everything: HTTP 10 s, LLM 8 s, WS heartbeat 30 s.
- **Bulkheads:** each adapter runs in its own task; one failure never blocks others.
- **Backpressure:** bounded queues; drop oldest raw observations before dropping detected events.
- **Idempotency:** deterministic event IDs (hash of the source key + time) so reprocessing never duplicates.
- **Graceful shutdown:** stop adapters, flush queue, close DB.

### 2.3 Graceful Degradation Matrix
| Failure | User impact | Behavior |
|---|---|---|
| AIS source down | No new vessel data | Banner, last known state marked stale, offer REPLAY |
| LLM down or limited | No AI wording | Template briefs |
| FIRMS down | No hotspot layer | Layer hidden with a notice; rules needing it pause |
| DB locked | Slow writes | WAL mode; short transactions; queue retry |
| WS disconnected | Live updates pause | Auto-reconnect and resync |

## 3. Data Quality and Provenance

- Every event stores source, retrieval time and original identifier.
- Validate coordinates (range, not 0,0), speeds (plausible max), and timestamps (not in the future).
- Deduplicate observations (same MMSI + timestamp).
- Track detector precision manually: keep a **review log** of flagged events labeled *true gap / coverage artifact / unclear*, and compute the false-positive rate per rule.
- Version the rules and thresholds; a change in a threshold is a code review item, not a silent config tweak.
- Refresh sanctions data on a schedule and store the dataset date shown in the UI.

## 4. Testing Standards

| Area | Target |
|---|---|
| Detectors and rules (unit) | ≥ 90% line coverage and all edge cases listed |
| API (integration) | Every endpoint has success, validation-error and auth-error tests |
| Adapters | Recorded fixtures; test reconnect and malformed messages |
| Frontend components | Key components and reducers via Vitest and Testing Library |
| E2E | Golden scenario in Playwright |
| Accessibility | axe checks in CI on landing and console |

**Edge cases to test for GhostWake:** vessel leaves the bounding box, vessel enters a port, duplicate timestamps, out-of-order messages, clock skew, very slow speed, message bursts after reconnect, MMSI reuse.

## 5. Code Review Checklist

- [ ] Does the change keep the language rules (no "dark fleet", "guilty")?
- [ ] Are new thresholds documented with a reason?
- [ ] Are external inputs validated and treated as untrusted?
- [ ] Is there a test for the failure path?
- [ ] Does it work in replay mode?
- [ ] Any new dependency justified and audited?
- [ ] Any secrets or personal data in logs, fixtures or screenshots?
- [ ] Is the UI state complete (loading, empty, error)?

## 6. Frontend Good Practice

- Server Components where possible; ship less JS.
- Lazy-load MapLibre, deck.gl and React Flow with dynamic imports.
- Virtualize the feed list (for example, TanStack Virtual).
- Keep map state outside React render cycles; batch updates per frame.
- Use `Intl` for times with explicit time zones (show UTC by default; analysts need it).
- Image optimization via `next/image`; fonts via `next/font` with `display: swap`.
- Error boundaries around the map, graph and drawer so a crash in one does not kill the page.
- Do not store tokens in `localStorage`.

## 7. Backend Good Practice

- Async I/O end to end; no blocking calls in the event loop (run CPU-heavy geo work in a thread pool).
- Dependency injection for adapters and the clock, so tests control time.
- Spatial indexing (H3 cells or an R-tree) for proximity checks instead of O(n²) loops.
- Configuration in one validated settings object.
- Structured logging with correlation IDs.
- OpenAPI docs generated; keep the examples current.
- Type everything; fail CI on mypy errors.

## 8. Accessibility (target WCAG 2.2 AA)

- Text contrast ≥ 4.5:1 on the dark theme (check green-on-black and gray secondary text).
- Severity never conveyed by color alone.
- Full keyboard operation of feed, filters, drawer and replay bar.
- Visible focus indicators.
- `aria-live="polite"` for new events, rate-limited.
- Alt text or labels for map controls; a table view alternative to the map for screen reader users.
- Respect reduced motion (see ANIMATION.md).

## 9. Performance Good Practice

- Measure with Lighthouse and the Chrome Performance panel; set budgets in CI (bundle size check).
- Cache API responses with ETag or short TTLs; cache third-party lookups aggressively (crt.sh, sanctions).
- Debounce filter inputs (200 ms).
- Use `Cache-Control` for static assets; immutable hashed filenames.
- Compress API responses (gzip or zstd).

## 10. Documentation Standards

| Doc | Content |
|---|---|
| README | What it is, screenshot or GIF, quick start (one command), limitations, ethics, license |
| `docs/data-sources.md` | Each source: link, key needed, limits, terms, how used, last verified date |
| `docs/limitations.md` | AIS coverage, false positives, latency, what Lyncis does not prove |
| `docs/adr/` | Architecture decision records |
| `docs/runbook.md` | Restart, rollback, rotate keys, restore backup |
| `CONTRIBUTING.md` | Setup, branch naming, commit style, review process |
| `SECURITY.md` (root) | How to report vulnerabilities |
| `CHANGELOG.md` | Keep a Changelog format |

## 11. Ethics and Responsible Use

- Publish a short **responsible use statement**: for analysis of organizations, infrastructure and events; not for targeting individuals.
- Provide a correction or takedown contact.
- Show uncertainty in the UI, not just in the docs.
- Keep an internal log of reviewed false positives and share lessons in the docs.
- If a future feature touches personal data, stop and run a privacy review first.

## 12. Licensing and Attribution

- Choose a license for the code (for example, MIT or Apache-2.0).
- Check each dataset's license; some (for example, sanctions datasets) have conditions for commercial use. **VERIFY** before any commercial plans.
- Show required attributions in the UI footer and README (map tiles, OpenStreetMap, data providers).
- Respect redistribution limits when committing recorded data.

## 13. Operational Good Practice

- One command to start everything: `make dev` or `docker compose up`.
- Seed script to create demo data and the golden replay.
- Pre-commit hooks: ruff, prettier, gitleaks.
- Weekly: dependency updates, source terms spot-check, backup restore test (monthly).
- Keep a short **incident log**; every incident leads to a test or a doc fix.

## 14. Release Process

1. Freeze scope; run the full CI pipeline.
2. Run the golden scenario manually.
3. Update the CHANGELOG and tag the release.
4. Deploy to demo/prod using the deployment procedure.
5. Smoke test; watch logs for 10 minutes.
6. Announce with the known limitations.

## 15. Anti-Patterns to Avoid

| Anti-pattern | Why |
|---|---|
| "Mega" scope before the core works | Unfinished demo |
| Using the LLM to decide what is suspicious | Unexplainable and untestable |
| Fake precision ("96% collusion risk") | Misleads; fails judge questions |
| Hotlinking free tile servers heavily | Violates terms; gets blocked |
| Depending on a single unverified source | One outage kills the project |
| Hiding limitations | Loses trust when discovered |
| Silent threshold changes | Unreproducible results |
| Committing recorded data without checking terms | Licensing risk |
