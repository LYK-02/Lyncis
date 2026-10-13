# Lyncis — Technical Requirements Document (TRD)

Version 1.0 · Companion to `01-PRD.md`

---

## 1. Core architectural decision
**AI never writes raw HTML or JavaScript.** It produces a validated JSON document (the **Site DSL**). A fixed library of first-party React blocks renders that document. This gives us:
- Safety: no arbitrary script injection in published sites.
- Editability: the editor patches JSON, not markup.
- Consistency: design quality is controlled by blocks and tokens.
- Cheap re-generation of single sections.

## 2. Stack
| Layer | Choice | Notes |
|---|---|---|
| Framework | Next.js (App Router), React, TypeScript strict | Server Components by default |
| Styling | Tailwind CSS + CSS variables (tokens in `10-DESIGN.md`) | |
| UI primitives | shadcn/ui (Radix) | Accessible by default |
| Animation | Motion (`motion/react`) + CSS | See `07-ANIMATION.md` |
| State (editor) | Zustand + Immer patches | Undo/redo via patch history |
| Forms/validation | React Hook Form + Zod | Same schemas client and server |
| Database | Postgres (Supabase) with Row Level Security | |
| Auth | Supabase Auth (email, Google, magic link) | |
| Storage | Supabase Storage or Cloudflare R2 for user assets | **VERIFY** limits |
| Jobs / queues | Inngest or Trigger.dev (or Supabase Queues) | Long AI and image jobs |
| Cache / rate limit | Upstash Redis | |
| AI | Provider abstraction (Gemini, Groq, Anthropic, OpenAI-compatible) | Structured JSON output |
| Images | Stock API (Unsplash/Pexels) + optional AI image gen; `sharp` for processing | Check each API's license/attribution terms |
| Payments | Stripe or Razorpay (open decision) | Webhook-driven |
| Email | Resend or Postmark | |
| Observability | Sentry, PostHog (product), structured logs, uptime monitor | |
| Hosting | Vercel (app + published sites), Cloudflare (DNS/WAF) | Vercel Hobby is non-commercial; production needs a paid plan. **VERIFY** |
| CI/CD | GitHub Actions | |
| Package manager | pnpm + Turborepo | |

## 3. System architecture
```
                       ┌──────────────────────────┐
 Visitor / User ─────▶ │ Cloudflare (DNS, WAF)     │
                       └─────────────┬────────────┘
                                     │
                 ┌───────────────────▼───────────────────┐
                 │ Next.js on Vercel                      │
                 │  • apps/web  (marketing + app)         │
                 │  • tenant renderer ({site}.lyncis.site)│
                 │  • route handlers / server actions     │
                 └───┬─────────────┬───────────────┬──────┘
                     │             │               │
            ┌────────▼───┐  ┌──────▼──────┐  ┌─────▼───────────┐
            │ Supabase   │  │ Upstash     │  │ Job runner      │
            │ Postgres   │  │ Redis       │  │ (Inngest)       │
            │ Auth, RLS  │  │ rate limits │  │ AI + image jobs │
            │ Storage    │  │ cache       │  └─────┬───────────┘
            └────────────┘  └─────────────┘        │
                                          ┌────────▼─────────┐
                                          │ LLM providers     │
                                          │ Stock/Image APIs  │
                                          └──────────────────┘
        Stripe/Razorpay ──webhooks──▶ /api/webhooks/billing
```

## 4. Repository layout (monorepo)
```
lyncis/
├─ apps/
│  └─ web/                    # Next.js app
│     ├─ app/
│     │  ├─ (marketing)/      # landing, pricing, legal
│     │  ├─ (auth)/           # login, signup, callback
│     │  ├─ (app)/            # dashboard, generate, editor, settings
│     │  ├─ (tenant)/_sites/  # published-site renderer (host-based rewrite)
│     │  └─ api/              # route handlers, webhooks
│     ├─ components/          # ui/, marketing/, editor/
│     ├─ lib/                 # supabase, ai, billing, rate-limit, utils
│     └─ middleware.ts        # host routing, auth gate, security headers
├─ packages/
│  ├─ site-schema/            # Zod schemas + TS types for Site DSL
│  ├─ blocks/                 # React block renderers (shared by editor + tenant)
│  ├─ ai/                     # prompts, pipeline, provider adapters, evals
│  ├─ config/                 # eslint, tsconfig, tailwind preset
│  └─ ui/                     # design tokens + shared primitives
├─ supabase/                  # migrations, seed, RLS tests
├─ docs/                      # this documentation set
└─ .github/workflows/
```

