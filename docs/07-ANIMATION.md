# 07 — Animation and Motion

Motion in Lyncis should feel like a **precise instrument**: smooth, glowing, never decorative noise. It explains change (a signal appeared, two things linked) and gives the UI polish.

---

## 1. Principles

1. **Purposeful.** Every animation shows cause, change or hierarchy.
2. **Fast.** UI feedback 120–240 ms; entrances 300–600 ms; ambient loops are slow (4–10 s).
3. **Cheap.** Animate only `transform` and `opacity` (and `filter` sparingly). Never animate layout properties such as `width`, `height`, `top`, `left`.
4. **Respectful.** Honor `prefers-reduced-motion`.
5. **Consistent.** Use shared tokens, not ad-hoc values.
6. **Honest.** Never animate in a way that implies certainty (for example, no "locking onto target" effects for low-confidence events).

## 2. Tokens

```css
:root {
  /* durations */
  --dur-instant: 90ms;
  --dur-fast: 160ms;
  --dur-base: 240ms;
  --dur-slow: 420ms;
  --dur-hero: 700ms;
  --dur-ambient: 6000ms;

  /* easings */
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);      /* entrances */
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);   /* moves */
  --ease-in: cubic-bezier(0.64, 0, 0.78, 0);       /* exits */
  --ease-spring-ish: cubic-bezier(0.34, 1.56, 0.64, 1); /* small pops only */
}
```

Motion library config (`motion`):

```ts
export const spring = { type: "spring", stiffness: 380, damping: 32, mass: 0.8 };
export const springSoft = { type: "spring", stiffness: 220, damping: 28 };
export const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.42, ease: [0.22, 1, 0.36, 1] } },
};
export const stagger = { show: { transition: { staggerChildren: 0.06, delayChildren: 0.05 } } };
```

## 3. Landing Page Animations

| Element | Animation | Spec |
|---|---|---|
| **Hero headline** | Line-by-line reveal; green phrase fades in last | `fadeUp`, stagger 80 ms; green line adds a subtle glow bloom (opacity 0 → 1, 600 ms) |
| **Hero badge** | Fade + scale 0.95 → 1 | 240 ms |
| **CTA buttons** | Hover: lift 2 px + green glow; press: scale 0.97 | 160 ms, `--ease-out` |
| **Hero mockup** | Slow float: translateY ±8 px, rotateX/rotateY ±1.5° | 8 s ease-in-out infinite; parallax on pointer move (max 6 px) |
| **Orbiting color dots** | Scale pulse in sequence | 1.8 s loop, 120 ms offset each |
| **Background glow** | Radial gradient breathes (opacity 0.55 ↔ 0.8) | 6 s ease-in-out infinite |
| **Mountain / hero image** | Slow zoom 1 → 1.04 | 20 s linear alternate |
| **Scroll cue (mouse icon)** | Wheel dot moves down and fades; arrow bobs | 1.6 s loop |
| **Stats strip** | Numbers count up when in view | 1.2 s, ease-out, once |
| **Section headings** | Fade-up on enter | `whileInView`, once, margin −80 px |
| **How-it-works cards** | Stagger in; border glow on hover | 60 ms stagger; hover 160 ms |
| **Feature cards** | Hover: border color → green at 40% alpha, subtle inner glow | 200 ms |
| **Showcase tiles** | Hover: image scale 1.03, arrow button slides 4 px | 240 ms |
| **CTA input + button** | Focus ring pulses once | 400 ms |

## 4. Console Animations

### 4.1 Map

| Interaction | Animation | Spec |
|---|---|---|
| **Vessel position update** | Interpolate between old and new coordinates | Linear interpolation over the report interval (cap 3 s); update in one `requestAnimationFrame` batch |
| **New vessel appears** | Scale 0 → 1, opacity 0 → 1 | 240 ms `--ease-spring-ish` |
| **Vessel leaves** | Fade out | 300 ms |
| **AIS gap** | Last-known marker turns amber; **radar-style pulse ring** expands and fades | Ring radius 0 → 40 px, opacity 0.6 → 0, 1.8 s loop while the gap is open (stop after 3 loops once the user has seen it) |
| **Gap closes** | Dashed line draws from the last to the new position | `stroke-dashoffset` 600 ms |
| **Track trail** | Gradient fade of older segments | Static gradient, no per-frame cost |
| **Hotspot (FIRMS)** | Soft flicker glow | opacity 0.7 ↔ 1, 2.4 s, random phase |
| **Wind arrows** | Gentle rotate on data change | 400 ms |
| **Select event** | Map `flyTo` with easing; selected marker gets a ring | 700–900 ms, `--ease-in-out` |
| **Correlation link** | Animated dashed line between parent events | Dash offset flows 1.2 s linear loop; stops when not hovered or selected |

