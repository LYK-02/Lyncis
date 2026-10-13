# 04 — Rules

These rules are binding for product, data, AI and engineering decisions. Break one only through a written exception in the ADR log.

---

## 1. Product Rules

| # | Rule |
|---|---|
| P1 | Lyncis analyzes **organizations, vessels, infrastructure and events**. It never profiles, tracks or locates private individuals. |
| P2 | Every event shows **confidence** (low / medium / high), **reasoning** and **at least one evidence reference**. |
| P3 | No event is ever presented as proof of wrongdoing. The UI says what was observed, not what it means. |
| P4 | Replay mode is always labeled with a visible **REPLAY** badge. Never present recorded data as live. |
| P5 | Sample or synthetic data is always labeled **SAMPLE**. Never invent data and present it as real. |
| P6 | Features that depend on unverified sources ship behind feature flags. |
| P7 | The pitch and README state known limitations (AIS coverage gaps, source delays). |

## 2. Language Rules

**Use:** "possible", "AIS gap", "match candidate", "co-located", "needs review", "observed", "reported".

**Do not use:** "dark fleet", "smuggling", "illegal", "guilty", "criminal", "confirmed violation", "evading sanctions". The brief validator rejects these terms.

| Instead of | Write |
|---|---|
| "Vessel went dark to evade sanctions" | "Possible AIS gap of 133 min; reason unknown." |
| "Sanctioned ship detected" | "Vessel identifier matches a sanctions-list record. Review the source." |
| "Illegal transfer" | "Possible ship-to-ship proximity for 42 min." |

## 3. Data Rules

| # | Rule |
|---|---|
| D1 | Only use sources whose terms permit the intended use. Record the source, license and terms link in `docs/data-sources.md`. |
| D2 | No scraping that violates terms of service. No captcha bypass. No credential sharing. |
| D3 | No scraping-vendor pages as proof that a source is free or open. Use primary documentation. |
| D4 | Respect rate limits. Cache. Back off. Identify the client with a User-Agent where the source expects one. |
| D5 | Store only what is needed. Apply the retention defaults in the TRD. |
| D6 | No personal data ingestion in the MVP. If a source includes personal names (for example, sanctions lists), exclude person entities from automated matching and display. |
| D7 | Never commit API keys, personal data or raw data whose license forbids redistribution. |
| D8 | Every record keeps provenance: source, retrieval time and original identifier. |
| D9 | ShadowTrace scans only domains the user owns or can prove control over (DNS TXT challenge), or an explicit demo allowlist. |
| D10 | Do not fabricate figures. Market sizes and statistics on slides need a cited source or are removed. |

## 4. AI Rules

| # | Rule |
|---|---|
| A1 | The LLM writes wording. It never decides detection, severity or confidence. |
| A2 | Input to the LLM is structured event fields only, not raw web text. |
| A3 | Treat all external text (ship names, news headlines, domain names) as untrusted. Pass as quoted data fields; never as instructions. |
| A4 | Output must pass schema validation, a length limit (≤ 3 sentences) and the banned-term filter. |
| A5 | On failure or timeout, use the template brief and mark `is_fallback`. |
| A6 | Log provider, latency and fallback rate. Never log secrets. |
| A7 | Briefs cite evidence IDs; if there is no evidence, no brief is generated. |
| A8 | Show an "AI-written summary" label next to every generated brief. |

## 5. Engineering Rules

### 5.1 General
- TypeScript `strict: true`. Python typed and checked with mypy.
- No `any` without a comment. No bare `except`.
- One source of truth for the event schema; generate the other language's types.
- Pure functions for detectors and rules so they are easy to test.
- No secrets in code, logs, client bundles or Git history.

### 5.2 Git
- Trunk-based with short-lived branches: `feat/…`, `fix/…`, `chore/…`.
- Conventional Commits: `feat(ghostwake): add speed-aware gap threshold`.
- PRs require passing CI. Squash merge.
- Keep PRs under about 400 changed lines where possible.

### 5.3 Code Quality
- Ruff, mypy, ESLint and Prettier run in pre-commit and CI.
- Detectors and rules need unit tests before merge.
- Public functions have docstrings; non-obvious thresholds have a comment explaining why.

### 5.4 Error Handling
- Adapters never crash the process. They retry and report.
- API errors use the standard error format with a `request_id`.
- UI shows a degraded state, never a blank screen.

### 5.5 Performance
- No unbounded lists in memory; cap queues and use backpressure.
- Batch UI updates per animation frame.
- Lazy-load heavy map and graph libraries.

### 5.6 Accessibility
- Color is never the only signal; severity also uses an icon and a text label.
- Keyboard navigation for the feed and drawer.
- Respect `prefers-reduced-motion`.

## 6. Definition of Done

A change is done when:
- [ ] Code is reviewed and CI is green.
- [ ] Tests cover the new behavior (including a failure case).
- [ ] No new lint, type or accessibility warnings.
- [ ] Docs and env-var tables are updated.
- [ ] Language rules and evidence rules are respected.
- [ ] Works in replay mode.

## 7. Exceptions

Write an ADR with: context, decision, risk accepted, owner, and review date.
