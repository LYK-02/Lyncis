# 10 — Design System

Derived from the uploaded theme (dark "AI website builder" landing page): near-black canvas, neon-lime accents, glass cards with soft green glow, white pill buttons, bold sans-serif headlines with a highlighted green phrase, and 3D-tilted product mockups.

> Color values are **approximated from a screenshot**. Sample the exact pixels in Figma or the browser and adjust the tokens once.

---

## 1. Design Principles

1. **Dark first.** Analysts work long sessions; the dark theme reduces glare and makes the map glow.
2. **Signal over decoration.** Neon green marks live and active things. If everything glows, nothing does.
3. **Honest hierarchy.** Confidence and severity are always readable, never only colored.
4. **Calm density.** Console panels are information-dense but have consistent spacing.
5. **Theme continuity.** Landing and console share tokens, so the product feels like one thing.

## 2. Brand

- **Name:** Lyncis
- **Tagline:** See the signals. Link the story.
- **Voice:** Clear, confident, precise, never alarmist. Short sentences. Use "possible" and "observed".
- **Logo direction:** A minimal mark combining a link (two connected nodes) with a lynx-eye or radar ring. White line mark on dark with a small green dot as the accent. The reference uses an outlined hexagon/atom-style mark; use a similar outline weight (2 px at 32 px size).

## 3. Color Tokens

### 3.1 Core Palette

```css
:root {
  /* Surfaces */
  --bg-0: #050505;          /* page background (near black) */
  --bg-1: #0b0b0b;          /* alt sections */
  --bg-2: #121212;          /* raised sections (like "One prompt" band) */
  --surface-1: #0f0f0f;     /* cards */
  --surface-2: #161616;     /* inputs, nested panels */
  --surface-glass: rgba(255,255,255,0.03);

  /* Borders */
  --border-subtle: rgba(255,255,255,0.08);
  --border-strong: rgba(255,255,255,0.16);
  --border-accent: rgba(140,255,46,0.35);

  /* Text */
  --text-0: #ffffff;        /* headings */
  --text-1: #d4d4d4;        /* body */
  --text-2: #8f8f8f;        /* secondary */
  --text-3: #5c5c5c;        /* disabled / hints */

  /* Brand green (lime) */
  --lime-300: #b6ff6a;
  --lime-400: #8cff2e;      /* primary accent / highlight text */
  --lime-500: #6fe01c;
  --lime-600: #4c9a14;
  --lime-700: #356b10;      /* dark green buttons (like "Get Started" in pricing) */
  --lime-900: #12260a;      /* tinted backgrounds */

  /* Glow */
  --glow-lime: 0 0 24px rgba(140,255,46,0.25);
  --glow-lime-strong: 0 0 48px rgba(140,255,46,0.35);
}
```

### 3.2 Semantic Colors (console)

Brand green already means "live / active", so severity uses distinct hues.

| Meaning | Token | Hex | Use |
|---|---|---|---|
| Live / OK | `--status-ok` | `#8cff2e` | LIVE badge, source OK |
| Info | `--sev-info` | `#6ea8ff` | Informational events |
| Low | `--sev-low` | `#d9e35a` | Low severity |
| Medium | `--sev-medium` | `#ffb020` | Medium severity, AIS gaps |
| High | `--sev-high` | `#ff4d4f` | High severity |
| Replay | `--status-replay` | `#ffb020` | REPLAY badge (amber) |
| Sample data | `--status-sample` | `#b48cff` | SAMPLE badge |
| Down | `--status-down` | `#ff4d4f` | Source down |

Severity chips always pair color with an icon and a text label.

### 3.3 Gradients

```css
--grad-hero-glow: radial-gradient(60% 50% at 70% 30%, rgba(40,120,255,0.35) 0%, rgba(5,5,5,0) 70%),
                  radial-gradient(50% 40% at 60% 60%, rgba(140,255,46,0.22) 0%, rgba(5,5,5,0) 70%);
--grad-card-edge: linear-gradient(180deg, rgba(140,255,46,0.18), rgba(255,255,255,0.02));
--grad-text-lime: linear-gradient(90deg, #8cff2e, #b6ff6a);
```

