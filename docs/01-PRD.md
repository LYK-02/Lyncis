# Lyncis — Product Requirements Document (PRD)

Version 1.0 · Status: Ready for build · Owner: Laik

---

## 1. Summary
Lyncis is an AI website builder. A user describes a business or idea in a sentence. Lyncis generates a complete, responsive, multi-section website (layout, copy, imagery), lets the user customize it visually, and publishes it live in one click. No code required.

Tagline: **Your idea. Our AI. Stunning websites.**

## 2. Problem
- Small businesses, freelancers, and students need a website but find template builders slow and design tools hard.
- Existing AI builders often produce generic pages, break on mobile, or lock editing behind code.
- Users want: fast first draft, easy edits, reliable hosting, and a free way to start.

## 3. Target users
| Persona | Need | Plan fit |
|---|---|---|
| Solo founder / freelancer | Portfolio or landing page in minutes | Free, Pro |
| Small business owner | Professional site with own domain | Pro |
| Student / creator | Free portfolio | Free |
| Agency / small team | Many client sites, shared access | Business |

## 4. Goals and non-goals
### Goals (v1)
- G1. Prompt to first visible preview in under 30 seconds (p50).
- G2. Prompt to published site in under 5 minutes for a new user.
- G3. Every generated site is responsive and passes basic accessibility checks.
- G4. Sustainable AI cost per generation (see §10).

### Non-goals (v1)
Full CMS, blog engine, e-commerce checkout, multi-language sites, custom code injection, real-time multi-user co-editing, template marketplace, native mobile app.

## 5. Plans and limits
Based on the pricing section of the approved design. Numeric quotas are **ASSUMPTIONS** to tune.

| | Free ($0) | Pro ($19/mo) | Business ($49/mo) |
|---|---|---|---|
| Websites | 1 | 10 | Unlimited (fair use, e.g. 200 cap) |
| AI generation | Yes, 5 full generations/day | 50/day | 200/day |
| Templates | Basic | Premium | Premium |
| Custom domain | No (lyncis subdomain) | Yes | Yes |
| "Made with Lyncis" badge | Yes | No | No |
| Team collaboration | No | No | Yes (members + roles) |
| Analytics | Basic views | Basic views | Advanced |
| Support | Community | Priority | Priority |
| Trial | n/a | Free trial (**ASSUMPTION:** 7 days) | Free trial (7 days) |

## 6. User stories
- As a visitor, I can understand what Lyncis does and try a prompt before signing up (prompt is saved and resumed after signup).
- As a new user, I can sign up with Google or email and land directly in a generation flow.
- As a user, I can describe my site and watch it build in real time.
- As a user, I can regenerate the whole site, one section, or just the copy.
- As a user, I can edit text inline, reorder or add sections, change colors and fonts, and preview mobile/tablet/desktop.
- As a user, I can publish to a Lyncis subdomain, later connect my own domain, and roll back to an older version.
- As a Pro/Business user, I can manage billing and see invoices.
- As a Business user, I can invite teammates with viewer/editor/admin roles.
- As an admin, I can review abuse reports and take a site down.

## 7. Functional requirements
Priority: **P0** = launch blocker, **P1** = launch target, **P2** = after launch.

### 7.1 Marketing site
| ID | Requirement | Pri |
|---|---|---|
| M-1 | Landing page with sections: hero, stats strip, how it works, AI generation, features, showcase, pricing, final CTA, footer (see `10-DESIGN.md`) | P0 |
| M-2 | Hero and final CTA prompt boxes start generation (guest → saved draft prompt → signup) | P0 |
| M-3 | Pricing page/section with plan comparison and monthly/annual toggle (annual **ASSUMPTION**, P1) | P0 |
| M-4 | Showcase gallery of real sites made with Lyncis (static list at launch, curated) | P1 |
| M-5 | Legal pages: Terms, Privacy, Acceptable Use, Cookie notice | P0 |
| M-6 | Newsletter signup with double opt-in | P1 |
| M-7 | SEO: metadata, OG images, sitemap, robots, structured data | P0 |

### 7.2 Accounts
| ID | Requirement | Pri |
|---|---|---|
| A-1 | Sign up / sign in: email + password, Google OAuth, magic link | P0 |
| A-2 | Email verification and password reset | P0 |
| A-3 | Profile and workspace created automatically | P0 |
| A-4 | Account deletion and data export | P1 |
| A-5 | Team invites, roles (owner, admin, editor, viewer) | P1 (Business) |

### 7.3 AI generation
| ID | Requirement | Pri |
|---|---|---|
| G-1 | Prompt input with optional fields: business name, tone, audience, color mood | P0 |
| G-2 | Streamed progress: plan → sections appear one by one → theme → images | P0 |
| G-3 | Output is a validated structured site (Site DSL), never raw HTML/JS | P0 |
| G-4 | Regenerate: whole site, single section, or copy only | P0 |
| G-5 | AI copy tools on selected text: shorten, expand, change tone, fix grammar | P1 |
| G-6 | Image selection with alt text; replace or upload | P0 |
| G-7 | Generation history; any generation can be restored | P1 |
| G-8 | Quota enforcement per plan, with clear "limit reached" state | P0 |
| G-9 | Content moderation on prompt and output | P0 |
| G-10 | Graceful failure: partial result is kept; clear retry | P0 |

