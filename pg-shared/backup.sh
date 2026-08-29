#!/usr/bin/env bash
# Daily PostgreSQL backup → DigitalOcean Spaces
# Run via cron on the Droplet: 0 3 * * * /home/deploy/ecosystem-infra/pg-shared/backup.sh >> /home/deploy/ecosystem-infra/pg-shared/logs/backup.log 2>&1
# Backs up whichever app's DB is passed via DB_NAME (defaults to options_journal) —
# invoke once per app in cron, each with its own DB_USER/DB_NAME override, to back
# up multiple apps on the shared pg-shared instance.

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
CONTAINER="${DB_CONTAINER:-pg-shared}"   # shared Postgres container (was standalone options-journal-db)
DB_USER="${DB_USER:-options}"
DB_NAME="${DB_NAME:-options_journal}"
SPACES_BUCKET="${SPACES_BUCKET:-}"          # set in environment or .env
SPACES_REGION="${SPACES_REGION:-atl1}"
RETAIN_DAYS=30

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="/tmp/${DB_NAME}_backup_${TIMESTAMP}.sql.gz"

# ── Result logging ────────────────────────────────────────────────────────────
# Writes one row to backup_log so the app's daily integrity sweep (5:30am CT,
# well after this 3am run) can notice a failure or a cron that stopped running
# altogether and alert admins — this script has no notification channel of its
# own. Best-effort: a logging failure must never mask this run's real exit code
# or crash the script (the DB/container may itself be the thing that's down).
# NOTE: assumes a `backup_log` table exists in the target DB_NAME's schema —
# apps without one simply get no logging here (silent no-op, not a failure).
log_backup_result() {
  local status="$1" message="$2"
  local escaped
  escaped=$(printf '%s' "$message" | head -c 500 | sed "s/'/''/g")
  docker exec "${CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" -c \
    "INSERT INTO backup_log (status, message) VALUES ('${status}', '${escaped}')" \
    >/dev/null 2>&1 || true
}

on_error() {
  local line="$1" code="$2"
  echo "[$(date)] ERROR: backup.sh failed at line ${line} (exit ${code})"
  log_backup_result "failed" "backup.sh exited at line ${line} (exit ${code})"
}
trap 'on_error ${LINENO} $?' ERR

# ── Validate ──────────────────────────────────────────────────────────────────
if [[ -z "$SPACES_BUCKET" ]]; then
  echo "[$(date)] ERROR: SPACES_BUCKET is not set. Aborting."
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  echo "[$(date)] ERROR: Container '${CONTAINER}' is not running. Aborting."
  exit 1
fi

# ── Dump ──────────────────────────────────────────────────────────────────────
echo "[$(date)] Starting pg_dump → ${BACKUP_FILE}"
docker exec "${CONTAINER}" pg_dump -U "${DB_USER}" "${DB_NAME}" | gzip > "${BACKUP_FILE}"
echo "[$(date)] Dump complete. Size: $(du -sh "${BACKUP_FILE}" | cut -f1)"

# ── Upload to Spaces (S3-compatible) ──────────────────────────────────────────
# Requires AWS CLI configured with Spaces keys:
#   aws configure --profile spaces
#   (endpoint: https://${SPACES_REGION}.digitaloceanspaces.com)
DEST="s3://${SPACES_BUCKET}/backups/$(basename "${BACKUP_FILE}")"
echo "[$(date)] Uploading to ${DEST}"
aws s3 cp "${BACKUP_FILE}" "${DEST}" \
  --endpoint-url "https://${SPACES_REGION}.digitaloceanspaces.com" \
  --profile spaces \
  --no-progress
echo "[$(date)] Upload complete."

# The backup itself succeeded — log it now, then drop the ERR trap. Pruning
# below is best-effort housekeeping; a prune failure (e.g. a stray non-dated
# object in the bucket) must not overwrite today's real success with a false
# "failed" row.
log_backup_result "success" "uploaded $(basename "${BACKUP_FILE}") ($(du -sh "${BACKUP_FILE}" | cut -f1))"
trap - ERR

# ── Prune old backups ─────────────────────────────────────────────────────────
echo "[$(date)] Pruning backups older than ${RETAIN_DAYS} days..."
CUTOFF=$(date -d "-${RETAIN_DAYS} days" +"%Y-%m-%d" 2>/dev/null || date -v-${RETAIN_DAYS}d +"%Y-%m-%d")
aws s3 ls "s3://${SPACES_BUCKET}/backups/" \
  --endpoint-url "https://${SPACES_REGION}.digitaloceanspaces.com" \
  --profile spaces \
  | awk '{print $4}' \
  | while read -r key; do
      # `|| true` — grep exits 1 on no match (e.g. a non-dated object like a
      # stray "backups/" folder placeholder), which under pipefail previously
      # aborted the whole script here even though the real backup had already
      # succeeded. A key with no parseable date is simply never pruned.
      file_date=$( (echo "$key" | grep -oP '\d{4}-\d{2}-\d{2}' | head -1) || true)
      if [[ -n "$file_date" && "$file_date" < "$CUTOFF" ]]; then
        echo "[$(date)] Deleting old backup: $key"
        aws s3 rm "s3://${SPACES_BUCKET}/backups/${key}" \
          --endpoint-url "https://${SPACES_REGION}.digitaloceanspaces.com" \
          --profile spaces
      fi
    done

# ── Cleanup ───────────────────────────────────────────────────────────────────
rm -f "${BACKUP_FILE}"
echo "[$(date)] Backup finished successfully."
