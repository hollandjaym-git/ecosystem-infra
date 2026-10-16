-- Read-only role for the weekly security digest. Run ONCE per app database as a superuser, e.g. on the droplet:
--   docker exec -i pg-shared psql -U <superuser> -d options_journal < sql/create_digest_role.sql
--   (and again with -d fitness, -d kitchen, -d peptides)
-- It can only SELECT the handful of tables the digest counts; it cannot see any other table, and the digest also
-- opens every session with default_transaction_read_only=on. No password: pg-shared trusts local socket connections,
-- exactly as backup.sh relies on.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'digest_ro') THEN
    CREATE ROLE digest_ro LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
  END IF;
END $$;

DO $$ BEGIN
  EXECUTE format('GRANT CONNECT ON DATABASE %I TO digest_ro', current_database());
END $$;
GRANT USAGE ON SCHEMA public TO digest_ro;

-- COLUMN-level grants only, so the digest can never read PIN hashes, session tokens, passkey keys or any other secret:
-- it sees account flags, timestamps and ids, plus the token columns solely to test for the "enc:v1:" prefix
-- (those hold ciphertext). Columns that don't exist in a given app are skipped.
DO $$
DECLARE
  spec text[];
  tbl text;
  cols text[];
  present text[];
BEGIN
  FOREACH spec SLICE 1 IN ARRAY ARRAY[
    ARRAY['login_audit', 'email,success,ip_address,attempted_at'],
    ARRAY['app_users', 'id,email,role,is_locked,passkey_only'],
    ARRAY['users', 'id,email,role,is_locked,passkey_only'],
    ARRAY['app_sessions', 'user_id,created_at,expires_at'],
    ARRAY['webauthn_credentials', 'user_id'],
    ARRAY['backup_log', 'status,run_at'],
    ARRAY['strava_accounts', 'access_token,refresh_token'],
    ARRAY['peptides_accounts', 'access_token'],
    ARRAY['kroger_accounts', 'access_token,refresh_token']
  ] LOOP
    tbl := spec[1];
    cols := string_to_array(spec[2], ',');
    SELECT array_agg(column_name::text) INTO present
      FROM information_schema.columns
     WHERE table_schema = 'public' AND table_name = tbl AND column_name = ANY(cols);
    IF present IS NOT NULL THEN
      EXECUTE format('GRANT SELECT (%s) ON public.%I TO digest_ro', (SELECT string_agg(quote_ident(c), ', ') FROM unnest(present) c), tbl);
    END IF;
  END LOOP;
END $$;
-- pg_constraint is readable by everyone; nothing to grant.
