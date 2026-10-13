# 08 — Deployment

Goal: **$0 recurring cost**, reproducible builds, and a demo that survives bad Wi-Fi.

> **VERIFY:** free-tier limits, sleep behavior and terms for every host below change often. Check each provider's official pricing page before committing.

---

## 1. Environments

| Env | Purpose | Where | Data |
|---|---|---|---|
| **local** | Development | Docker Compose on your machine | Live or replay |
| **demo** | Hackathon presentation | **Local laptop** (primary) + hosted fallback | Replay (golden scenario) |
| **preview** | PR previews | Vercel preview deployments (frontend only) | Replay API |
| **prod** (post-hackathon) | Public instance | Free VM or free container host | Live + replay |

**Demo rule:** the primary demo runs from your laptop with replay mode, with no dependency on the internet except map tiles (cache or use an offline-friendly style). Keep a screen recording as a last-resort backup.

## 2. Hosting Options

| Component | Recommended | Alternative | Notes |
|---|---|---|---|
| Frontend | Vercel (Hobby) | Cloudflare Pages, Netlify | Static + SSR; check Hobby terms for non-commercial use |
| Backend | Always-on free VM (for example Oracle Cloud Always Free) **(VERIFY)** | Fly.io, a home server, a spare laptop | The backend needs a **persistent process** for the AIS WebSocket |
| Not suitable | Free hosts that sleep on inactivity (for example Render free web services) | | Sleeping kills long-lived WebSocket consumers |
| DB | SQLite file on a persistent volume | Supabase/Neon free Postgres if you outgrow SQLite | Back up the file |
| Map tiles/style | An open style with a free tile source **(VERIFY terms and usage limits)** | Self-hosted PMTiles on object storage | Do not hotlink tile servers that forbid heavy use |
| Secrets | Host env vars / GitHub secrets | | Never in the repo |
| DNS/CDN | Cloudflare free | | Optional |

## 3. Container Setup

### 3.1 `docker-compose.yml` (local and VM)

```yaml
services:
  api:
    build: ./apps/api
    env_file: .env
    ports: ["8000:8000"]
    volumes:
      - lyncis-data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 15s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    user: "10001:10001"
    read_only: true
    tmpfs: ["/tmp"]
  web:
    build: ./apps/web
    env_file: .env.web
    ports: ["3000:3000"]
    depends_on: [api]
    restart: unless-stopped
volumes:
  lyncis-data:
```

### 3.2 API Dockerfile (outline)
- Base: `python:3.12-slim`; multi-stage; install deps from a locked file.
- Create a non-root user; copy only the needed files.
- `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
- One worker (the event bus and the AIS connection are in-process). Scale later by splitting ingestion from the API.

## 4. Environment Variables

| Variable | Scope | Example / Notes |
|---|---|---|
| `APP_ENV` | api | `local | demo | prod` |
| `AIS_API_KEY` | api | From AISStream; never exposed to the browser |
| `AIS_BBOX` | api | `[[lat1,lon1],[lat2,lon2]]` |
| `FIRMS_MAP_KEY` | api | NASA FIRMS key |
| `LLM_PROVIDER` | api | `gemini | groq | none` |
| `LLM_API_KEY` | api | Provider key |
| `LLM_TIMEOUT_S` | api | `8` |
| `DATABASE_URL` | api | `sqlite+aiosqlite:////data/lyncis.db` |
| `REPLAY_DIR` | api | `/data/replay` |
| `ADMIN_TOKEN` | api | Long random string; protects control endpoints |
| `CORS_ORIGINS` | api | Comma-separated allowed origins |
| `FEATURE_SHADOWTRACE` | api | `false` by default |
| `FEATURE_AEROTHERMAL` | api | `false` by default |
| `RETENTION_EVENTS_DAYS` | api | `30` |
| `RETENTION_TRACKS_HOURS` | api | `72` |
| `NEXT_PUBLIC_API_URL` | web | Public API base URL |
| `NEXT_PUBLIC_WS_URL` | web | `wss://…/ws/events` |
| `NEXT_PUBLIC_MAP_STYLE_URL` | web | Style JSON URL |