## 5. Site DSL (contract between AI, editor, and renderer)
```ts
// packages/site-schema/src/index.ts
import { z } from "zod";

export const Id = z.string().min(1).max(40);
const Text = (max: number) => z.string().trim().min(1).max(max);

export const AssetRef = z.object({
  assetId: Id.optional(),
  url: z.string().url().max(500),       // must be our CDN or an allow-listed stock host
  alt: Text(140),
  width: z.number().int().positive().optional(),
  height: z.number().int().positive().optional(),
});

export const Theme = z.object({
  palette: z.enum(["lime-night", "ocean", "sunset", "mono", "forest", "violet"]),
  tokens: z.object({                    // optional overrides, contrast-checked server side
    primary: z.string().regex(/^#[0-9a-fA-F]{6}$/),
    background: z.string().regex(/^#[0-9a-fA-F]{6}$/),
    foreground: z.string().regex(/^#[0-9a-fA-F]{6}$/),
  }).partial(),
  fontPair: z.enum(["inter", "sora-inter", "playfair-inter", "space-inter"]),
  radius: z.enum(["none", "sm", "md", "lg", "full"]),
  density: z.enum(["compact", "comfortable", "spacious"]),
});

const Link = z.object({ label: Text(30), href: z.string().max(300) }); // validated: https, mailto, tel, #anchor, or internal slug

const base = { id: Id, hidden: z.boolean().default(false) };

export const Section = z.discriminatedUnion("type", [
  z.object({ ...base, type: z.literal("navbar"),   brand: Text(30), links: z.array(Link).max(6), cta: Link.optional() }),
  z.object({ ...base, type: z.literal("hero"),     eyebrow: Text(40).optional(), headline: Text(90), subheadline: Text(220),
             primaryCta: Link, secondaryCta: Link.optional(), image: AssetRef.optional(), layout: z.enum(["split", "centered"]) }),
  z.object({ ...base, type: z.literal("stats"),    items: z.array(z.object({ value: Text(12), label: Text(30) })).min(2).max(4) }),
  z.object({ ...base, type: z.literal("steps"),    title: Text(80), items: z.array(z.object({ title: Text(40), body: Text(140) })).min(3).max(5) }),
  z.object({ ...base, type: z.literal("features"), title: Text(80), subtitle: Text(160).optional(),
             items: z.array(z.object({ icon: Text(30), title: Text(40), body: Text(160) })).min(3).max(9) }),
  z.object({ ...base, type: z.literal("showcase"), title: Text(80), items: z.array(z.object({ label: Text(30), image: AssetRef, href: z.string().max(300).optional() })).min(2).max(8) }),
  z.object({ ...base, type: z.literal("pricing"),  title: Text(80), plans: z.array(z.object({ name: Text(20), price: Text(12), period: Text(12), features: z.array(Text(60)).max(8), cta: Link, highlight: z.boolean().default(false) })).min(1).max(4) }),
  z.object({ ...base, type: z.literal("testimonials"), items: z.array(z.object({ quote: Text(220), name: Text(40), role: Text(50).optional() })).min(1).max(6) }),
  z.object({ ...base, type: z.literal("faq"),      items: z.array(z.object({ q: Text(120), a: Text(400) })).min(2).max(10) }),
  z.object({ ...base, type: z.literal("contact"),  title: Text(80), fields: z.array(z.enum(["name", "email", "message", "phone"])).min(1) }),
  z.object({ ...base, type: z.literal("cta"),      headline: Text(90), body: Text(160).optional(), button: Link }),
  z.object({ ...base, type: z.literal("footer"),   columns: z.array(z.object({ title: Text(24), links: z.array(Link).max(6) })).max(4), legal: Text(120) }),
]);

export const Page = z.object({ id: Id, slug: z.string().regex(/^[a-z0-9-]{0,40}$/), title: Text(60), sections: z.array(Section).min(1).max(30) });

export const Site = z.object({
  schemaVersion: z.literal(1),
  meta: z.object({ title: Text(70), description: Text(160), lang: z.string().default("en"), ogImage: AssetRef.optional(), favicon: AssetRef.optional() }),
  theme: Theme,
  pages: z.array(Page).min(1).max(10),
});
export type Site = z.infer<typeof Site>;
```
Rules for the DSL:
- Versioned (`schemaVersion`). Every change ships a migration function `migrate(vN → vN+1)`.
- Text fields are plain text; any rich text uses a restricted inline schema (bold, italic, link). No HTML.
- All URLs pass an allow-list validator (https/mailto/tel/anchor/internal only; image hosts allow-listed).
- Max document size 256 KB.

