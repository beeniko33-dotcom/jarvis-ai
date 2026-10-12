# Production Readiness – Jarvis AI

## Phase 1 – Foundation

- [x] `.gitignore` covers secrets, DBs, logs, build artifacts
- [x] Committed `risk.db` removed
- [x] README describing components
- [x] Multi-service `docker-compose.yml` present (app, risk, db, redis, traefik, grafana)
- [x] Requirements pinned for core stack

## Phase 2 – Next level (before any public/production deployment)

### Critical

1. **Change all default passwords** in `docker-compose.yml`:
   - `DB_PASSWORD` (default `jarvispass` is only for local experiments)
   - `JWT_SECRET_KEY`
   - `GRAFANA_PASSWORD`
2. Use a real secret manager or host env files that are never committed.
3. Confirm TLS / Traefik ACME email and domains match your real infrastructure.
4. Bind ports carefully (compose already prefers `127.0.0.1` for several services).

### Operational checklist

| Item | Notes |
|------|-------|
| Secrets via environment | Required |
| Database migrations | Use Alembic (`alembic.ini` present) |
| Healthchecks | Defined for app, risk, db, redis |
| Restart policy | `unless-stopped` |
| Logging | Prefer structured logs (loguru is in requirements) |
| Backups | Plan for Postgres + Redis volumes |

### Local vs production

- Local: `docker compose up` with strong random passwords in a private `.env`.
- Production: replace default secrets, lock down Traefik dashboard, and restrict network exposure.

Treat this stack as **infrastructure for an experimental system**. Do not run real-money trading logic until the trading signal side has been paper-validated independently.