The reference hero has a subtle **blue glow in the upper right** behind the mockup and a **lime glow** beneath. Keep the blue very low in saturation so green stays the brand.

### 3.4 Contrast Checks
- `--text-0` on `--bg-0`: very high. ✔
- `--lime-400` on `--bg-0`: high. ✔ (large and body text)
- `--text-2` on `--surface-1`: verify ≥ 4.5:1; if not, lighten to `#9a9a9a`.
- Text on `--lime-400` buttons: use `#050505` (black).

## 4. Typography

| Role | Font | Notes |
|---|---|---|
| Display / headings | **Inter** (or Geist / Plus Jakarta Sans) | Weight 700–800, tight tracking (−0.02em) |
| Body | Inter | 400–500 |
| Data / code / IDs | **JetBrains Mono** (or Geist Mono) | MMSI, IMO, coordinates, timestamps, rule IDs |

The reference uses a clean geometric sans with heavy headlines. Load via `next/font` with `display: swap`.

### Type Scale (desktop / mobile)

| Token | Desktop | Mobile | Weight | Use |
|---|---|---|---|---|
| `display` | 64 / 68 | 40 / 44 | 800 | Hero headline |
| `h1` | 48 / 52 | 32 / 38 | 800 | Section headline |
| `h2` | 32 / 38 | 24 / 30 | 700 | Card group titles |
| `h3` | 20 / 28 | 18 / 26 | 600 | Card titles |
| `body-lg` | 18 / 28 | 16 / 26 | 400 | Hero subtext |
| `body` | 15 / 24 | 15 / 24 | 400 | Default |
| `small` | 13 / 20 | 13 / 20 | 500 | Labels, meta |
| `micro` | 11 / 16 | 11 / 16 | 600 | Badges (uppercase, +0.06em) |
| `mono` | 13 / 20 | 13 / 20 | 500 | Data |

### Signature Headline Pattern
White heading with the **key phrase in lime**, as in the reference:

> Your idea. **Our AI.** → Lyncis equivalent:
> **Every signal.** (white)
> **One story.** (lime)

```html
<h1>Every signal.<br/><span class="text-lime">One story.</span></h1>
```

## 5. Spacing, Radius, Elevation

```css
--space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
--space-5: 24px; --space-6: 32px; --space-7: 48px; --space-8: 64px; --space-9: 96px;

--radius-sm: 8px;   /* inputs, small chips */
--radius-md: 12px;  /* buttons in console */
--radius-lg: 20px;  /* cards (reference uses large rounded cards) */
--radius-xl: 28px;  /* hero panels, stats strip */
--radius-pill: 999px; /* buttons, badges (reference style) */
```

- Section vertical rhythm: 96 px desktop, 64 px mobile.
- Max content width: 1200 px; landing text blocks 640–720 px.
- Console uses an 8 px grid, with panel padding of 16 px.

### Elevation (glow-based, since the surface is dark)

| Level | Style |
|---|---|
| 0 | Flat, `--border-subtle` |
| 1 | `--surface-1` + subtle top-edge highlight |
| 2 | Level 1 + `box-shadow: 0 8px 32px rgba(0,0,0,0.6)` |
| Glow | Level 2 + `--glow-lime` (hover or selected only) |

## 6. Components

### 6.1 Buttons (pill shape, as in the reference)

| Variant | Style | Use |
|---|---|---|
| **Primary (white)** | bg `#fff`, text `#050505`, pill, 40–44 px height; hover: lift 2 px + soft white glow | Main CTAs ("Launch Console") |
| **Secondary (outline)** | transparent, 1 px `--border-strong`, white text; hover: border → lime | "Watch Demo" |
| **Accent (lime-dark)** | bg `--lime-700`, text white; hover: `--lime-600` | In-card CTAs (like pricing "Get Started") |
| **Accent (lime)** | bg `--lime-400`, text `#050505`; hover: `--lime-300` + glow | Generate / Run actions |
| **Icon button (circle)** | 36 px circle, `--lime-400` bg, black arrow (like the circular arrow in cards) | Navigation or "open" |
| **Ghost** | text only; hover underline | Tertiary |