## 6. AI generation pipeline
```
Prompt ─▶ [0 Moderate] ─▶ [1 Intent] ─▶ [2 Layout plan] ─▶ [3 Section copy ×N parallel]
                                                          ─▶ [4 Theme pick] ─▶ [5 Images]
                                                          ─▶ [6 Assemble + validate] ─▶ persist version
```
| Stage | Model tier | Output | Validation |
|---|---|---|---|
| 0 Moderate | Moderation API / small model | allow / block + reason | Block list for disallowed categories |
| 1 Intent | Small | `{businessType, audience, tone, goals, language}` | Zod |
| 2 Layout plan | Small | Ordered list of section types with purpose | Must include navbar, hero, footer; max 12 sections |
| 3 Copy | Medium/large | One Section JSON per call, parallel (concurrency 4) | Zod per section; one automatic repair retry |
| 4 Theme | Rule-based + small model | Palette, font pair, radius | Contrast ≥ 4.5:1 enforced in code |
| 5 Images | API search + optional gen | `AssetRef` with alt text | Host allow-list, size caps |
| 6 Assemble | Code | Full `Site` | Full Zod parse, link and URL validator, size limit |

Rules:
- Use provider structured-output / JSON-schema mode where available; always re-validate with Zod.
- Treat user prompt as **data**: wrap in delimiters, never let it override system instructions (see prompt-injection controls in `05-SECURITY.md`).
- Stream stage events to the client via SSE: `plan`, `section`, `theme`, `image`, `done`, `error`. Partial results are persisted so a failure keeps completed sections.
- Provider failover order configurable per stage; circuit breaker after 3 consecutive failures for 60s.
- Every generation row stores: prompt hash, model, token counts, cost estimate, latency per stage, outcome.
- Offline eval set (≥ 50 prompts) runs in CI nightly: schema pass rate, banned-content rate, average latency, cost.

## 7. Data model (Postgres)
```sql
-- profiles & workspaces
create table profiles (
  id uuid primary key references auth.users on delete cascade,
  display_name text, avatar_url text, created_at timestamptz default now()
);
create table workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null, owner_id uuid not null references profiles(id),
  plan text not null default 'free' check (plan in ('free','pro','business')),
  created_at timestamptz default now()
);
create table workspace_members (
  workspace_id uuid references workspaces(id) on delete cascade,
  user_id uuid references profiles(id) on delete cascade,
  role text not null check (role in ('owner','admin','editor','viewer')),
  primary key (workspace_id, user_id)
);

-- sites & versions
create table sites (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  name text not null, slug text not null unique check (slug ~ '^[a-z0-9-]{3,40}$'),
  status text not null default 'draft' check (status in ('draft','published','suspended','archived')),
  current_version_id uuid, published_version_id uuid,
  created_by uuid references profiles(id), created_at timestamptz default now(), updated_at timestamptz default now()
);
create table site_versions (
  id uuid primary key default gen_random_uuid(),
  site_id uuid not null references sites(id) on delete cascade,
  number int not null, content jsonb not null, schema_version int not null,
  source text not null check (source in ('generation','edit','restore','publish')),
  created_by uuid references profiles(id), created_at timestamptz default now(),
  unique (site_id, number)
);
create table domains (
  id uuid primary key default gen_random_uuid(),
  site_id uuid not null references sites(id) on delete cascade,
  hostname text not null unique, status text not null default 'pending'
    check (status in ('pending','verified','active','failed','removed')),
  verification_token text not null, verified_at timestamptz, created_at timestamptz default now()
);

-- assets
create table assets (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  storage_path text not null, mime text not null, bytes int not null,
  width int, height int, alt text, created_at timestamptz default now()
);

-- AI usage
create table generations (
  id uuid primary key default gen_random_uuid(),
  site_id uuid references sites(id) on delete set null,
  workspace_id uuid not null references workspaces(id) on delete cascade,
  user_id uuid not null references profiles(id),
  kind text not null check (kind in ('full','section','copy')),
  status text not null check (status in ('queued','running','succeeded','partial','failed','blocked')),
  prompt_hash text not null, model text, input_tokens int, output_tokens int,
  cost_usd numeric(10,5), latency_ms int, error_code text, created_at timestamptz default now()
);
create table usage_counters (
  workspace_id uuid references workspaces(id) on delete cascade,
  day date not null, generations int not null default 0,
  primary key (workspace_id, day)
);

-- billing
create table subscriptions (
  workspace_id uuid primary key references workspaces(id) on delete cascade,
  provider text not null, provider_customer_id text, provider_subscription_id text,
  plan text not null, status text not null, current_period_end timestamptz,
  cancel_at_period_end boolean default false, updated_at timestamptz default now()
);
create table billing_events (   -- idempotency for webhooks
  provider_event_id text primary key, type text not null, received_at timestamptz default now(), processed_at timestamptz
);

-- trust & safety, audit
create table abuse_reports (
  id uuid primary key default gen_random_uuid(), site_id uuid references sites(id),
  reason text not null, details text, reporter_email text, status text default 'open', created_at timestamptz default now()
);
create table audit_log (
  id bigint generated always as identity primary key, actor_id uuid, workspace_id uuid,
  action text not null, target_type text, target_id text, meta jsonb, ip inet, created_at timestamptz default now()
);

create index on sites (workspace_id);
create index on site_versions (site_id, number desc);
create index on generations (workspace_id, created_at desc);
create index on domains (site_id);
```
RLS rules:
- Every table has RLS enabled. Default deny.
- Access is by workspace membership. Writes require `editor` or above; billing and member management require `admin`/`owner`.
- Published-site reads go through a server-side tenant resolver using the service role on a narrow function, never via client keys.
- Service-role key is server-only. RLS policies have automated tests (`supabase/tests`).