### 7.4 Editor
| ID | Requirement | Pri |
|---|---|---|
| E-1 | Section list with drag reorder, duplicate, delete, hide | P0 |
| E-2 | Inline text editing on canvas | P0 |
| E-3 | Block library (hero, features, steps, stats, showcase, pricing, testimonials, FAQ, contact, CTA, footer) | P0 |
| E-4 | Theme panel: palette, fonts (curated list), radius, spacing density | P0 |
| E-5 | Device preview: desktop, tablet, mobile | P0 |
| E-6 | Undo/redo, autosave, unsaved-state indicator | P0 |
| E-7 | Image panel: upload, stock search, crop, alt text | P0 |
| E-8 | SEO panel: title, description, OG image, favicon | P1 |
| E-9 | Multi-page sites (up to 10 pages) | P1 |
| E-10 | Keyboard accessibility for all editor controls | P0 |

### 7.5 Publishing and domains
| ID | Requirement | Pri |
|---|---|---|
| P-1 | One-click publish to `{slug}` subdomain with success state and live URL | P0 |
| P-2 | Unpublish and republish; version history and rollback | P0 |
| P-3 | Custom domain connection with DNS instructions, verification, auto-SSL | P1 (Pro+) |
| P-4 | Free plan shows a "Made with Lyncis" badge | P0 |
| P-5 | Published sites are fast: Lighthouse performance ≥ 90 on mobile for template output | P0 |
| P-6 | Contact form on published sites with spam protection (**ASSUMPTION:** emails owner) | P1 |

### 7.6 Billing
| ID | Requirement | Pri |
|---|---|---|
| B-1 | Checkout for Pro and Business, trial support | P0 |
| B-2 | Customer portal: change plan, update card, cancel, invoices | P0 |
| B-3 | Webhook-driven entitlement updates, idempotent | P0 |
| B-4 | Failed payment handling with grace period and email | P1 |
| B-5 | Downgrade rules: excess sites become read-only, not deleted | P0 |

### 7.7 Analytics and admin
| ID | Requirement | Pri |
|---|---|---|
| D-1 | Privacy-friendly page-view counts per site (no cookies) | P1 |
| D-2 | Advanced analytics (referrers, countries, devices) for Business | P2 |
| X-1 | Internal admin: user/site lookup, abuse queue, takedown, usage view | P0 |
| X-2 | Abuse report link on every published site | P0 |

## 8. Non-functional requirements
| Area | Target |
|---|---|
| Performance (app) | LCP < 2.5s, INP < 200ms, CLS < 0.1 on landing and dashboard |
| Performance (published sites) | Mobile Lighthouse ≥ 90, TTFB < 400ms from CDN |
| Availability | 99.9% monthly for published sites; 99.5% for the editor |
| Accessibility | WCAG 2.2 AA for the marketing site, app, and generated output |
| Browsers | Last 2 versions of Chrome, Edge, Safari, Firefox; iOS Safari 16+ |
| Security | See `05-SECURITY.md` |
| Privacy | Compliant with India DPDP Act and GDPR basics (consent, deletion, export) |
| Scalability | 10k users, 50k published sites without architecture change |

## 9. Success metrics
| Metric | Target at 90 days (**ASSUMPTION**) |
|---|---|
| Visitor → signup | ≥ 6% |
| Signup → first generation | ≥ 70% |
| Generation → publish | ≥ 35% |
| Valid-output rate (passes schema first try) | ≥ 97% |
| Median time to first preview | < 30s |
| Free → paid | ≥ 3% |
| 30-day retention (publishers) | ≥ 25% |
| AI cost per free user per month | < $0.20 |

## 10. AI cost guardrails
- Per-plan daily quotas (see §5), plus a global daily budget with alert at 70% and hard stop at 100%.
- Cheap model for planning, stronger model for copy; cache identical prompts for 24h.
- Max input 800 characters; max output tokens capped per stage.

## 11. Content and claims
Marketing numbers in the design ("10x faster", "100% responsive") must be backed by a measured comparison, or reworded (for example "Responsive on every device") before launch.

## 12. Risks
| Risk | Impact | Mitigation |
|---|---|---|
| Generic-looking output | Low retention | Curated design system and block library; theme constraints |
| LLM cost spikes | Margin loss | Quotas, caching, budget kill switch |
| Abuse (phishing, spam sites) | Legal/reputation | Moderation, abuse queue, takedown SLA, no custom HTML in v1 |
| Provider outage | Generation down | Multi-provider fallback, partial results |
| Custom domain complexity | Support load | Guided DNS checker, clear error states |
| Scope creep | Late launch | Phase gates in `03-PHASES.md` |

## 13. MVP acceptance criteria
1. A new user can sign up, generate, edit, and publish a working site without help.
2. Published site loads over HTTPS on a Lyncis subdomain and is responsive at 360px, 768px, 1280px.
3. Free quotas and plan limits are enforced server-side.
4. Payments upgrade and downgrade entitlements correctly via webhooks.
5. Security checklist in `05-SECURITY.md` passes; no P0/P1 bugs open.
