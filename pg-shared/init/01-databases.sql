-- pg-shared: one Postgres server, an isolated database + owning role per app.
-- Each app connects ONLY to its own DB with its own role. We REVOKE the default
-- PUBLIC CONNECT privilege on each database and grant it back to just the owner,
-- so one app's role cannot even connect to another app's database.
--
-- Passwords here are LOCAL-ONLY placeholders. On the droplet these come from
-- env/secrets (see docker-compose.yml PGSHARED_* / per-app .env), not this file.

-- options-journal ----------------------------------------------------------
CREATE ROLE options LOGIN PASSWORD 'options_local';
CREATE DATABASE options_journal OWNER options;
REVOKE CONNECT ON DATABASE options_journal FROM PUBLIC;
GRANT  CONNECT ON DATABASE options_journal TO options;

-- fitness-tracker -----------------------------------------------------------
CREATE ROLE fitness LOGIN PASSWORD 'fitness_local';
CREATE DATABASE fitness OWNER fitness;
REVOKE CONNECT ON DATABASE fitness FROM PUBLIC;
GRANT  CONNECT ON DATABASE fitness TO fitness;

-- peptides ------------------------------------------------------------------
CREATE ROLE peptides LOGIN PASSWORD 'peptides_local';
CREATE DATABASE peptides OWNER peptides;
REVOKE CONNECT ON DATABASE peptides FROM PUBLIC;
GRANT  CONNECT ON DATABASE peptides TO peptides;

-- gktw ----------------------------------------------------------------------
CREATE ROLE gktw LOGIN PASSWORD 'gktw_local';
CREATE DATABASE gktw OWNER gktw;
REVOKE CONNECT ON DATABASE gktw FROM PUBLIC;
GRANT  CONNECT ON DATABASE gktw TO gktw;
