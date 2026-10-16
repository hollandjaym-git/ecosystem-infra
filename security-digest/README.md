# Weekly security digest

A **read-only** report sent to Telegram every Monday at 7:00 Central. One Python file (stdlib only), no new
containers, nothing listening. It reads counts and states, never tokens, PINs or raw emails.

## What it checks
| Area | Checks |
|---|---|
| Sign-ins (per app) | ok / failed sign-ins, passkey share, accounts with 5+ failures, failed admin sign-ins |
| Accounts | users, passkeys registered, passkey-only, locked, active sessions |
| Data safety | plaintext third-party tokens (must be 0), token CHECK constraints present and validated, last DB backup age |
| Public site | up, security headers, CORS closed to foreign origins, unauthenticated passkey route returns 401, TLS expiry |
| Containers | running, restart loops |
| Server | disk, memory, pending security updates, reboot required, **only ports 22/80/443 exposed**, SSH failure noise, `.env` modes |
| Fitness CSP | violation reports from the report-only policy (0 for a week = safe to enforce) |
| Code (optional) | Dependabot alerts and PRs, CI state on each default branch |

An AI step (Claude) turns this week's numbers plus the last four snapshots into a short "what changed / what needs
action" summary at the top. It sees only the masked counts above, as data.

## One-time setup (on the droplet, as `deploy`)
1. **Read-only DB role** — once per database, as a Postgres superuser:
   ```bash
   cd /home/deploy/ecosystem-infra/security-digest
   for db in options_journal fitness kitchen peptides; do
     docker exec -i pg-shared psql -U <superuser> -d $db < sql/create_digest_role.sql
   done
   ```
   The role has column-level `SELECT` only (no PIN hashes, no session tokens, no passkey keys) and every digest
   session is also opened `default_transaction_read_only=on`.
2. **Secrets** — `cp .env.example .env && chmod 600 .env`, then fill in `DIGEST_ANTHROPIC_API_KEY` (create a *new* key
   named "security-digest" so its cost is tracked separately) and, optionally, `GITHUB_TOKEN`.
3. **Try it** (prints, sends nothing, writes no state): `python3 digest.py --dry-run`
   then send a real one: `python3 digest.py`.
4. **Schedule** — `crontab -e`:
   ```
   CRON_TZ=America/Chicago
   0 7 * * 1  /usr/bin/python3 /home/deploy/ecosystem-infra/security-digest/digest.py >> /home/deploy/ecosystem-infra/security-digest/digest.log 2>&1
   ```

## Flags
`--dry-run` print only · `--no-ai` skip the summary · `--no-github` skip GitHub · `--config FILE` use another config.

## Failure handling
If the digest itself crashes it sends `⚠️ Security digest FAILED: <error type>` to Telegram. (It cannot report if the
droplet or cron is down; in that case the apps would be down too, which you'd notice.) History lives in `state/`
(last 12 snapshots, metrics only).

## Tuning
Thresholds are in `digest.py` (e.g. `failed >= 30` warns). Add an app by adding a block to `config.json`.
