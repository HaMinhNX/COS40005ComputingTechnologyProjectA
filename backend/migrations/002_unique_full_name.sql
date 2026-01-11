-- Migration: Add UNIQUE constraint to full_name in users table
-- This ensures each patient and doctor has a unique name

-- Step 1: First, check and update any duplicate names
-- Add a number suffix to duplicates
WITH duplicates AS (
    SELECT full_name, 
           ROW_NUMBER() OVER (PARTITION BY full_name ORDER BY created_at) as rn
    FROM users
    WHERE full_name IN (
        SELECT full_name 
        FROM users 
        GROUP BY full_name 
        HAVING COUNT(*) > 1
    )
)
UPDATE users u
SET full_name = u.full_name || ' (' || d.rn || ')'
FROM duplicates d
WHERE u.full_name = d.full_name
  AND d.rn > 1;

-- Step 2: Add UNIQUE constraint to full_name column
ALTER TABLE users 
ADD CONSTRAINT users_full_name_unique UNIQUE (full_name);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_full_name ON users(full_name);

COMMENT ON CONSTRAINT users_full_name_unique ON users IS 'Ensures each user has a unique full name';
