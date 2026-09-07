-- Reference only. On this native Windows setup, these statements were already
-- run manually via psql during one-time setup (see docs/architecture Part 0.1).
-- Kept here so a fresh machine can reproduce the same setup by running:
--   psql -U postgres -h localhost -f database/init/02_create_test_database.sql

CREATE DATABASE geoai_test;
\c geoai_test
CREATE EXTENSION IF NOT EXISTS postgis;
