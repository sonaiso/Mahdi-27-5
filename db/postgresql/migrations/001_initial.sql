-- ============================================================================
-- Arabic Engine — Migration 001: Initial Schema
-- الترحيل 001: المخطط الأولي
--
-- This migration creates all initial tables for the Arabic Engine.
-- Apply with: psql -d arabic_engine -f 001_initial.sql
-- ============================================================================

BEGIN;

-- Create all tables from schema.sql
\i ../schema.sql

-- Apply seed data
\i ../seed.sql

COMMIT;
