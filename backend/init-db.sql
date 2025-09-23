-- Initial database setup script
-- This will run when the container starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- The database is automatically created by the postgres container

-- Set timezone
SET timezone = 'UTC';