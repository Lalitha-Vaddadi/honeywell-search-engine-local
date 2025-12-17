-- Migration: Fix timestamp columns to support timezone-aware datetimes
-- Version: 002
-- Date: 2024-12-17
-- Description: Changes TIMESTAMP WITHOUT TIME ZONE to TIMESTAMP WITH TIME ZONE

-- pdf_metadata table
ALTER TABLE pdf_metadata
    ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE,
    ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

-- users table
ALTER TABLE users
    ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE,
    ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

-- search_history table
ALTER TABLE search_history
    ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

-- Verify
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE column_name IN ('created_at', 'updated_at')
  AND table_name IN ('pdf_metadata', 'users', 'search_history')
ORDER BY table_name, column_name;