States: hover, active (scale 0.97), focus (2 px lime ring, 2 px offset), disabled (40% opacity), loading (spinner, fixed width).

### 6.2 Badges / Pills
- Section label: lime filled pill with black micro text (like "AI-POWERED WEBSITE BUILDER", "HOW IT WORKS", "FEATURES").
- Status badges: LIVE (green dot + text), REPLAY (amber), SAMPLE (violet), always with text.
- Confidence chip: `LOW | MEDIUM | HIGH` with a 3-segment bar icon.

### 6.3 Cards
- Background `--surface-1`, border `--border-subtle`, radius `--radius-lg`, padding 24 px.
- Soft green edge glow at the bottom or edge (reference cards have a faint green bloom): add `::after` radial gradient `rgba(140,255,46,0.08)`.
- Hover: border → `--border-accent`, translateY −2 px.
- Feature cards: title (h3), 2-line description, optional mini-visual.

### 6.4 Stats Strip
- A single wide rounded container (`--radius-xl`) with 4 equal cells separated by 1 px dividers; large number (white, 40 px) + small caption (`--text-2`).
- Use only true statements (for example, "6 data sources", "100% cited events").

### 6.5 Inputs
- `--surface-2` background, 1 px border, radius 12 px, 44 px height.
- Focus: lime border + `--glow-lime`.
- The CTA band uses an input + lime button side by side (as in the reference "Describe the website…" row); for Lyncis: "Search a vessel, IMO or region…".

### 6.6 Navigation
- Transparent top bar with logo at left, links centered/left, outlined pill at right (like "Sign In").
- On scroll: background `rgba(5,5,5,0.7)` with `backdrop-filter: blur(12px)` and a bottom border.

### 6.7 Mockup Frames
- 3D-tilted glass panels with `transform: perspective(1200px) rotateY(-12deg) rotateX(6deg)`.
- Floating label chips around the mockup (like "Designing layout", "Writing content", "Optimizing images") → Lyncis: **"Ingesting AIS"**, **"Linking events"**, **"Writing brief"**.
- A vertical tool rail at the left of the mockup and a row of color dots under it (the reference uses green/teal/white dots; use them as **layer toggles** in the real console).

### 6.8 Footer
- Logo + one-line description, three columns (Product, Company, Newsletter/Docs), copyright and responsible-use link.

## 7. Console-Specific Design

### 7.1 Layout Tokens
- Top bar: 48 px. Left filter rail: 280 px. Right feed: 360 px. Replay bar: 56 px.
- Panels use `--surface-1` with `backdrop-filter: blur(16px)` over the map so the map stays visible and the theme feels glassy.

### 7.2 Map Style
- Dark base style (near-black land, slightly lighter water, low-contrast labels).
- Vessel marker: small chevron, rotated by course; color by status (normal lime-tinted white, gap amber, sanctions match ring in red).
- Tracks: 1.5 px line with a fade gradient.
- Gap marker: amber ring with an animated pulse (see ANIMATION.md).
- Hotspot: orange-red radial gradient.
- Keep labels legible: text `--text-1` with a dark halo.

### 7.3 Event Feed Item

```
┌──────────────────────────────────────────┐
│ ▲ MEDIUM   ·  LOW CONFIDENCE    10:15 UTC │
│ Possible AIS gap · EXAMPLE STAR           │
│ 133 min · last speed 12 kn · near …       │
│ [ghostwake]  [R1]                         │
└──────────────────────────────────────────┘
```

- Left border 3 px in the severity color.
- Module tag in a small outline pill; rule ID in mono.

