# ecosystem-infra

Shared infrastructure for the **alpinepost.app** ecosystem, hosted on the existing
DigitalOcean droplet (no server move, no IP change). Two shared services front the
otherwise-independent apps (options-journal, fitness-tracker, peptides):

- **`front-caddy/`** — the single ecosystem entrypoint. Owns host `80`/`443`,
  terminates TLS with one wildcard Cloudflare Origin cert, and routes each
  subdomain to that app's frontend over the `edge` network:
  - `app.alpinepost.app` (+ `app.sfoptionsdesk.com` during transition) → options-journal
  - `fitness.alpinepost.app` → fitness-tracker
  - `peptides.alpinepost.app` → peptides
  - apex → redirect to app
- **`pg-shared/`** — one Postgres server with an **isolated database + role per
  app** (`options_journal`, `fitness`, `peptides`). Replaces the three separate
  per-app Postgres containers. Reachable only on the `data` network.

## Networking

Two shared external networks keep the planes separate (and keep the generic
`backend` service alias from colliding across apps):

| Network | Members | Purpose |
|---------|---------|---------|
| `edge`  | front-caddy + each app **frontend** | routing / TLS |
| `data`  | pg-shared + each app **backend**     | database traffic |

Create them once on the host:

```bash
docker network create edge
docker network create data
```

Each app joins these via its own `docker-compose.prod.yml` override (in the app's
repo), which also repoints the backend at `pg-shared` and gates out the app's own
Postgres/Caddy. Local dev is unaffected — the override is only applied in prod:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Before the cutover

- Put the wildcard `*.alpinepost.app` Origin cert in `front-caddy/caddy/` (gitignored).
- Set real per-role passwords: `PGSHARED_SUPER_PASSWORD` here, and
  `PGSHARED_<APP>_PASSWORD` in each app's `.env`. The `pg-shared/init` SQL uses
  local placeholder passwords.
- Migrate existing prod data (options-journal, fitness) into pg-shared; peptides
  starts empty.

See the full runbook for the ordered cutover steps.
