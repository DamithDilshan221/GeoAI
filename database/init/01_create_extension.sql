-- Reference only. On this native Windows setup, this statement was already
-- run manually via psql during one-time setup (see docs/architecture Part 0.1).
-- Kept here so a fresh machine can reproduce the same setup by running:
--   psql -U postgres -h localhost -f database/init/01_create_extension.sql

CREATE EXTENSION IF NOT EXISTS postgis;