### 4.2 Feed

| Interaction | Animation |
|---|---|
| New event | Slides in from the top (`y: −12 → 0`, opacity 0 → 1, 240 ms); existing items shift using layout animation (`layout` prop, spring) |
| High-severity event | One 600 ms border glow flash, then static |
| Hover | Background lift + green left border grows 0 → 3 px |
| Filter change | Cross-fade list, 160 ms |

Cap simultaneous entrance animations at 5 per second; beyond that, insert without animation to keep 60 fps.

### 4.3 Detail Drawer
- Slides from the right: `x: 24 → 0`, opacity, spring-soft.
- Sections reveal with a 40 ms stagger.
- AI brief text: simple fade (no typewriter effect; it delays reading and implies "thinking").
- Evidence links: underline draws left to right on hover.

### 4.4 Graph View
- Nodes appear with a stagger (30 ms), scale 0.8 → 1.
- Edges draw via `stroke-dashoffset` (400 ms).
- Hover a node: connected edges brighten; others dim to 30% opacity (160 ms).

### 4.5 Replay Bar
- Play/pause icon morphs (path interpolation or cross-fade, 160 ms).
- Scrubber thumb: scale 1.2 on drag.
- **REPLAY badge** has a slow amber pulse so it is never mistaken for live.

### 4.6 Status and Feedback
| Element | Animation |
|---|---|
| LIVE badge | Green dot pulses (scale 1 → 1.6, opacity 0.6 → 0, 1.6 s loop) |
| Source health dot | Color transition 200 ms; amber/red do **not** pulse (avoid alarm fatigue) |
| Toasts | Slide + fade, 240 ms in, 160 ms out; auto-dismiss 5 s |
| Skeleton loading | Green-tinted shimmer, 1.4 s |
| Button loading | Spinner replaces the label; width stays fixed |

## 5. Page Transitions
- Landing → Console: fade to black 200 ms, console fades in 300 ms with the map first, panels staggered after.
- No full-screen wipes or long transitions.

## 6. Reduced Motion

```ts
const reduce = useReducedMotion();
// If reduce: no parallax, no float, no count-up (show final value),
// no pulsing rings (use a static ring), fades only at ≤ 120 ms,
// map flyTo becomes jumpTo.
```

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Replay and LIVE badges still need a non-motion distinction (text plus color).

## 7. Performance Rules

| Rule | Detail |
|---|---|
| Layers | Use `will-change: transform` only on elements that animate continuously, and remove it afterward |
| Glow | Prefer pre-rendered radial gradients over large animated `box-shadow` or `filter: blur()` |
| Map | Animate markers on the GPU layer (deck.gl) rather than DOM markers for large counts |
| Loops | Pause ambient loops when the tab is hidden (`document.visibilityState`) and when off-screen (`IntersectionObserver`) |
| Budget | No animation task over 8 ms per frame; check in the Performance panel |
| Low-power | If `navigator.hardwareConcurrency <= 4` or the frame rate drops below 40 fps for 3 s, disable ambient effects automatically |

## 8. Accessibility
- No flashing above 3 times per second.
- Motion never carries information alone: severity uses icon + label; gap uses an icon + text.
- Focus rings are always visible and never animated away.
- Auto-updating regions use `aria-live="polite"` and are rate-limited so screen readers are not flooded.

## 9. QA Checklist
- [ ] 60 fps on the console with 2,000 markers on a mid-range laptop.
- [ ] Reduced-motion mode verified.
- [ ] Hidden-tab pause verified.
- [ ] No layout shift (CLS < 0.05) from animations.
- [ ] Demo scenario animations are rehearsed and timed (gap pulse at about 0:40, correlation at about 1:10).