Rules:
- Only `NEXT_PUBLIC_*` values may reach the browser, and they must never be secrets.
- The app fails fast at startup if a required variable is missing or invalid.
- Commit `.env.example`, never `.env`.

## 5. CI/CD (GitHub Actions)

### 5.1 Pipeline

```
PR opened/updated
  ├─ lint (ruff, mypy, eslint, prettier --check)
  ├─ unit tests (pytest, vitest)
  ├─ golden-scenario integration test (replay fixture)
  ├─ dependency audit (pip-audit, npm audit --audit-level=high)
  ├─ secret scan (gitleaks)
  ├─ build (docker build api, next build)
  └─ e2e smoke (Playwright against compose stack, replay mode)

Merge to main
  ├─ same checks
  ├─ deploy web → Vercel (auto)
  └─ deploy api → VM via SSH or registry pull (manual approval)
```

### 5.2 Rules
- `main` is protected; PRs need green CI.
- Pin third-party actions to a commit SHA.
- Use a least-privilege deploy key; rotate it periodically.
- Tag releases `vMAJOR.MINOR.PATCH` and keep a changelog.

## 6. Deployment Procedure (API on a VM)

1. SSH to the VM (key-based; password login disabled).
2. `git pull` or pull the new image.
3. `docker compose up -d --build api`
4. Wait for `/readyz` to return 200.
5. Smoke test: `/healthz`, `/events?limit=1`, open the WS and wait for a heartbeat.
6. Watch logs for 10 minutes for adapter errors.

**Rollback:** `docker compose up -d` with the previous image tag (`api:<prev>`); restore the SQLite backup if a migration ran. Keep the last 3 image tags.

## 7. Migrations
- Use Alembic. Migrations are forward-only and backward-compatible for one release (add columns before using them; remove later).
- Back up the DB file before every deploy: `sqlite3 lyncis.db ".backup /backups/lyncis-$(date +%F-%H%M).db"`.

## 8. TLS and Networking
- Terminate TLS with Caddy or Nginx in front of the API (Caddy gives automatic certificates).
- Open only ports 80/443 externally; the API listens on localhost.
- Enable WebSocket upgrade headers and a long read timeout (≥ 1 hour) in the proxy.
- Firewall: deny by default; allow SSH from your IP if possible.

Example Caddy snippet:

```
api.example.com {
  encode zstd gzip
  reverse_proxy localhost:8000
  header {
    Strict-Transport-Security "max-age=31536000"
    X-Content-Type-Options nosniff
  }
}
```

## 9. Backups and Recovery

| Item | Method | Frequency |
|---|---|---|
| SQLite DB | `.backup` to a separate disk or object storage | Daily |
| Replay files | Keep a copy in the repo (if the terms allow) or in cloud storage | On change |
| Sanctions bulk file | Re-downloadable; store the date and hash | Weekly refresh |
| Config | In Git (without secrets) | Always |

**RTO/RPO targets (hobby tier):** restore within 1 hour; data loss up to 24 hours is acceptable because most data is re-ingestable.

## 10. Monitoring
- Uptime check on `/healthz` (a free external pinger **(VERIFY)**).
- Log shipping optional; at minimum `docker logs` with rotation (`max-size: 10m`, `max-file: 3`).
- Alerts (email or Discord webhook): API down, all sources failing, brief fallback rate above 50% for 15 min, disk above 80%.

## 11. Demo-Day Checklist
- [ ] Laptop charged, charger and a backup HDMI/USB-C adapter packed.
- [ ] `docker compose up` works with the network off (replay mode).
- [ ] Map style cached or a fallback style available.
- [ ] Golden scenario tested twice in the last hour.
- [ ] Screen recording of a full run saved locally.
- [ ] Hosted version live as the second backup.
- [ ] Slides exported to PDF.
- [ ] No notifications or personal tabs visible while presenting.

## 12. Production Launch Checklist
- [ ] Security checklist (SECURITY.md §11) complete.
- [ ] Rate limits and CORS verified on the deployed URL.
- [ ] Source terms re-checked; attribution shown where required.
- [ ] Backups restore-tested once.
- [ ] Runbook written (restart, rollback, rotate keys).
- [ ] Limitations page published.