## 8. API surface
All route handlers validate input with Zod and return `{ data }` or `{ error: { code, message } }`.
| Method | Route | Purpose | Auth |
|---|---|---|---|
| POST | `/api/generate` | Start generation, returns `generationId` | user |
| GET | `/api/generate/:id/stream` | SSE progress | user |
| POST | `/api/sites/:id/regenerate` | Section or copy regeneration | editor |
| GET/PATCH | `/api/sites/:id` | Read / save draft (with `If-Match` version for optimistic concurrency) | member |
| GET | `/api/sites/:id/versions` | List versions | member |
| POST | `/api/sites/:id/restore` | Restore version | editor |
| POST | `/api/sites/:id/publish` | Publish current version | editor |
| POST | `/api/sites/:id/unpublish` | Take offline | editor |
| POST | `/api/sites/:id/domains` | Add custom domain (plan-gated) | admin |
| POST | `/api/domains/:id/verify` | Re-check DNS | admin |
| POST | `/api/assets/sign` | Signed upload URL (type and size checked) | editor |
| POST | `/api/billing/checkout` | Create checkout session | admin |
| POST | `/api/billing/portal` | Customer portal session | admin |
| POST | `/api/webhooks/billing` | Provider webhooks (signature verified, idempotent) | provider |
| POST | `/api/report-abuse` | Public abuse report (rate limited, captcha) | public |
| POST | `/api/forms/:siteId` | Published-site contact form | public (rate limited) |

Conventions: idempotency keys on POSTs that create resources; cursor pagination; ISO-8601 UTC timestamps; no business logic in the client.

## 9. Rendering and publishing
- **Editor canvas** and **published renderer** use the same `packages/blocks` components, so preview equals production.
- **Publish** creates an immutable `site_versions` row (`source='publish'`), sets `sites.published_version_id`, then calls `revalidateTag("site:<id>")`.
- **Tenant routing:** `middleware.ts` maps `Host` → site. `{slug}.lyncis.site` for subdomains; verified custom hostnames from `domains`. Unknown hosts return a branded 404.
- **Rendering mode (MVP):** Server Components with ISR and tag-based revalidation; published JSON cached at the edge. **Scale option:** pre-render static HTML to object storage + CDN.
- **Published sites live on a separate registrable domain** from the app (for example `lyncis.site` vs `lyncis.app`) so user sites cannot share cookies or origin with the app. Placeholder names.
- Free-plan badge is rendered by the renderer from plan data, not stored in the DSL.
- SEO output: `<title>`, meta description, OG tags, canonical, sitemap.xml, robots.txt, JSON-LD (Organization) per site.

## 10. Custom domains
1. User enters `www.example.com`; we create `domains` row with `verification_token`.
2. Show required DNS records (CNAME to our target; TXT `_lyncis-verify` with token).
3. Background job polls DNS (backoff up to 72h); on success, register hostname with the hosting provider's domains API, which provisions SSL automatically (**VERIFY** provider API).
4. Never serve a hostname until TXT ownership is verified (prevents hostname hijack and dangling DNS takeover).
5. On site deletion or downgrade: remove hostname from provider and mark `removed`.

