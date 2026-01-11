-- Week Plans Migration
-- Add support for week-long workout plans

-- Create week_plans table
CREATE TABLE IF NOT EXISTS week_plans (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    patient_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    plan_name VARCHAR(200) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_week_plans_patient ON week_plans(patient_id);
CREATE INDEX IF NOT EXISTS idx_week_plans_doctor ON week_plans(doctor_id);
CREATE INDEX IF NOT EXISTS idx_week_plans_dates ON week_plans(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_week_plans_status ON week_plans(status);

-- Alter assignments table to support week plans
ALTER TABLE assignments 
ADD COLUMN IF NOT EXISTS week_plan_id UUID REFERENCES week_plans(plan_id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS day_of_week INTEGER CHECK (day_of_week BETWEEN 1 AND 7),
ADD COLUMN IF NOT EXISTS sets INTEGER DEFAULT 3 CHECK (sets > 0),
ADD COLUMN IF NOT EXISTS rest_seconds INTEGER DEFAULT 60 CHECK (rest_seconds >= 0),
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Create index for week plan assignments
CREATE INDEX IF NOT EXISTS idx_assignments_week_plan ON assignments(week_plan_id);
CREATE INDEX IF NOT EXISTS idx_assignments_day_of_week ON assignments(day_of_week);

-- Add comments for documentation
COMMENT ON TABLE week_plans IS 'Stores week-long workout plans created by doctors for patients';
COMMENT ON COLUMN week_plans.plan_name IS 'Name of the workout plan';
COMMENT ON COLUMN week_plans.status IS 'Status of the plan: active, completed, or cancelled';
COMMENT ON COLUMN assignments.week_plan_id IS 'Reference to week plan if this assignment is part of a weekly plan';
COMMENT ON COLUMN assignments.day_of_week IS 'Day of week (1=Monday, 7=Sunday) for weekly plans';
COMMENT ON COLUMN assignments.sets IS 'Number of sets for this exercise';
COMMENT ON COLUMN assignments.rest_seconds IS 'Rest time between sets in seconds';
