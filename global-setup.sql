-- Run this in Supabase SQL Editor for global shared memory

CREATE TABLE IF NOT EXISTS shared_data (
    id SERIAL PRIMARY KEY,
    data_key VARCHAR(100) UNIQUE NOT NULL,
    data_value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable public access for shared data
ALTER TABLE shared_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations on shared_data" ON shared_data
    FOR ALL USING (true) WITH CHECK (true);