### 7.4 Detail Drawer
- Width 420 px, `--surface-1`, top-aligned sections separated by 1 px dividers.
- AI brief block has a subtle lime left border and an "AI-written summary" micro label.
- Caveats block uses an amber info icon and `--text-1` text.

### 7.5 Graph
- Nodes: circles with a 1 px border; fill by type (vessel white, organization lime-tinted, domain blue-tinted, region gray, hotspot orange).
- Edge labels in mono micro text.

## 8. Iconography
- Lucide icons, 1.5 px stroke, 20 px default; the reference uses thin outline icons in lime for feature headers.
- Icons carry meaning together with text, never alone.

## 9. Imagery
- The reference uses a **dark mountain with a neon green ridge** as hero art. Lyncis equivalent: a **dark ocean/coastline contour map with a neon green route line and glowing nodes**, generated as SVG or rendered from the real map for authenticity. Avoid stock photos.
- No fake logos, fake testimonials or fake customer counts.

## 10. Responsive Behavior

| Breakpoint | Behavior |
|---|---|
| ≥ 1280 | Full three-column console |
| 1024–1279 | Feed becomes a collapsible panel |
| 768–1023 | Filters in a drawer; the feed overlays the map |
| < 768 | Map full screen; bottom-sheet feed; stats strip becomes a 2×2 grid; hero mockup stacks below the text |

## 11. Tailwind Mapping (excerpt)

```ts
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        bg: { 0: "#050505", 1: "#0b0b0b", 2: "#121212" },
        surface: { 1: "#0f0f0f", 2: "#161616" },
        lime: { 300: "#b6ff6a", 400: "#8cff2e", 500: "#6fe01c", 600: "#4c9a14", 700: "#356b10", 900: "#12260a" },
        sev: { info: "#6ea8ff", low: "#d9e35a", medium: "#ffb020", high: "#ff4d4f" },
      },
      borderRadius: { lg: "20px", xl: "28px" },
      boxShadow: {
        glow: "0 0 24px rgba(140,255,46,0.25)",
        "glow-strong": "0 0 48px rgba(140,255,46,0.35)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
    },
  },
};
```

## 12. Landing Page Content Map (from the reference layout)

| Reference section | Lyncis version |
|---|---|
| Badge "AI-POWERED WEBSITE BUILDER" | `OPEN-SOURCE INTELLIGENCE` |
| "Your idea. Our AI. **Stunning websites.**" | "Every signal. **One story.**" |
| Subtext | "Lyncis links ships, thermal hotspots, sanctions data and news on one live map, with a source for every claim." |
| CTAs: Get Started Free / Watch Demo | Launch Console / Watch Demo |
| Stats: 10x / AI / 100% / No Code | **6 sources / Cited / Replay-ready / $0** (only if true at launch) |
| HOW IT WORKS: Describe / Customize / Publish | **Ingest / Link / Explain** |
| AI GENERATION band (carousel mockups) | "One map. **Many signals.**" console carousel |
| FEATURES grid (6 cards) | Live map, Gap detection, Sanctions matching, Correlation, AI briefs, Replay mode |
| SHOWCASE (4 tiles) | Scenarios: Maritime, Thermal, Domain exposure, News |
| PRICING | "Free and open" single card, or remove |
| READY TO START? input + Generate | "Search a vessel, IMO or region…" + Open |
| Footer | Product, Docs, Responsible use, Contact |

## 13. Design QA Checklist
- [ ] Tokens defined once and used everywhere (no stray hex values).
- [ ] Contrast checked for all text on all surfaces.
- [ ] Severity and confidence readable without color.
- [ ] Hover, focus, active, disabled and loading states for every interactive component.
- [ ] Empty, loading and error states designed.
- [ ] Responsive screenshots reviewed at 375, 768, 1280 and 1920 px.
- [ ] REPLAY and SAMPLE badges visible whenever they apply.
- [ ] No fake numbers, logos or testimonials.