## 11. Images and assets
- Upload: signed URL, max 8 MB, allow `image/jpeg|png|webp|avif`; reject SVG uploads in v1 (script risk).
- Server-side re-encode with `sharp`: strip EXIF, generate responsive widths (320/640/1024/1600) and WebP/AVIF.
- Serve via CDN with long-lived immutable URLs (content-hash in path).
- Every image must have alt text; AI proposes, user can edit.
- Stock images: store attribution/licensing metadata where the provider requires it.

## 12. Rate limiting and quotas
| Scope | Limit (**ASSUMPTION**, tune with data) |
|---|---|
| Auth endpoints | 10/min/IP |
| `/api/generate` | 3/min/user + plan daily quota |
| Section regenerate | 20/hour/user |
| Asset signing | 30/min/user |
| Public forms | 5/min/IP/site + captcha |
| Abuse reports | 5/hour/IP |
Quota check and increment happen in one atomic DB or Redis operation before the AI call.

## 13. Billing integration
- Checkout hosted by the provider. We never touch card data.
- Webhooks: verify signature, insert into `billing_events` (primary key = provider event id) to dedupe, then update `subscriptions` and `workspaces.plan`.
- Entitlements are computed server-side from `workspaces.plan` through one function `getEntitlements(workspace)`; the client only displays.
- Downgrade: sites above the new limit become `archived` (read-only), custom domains paused. Nothing is deleted for 30 days.
- Reconciliation job runs daily to compare provider state and DB.

## 14. Observability
- Sentry (client + server + source maps), release tags per deploy.
- Structured JSON logs with `requestId`, `userId`, `workspaceId`, `generationId`.
- Metrics: generation latency by stage, schema-failure rate, cost per generation, publish success, webhook failures, queue depth.
- Uptime checks on landing, app login, a sample published site, and the webhook endpoint.
- Alerts: error rate > 2% for 5 min, generation failure > 10%, AI spend > 70% of daily budget, webhook backlog.

## 15. Performance budgets
| Surface | Budget |
|---|---|
| Landing page JS (initial) | ≤ 150 KB gzipped |
| Landing LCP | < 2.5s on mid-range mobile, 4G |
| Editor initial JS | ≤ 350 KB gzipped, lazy-load panels |
| Published site JS | ≤ 60 KB gzipped (mostly static HTML) |
| API p95 (non-AI) | < 300 ms |
| First section streamed | < 15 s p50 |

## 16. Testing strategy
| Layer | Tooling | Scope |
|---|---|---|
| Unit | Vitest | DSL schemas, migrations, quota logic, URL validators |
| Component | Testing Library | Blocks render every variant; a11y checks with axe |
| Integration | Vitest + local Supabase | RLS policies, API handlers, webhook idempotency |
| E2E | Playwright | Signup → generate → edit → publish → view; billing in test mode |
| AI evals | Custom runner | Nightly, thresholds gate prompt changes |
| Visual | Playwright screenshots | Block library at 3 breakpoints |
| Load | k6 | Tenant renderer and generation queue |

## 17. Environment variables
```
# public
NEXT_PUBLIC_APP_URL=
NEXT_PUBLIC_SITES_DOMAIN=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_POSTHOG_KEY=
# server only
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=
LLM_PROVIDER_PRIMARY=            # e.g. gemini
GEMINI_API_KEY=
GROQ_API_KEY=
ANTHROPIC_API_KEY=
AI_DAILY_BUDGET_USD=
STOCK_IMAGES_API_KEY=
BILLING_SECRET_KEY=
BILLING_WEBHOOK_SECRET=
RESEND_API_KEY=
SENTRY_DSN=
HOSTING_API_TOKEN=               # domains API
TURNSTILE_SECRET_KEY=            # or hCaptcha
```
Validate at boot with a Zod `env.ts`; the app must fail fast on a missing variable.

## 18. Architecture decision records (initial)
| ADR | Decision | Reason |
|---|---|---|
| 001 | JSON DSL instead of AI-written HTML | Safety, editability, consistency |
| 002 | Monorepo with shared `blocks` | Editor preview equals production |
| 003 | Separate domain for published sites | Origin isolation |
| 004 | Postgres + RLS as the authorization layer | Defense in depth with app checks |
| 005 | SSE for generation streaming | Simple, proxy-friendly, one-way |
| 006 | Immutable versions | Rollback, audit, safe publish |
