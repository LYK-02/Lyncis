# 06 — App Flow

How users move through Lyncis, and how data moves through the system.

---

## 1. Site Map

```
/                      Landing (marketing)
/console               Main console (map + feed + graph)
/console/events/:id    Event detail (deep link, opens drawer)
/console/sources       Source health
/console/replay        Replay session picker
/about                 Method, limits, ethics
/docs                  README, data sources, limitations
```

## 2. Primary User Flows

### 2.1 First-time visitor → demo

```mermaid
flowchart TD
  A[Landing page] --> B{CTA}
  B -->|Launch Console| C[Console in LIVE or REPLAY]
  B -->|Watch Demo| D[Console auto-starts golden replay]
  C --> E[See map, feed, source health]
  D --> E
  E --> F[Click event in feed or on map]
  F --> G[Detail drawer: summary, confidence, reasoning, evidence]
  G --> H{Next action}
  H -->|Open source link| I[External evidence in new tab]
  H -->|View graph| J[Entity graph]
  H -->|Copy brief| K[Clipboard]
```

### 2.2 Analyst investigation

```mermaid
flowchart LR
  A[Open console] --> B[Set area / time filter]
  B --> C[Filter by module, severity, confidence]
  C --> D[Select correlated event]
  D --> E[Inspect parent events]
  E --> F[Check sanctions match: source link]
  F --> G[Read AI brief + reasoning]
  G --> H[Export cited report]
```

### 2.3 Replay demo (golden scenario)

1. Presenter opens `/console` and selects "Golden scenario" (REPLAY badge visible).
2. Vessels move on the map at 5× speed.
3. A vessel's track stops → **gap pulse** appears and the feed adds an `ais_gap` event (low confidence, "possible").
4. SanctionWeb exact-matches the vessel's identifier → a **sanctions badge** appears.
5. Rule R3 fires → **correlated event** (medium) slides into the feed.
6. Presenter opens the drawer → brief generated, evidence links shown.
7. Presenter opens the graph → vessel, organization and region nodes linked.
8. Close with the limitations panel ("what this does not prove").

## 3. Screen Specifications

### 3.1 Landing (`/`)
Sections (matching the supplied theme):
1. Nav: logo, Features, Showcase, Pricing → *replace with* Features, How it works, Console, About; "Sign In" outline pill → *replace with* "Launch Console".
2. Hero: badge, headline with green highlight, subtext, two CTAs, 3D-tilted console mockup with orbiting color dots, scroll-down cue.
3. Stats strip: four cells (for example: *Live sources · Cited events · Replay-ready · $0 to run*). Use only true numbers.
4. How it works: three cards (**Ingest → Link → Explain**).
5. Feature spotlight: "One map. Many signals." with mockup carousel.
6. Features grid: 6 cards (Live map, Gap detection, Sanctions matching, Correlation, AI briefs, Replay mode).
7. Showcase: scenario thumbnails (Maritime, Thermal, Domain exposure, News).
8. Limits and ethics section (honesty builds trust).
9. CTA band: "Open the console".
10. Footer: Product, Company, Docs, Newsletter *(optional, remove if unused)*.

> The reference theme includes a pricing section. Lyncis is free, so use a "Free and open" card or remove the section. Do not show fake paid plans.

### 3.2 Console (`/console`)

```
┌─────────────────────────────────────────────────────────────────┐
│ Top bar: logo · mode badge (LIVE/REPLAY) · time · source health │
├───────────┬─────────────────────────────────────┬───────────────┤
│ Filters   │                                     │ Event feed    │
│ - Module  │            MAP                      │ (virtualized) │
│ - Sever.  │   vessels · tracks · gaps · layers  │               │
│ - Conf.   │                                     │               │
│ - Time    │                                     │               │
├───────────┴─────────────────────────────────────┴───────────────┤
│ Replay bar: ⏮ ⏯ speed 1×/5×/20× · timeline scrubber            │
└─────────────────────────────────────────────────────────────────┘
        Detail drawer slides over the right panel on select
```

**Mobile:** map full screen; feed as bottom sheet; filters in a modal.

### 3.3 Event Detail Drawer
- Header: type, severity icon + label, confidence label, timestamp.
- Summary line (hedged language).
- AI brief (labeled "AI-written summary") or template brief.
- Reasoning list and caveats.
- Evidence list (links).
- Parent events (click to navigate).
- "Raw data" collapsible.
- Actions: Copy brief, Focus on map, View in graph.

### 3.4 Graph View
- Nodes: vessel, organization, domain, region, hotspot, news cluster.
- Edges labeled with rule ID or relation type.
- Click node → highlight related events in the feed.

### 3.5 Source Health
- Row per source: status (OK / Degraded / Down), last success, error count, mode (live/replay).

## 4. Data Flow

```mermaid
sequenceDiagram
  participant S as Source (AISStream etc.)
  participant A as Adapter
  participant B as Event Bus
  participant D as Detector
  participant C as Correlation
  participant DB as SQLite
  participant W as WS Hub
  participant U as UI

  S->>A: raw message
  A->>B: normalized observation
  B->>D: observation
  D->>B: event (e.g., ais_gap)
  B->>C: event
  C->>B: correlated event (with parents)
  B->>DB: persist
  B->>W: broadcast
  W->>U: WS message (mode: live|replay)
  U->>U: update store, animate marker/feed
  U->>W: (on select) GET /events/{id}
  W-->>U: event + parents + brief
```

## 5. Connection State Machine (frontend)

```mermaid
stateDiagram-v2
  [*] --> Connecting
  Connecting --> Live: ws open + hello
  Connecting --> Retry: error
  Live --> Retry: close / heartbeat timeout
  Retry --> Connecting: backoff (1s→30s, jitter)
  Retry --> Offline: 5 failures
  Offline --> Connecting: user clicks Reconnect
  Live --> Replay: user starts replay
  Replay --> Live: user exits replay
```

On `Live` after a retry: fetch `GET /events?from=<last_ts>` to fill the gap before applying new messages.

## 6. Event Lifecycle

```mermaid
stateDiagram-v2
  [*] --> Observed
  Observed --> Open: gap detected
  Open --> Closed: vessel reappears
  Open --> Expired: retention window passed
  Open --> Correlated: rule matches
  Correlated --> Closed
  Closed --> [*]
  Expired --> [*]
```

A gap event stays **Open** until the vessel reports again; a follow-up event states the new position and the elapsed gap.

## 7. Empty, Loading and Error States

| State | UI behavior |
|---|---|
| Loading map | Skeleton glass card with a green shimmer |
| No events | "No events in this window. Try REPLAY." |
| Source down | Amber badge in the top bar; feed continues from other sources |
| WS offline | Banner with "Reconnect"; the map shows the last known state, marked stale |
| Brief failed | Template brief with a small "template" tag |
| API error | Toast with `request_id`, retry button |

## 8. Keyboard Shortcuts

| Key | Action |
|---|---|
| `J` / `K` | Next / previous event in feed |
| `Enter` | Open selected event |
| `Esc` | Close drawer |
| `Space` | Play / pause replay |
| `G` | Toggle graph |
| `/` | Focus search |

## 9. Analytics (privacy-respecting, optional)

Only aggregate, cookie-less events (page views, replay started). No tracking of individuals.
