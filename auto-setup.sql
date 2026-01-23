-- Create this function in Supabase SQL Editor for automated setup

CREATE OR REPLACE FUNCTION setup_tables()
RETURNS void AS $$
BEGIN
    -- Create users table if not exists
    CREATE TABLE IF NOT EXISTS users (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100),
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create feedback table if not exists
    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        title VARCHAR(200) NOT NULL,
        content TEXT NOT NULL,
        category VARCHAR(50),
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        status VARCHAR(20) DEFAULT 'pending',
        admin_response TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Enable RLS
    ALTER TABLE users ENABLE ROW LEVEL SECURITY;
    ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

    -- Insert default admin if not exists
    INSERT INTO users (username, password, email, is_admin) 
    VALUES ('admin', 'admin123', 'admin@example.com', TRUE)
    ON CONFLICT (username) DO NOTHING;
END;
$$ LANGUAGE plpgsql;
