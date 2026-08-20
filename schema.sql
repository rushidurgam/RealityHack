-- ============================================================================
-- SkillBridge AI - PostgreSQL / Supabase Schema
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL DEFAULT 'Demo User',
    email VARCHAR(255),
    target_role VARCHAR(200) DEFAULT '',
    resume_text TEXT DEFAULT '',
    is_sample BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_users_id ON users(id);
CREATE INDEX IF NOT EXISTS ix_users_created_at ON users(created_at);

-- Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    raw_text TEXT DEFAULT '',
    parsed_skills JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_resumes_id ON resumes(id);
CREATE INDEX IF NOT EXISTS ix_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS ix_resumes_created_at ON resumes(created_at);

-- Job Postings table (cache with batch tracking)
CREATE TABLE IF NOT EXISTS job_postings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
    batch_id VARCHAR(64) DEFAULT '',
    role VARCHAR(200) DEFAULT '',
    role_query VARCHAR(200) DEFAULT '',
    location VARCHAR(200) DEFAULT '',
    title VARCHAR(200) NOT NULL,
    company VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    source VARCHAR(50) DEFAULT 'adzuna',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_job_postings_id ON job_postings(id);
CREATE INDEX IF NOT EXISTS ix_job_postings_user_id ON job_postings(user_id);
CREATE INDEX IF NOT EXISTS ix_job_postings_resume_id ON job_postings(resume_id);
CREATE INDEX IF NOT EXISTS ix_job_postings_batch_id ON job_postings(batch_id);
CREATE INDEX IF NOT EXISTS ix_job_postings_created_at ON job_postings(created_at);

-- Skill Gaps table
CREATE TABLE IF NOT EXISTS skill_gaps (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    skill_name VARCHAR(200) NOT NULL,
    reason TEXT DEFAULT '',
    priority_rank INTEGER DEFAULT 1,
    demand_count INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_skill_gaps_id ON skill_gaps(id);
CREATE INDEX IF NOT EXISTS ix_skill_gaps_user_id ON skill_gaps(user_id);
CREATE INDEX IF NOT EXISTS ix_skill_gaps_resume_id ON skill_gaps(resume_id);
CREATE INDEX IF NOT EXISTS ix_skill_gaps_skill_name ON skill_gaps(skill_name);
CREATE INDEX IF NOT EXISTS ix_skill_gaps_created_at ON skill_gaps(created_at);

-- Lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    skill_gap_id INTEGER NOT NULL REFERENCES skill_gaps(id) ON DELETE CASCADE,
    skill_name VARCHAR(200) DEFAULT '',
    theory_markdown TEXT DEFAULT '',
    starter_code TEXT DEFAULT '',
    solution_code TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_lessons_id ON lessons(id);
CREATE INDEX IF NOT EXISTS ix_lessons_skill_gap_id ON lessons(skill_gap_id);
CREATE INDEX IF NOT EXISTS ix_lessons_created_at ON lessons(created_at);

-- Practice Attempts table
CREATE TABLE IF NOT EXISTS practice_attempts (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    submitted_code TEXT DEFAULT '',
    hint TEXT DEFAULT '',
    passed BOOLEAN DEFAULT FALSE,
    score FLOAT DEFAULT 0,
    correctness INTEGER DEFAULT 0,
    code_quality INTEGER DEFAULT 0,
    concept_match INTEGER DEFAULT 0,
    evaluation JSONB DEFAULT '{}'::jsonb,
    evaluation_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_practice_attempts_id ON practice_attempts(id);
CREATE INDEX IF NOT EXISTS ix_practice_attempts_lesson_id ON practice_attempts(lesson_id);
CREATE INDEX IF NOT EXISTS ix_practice_attempts_created_at ON practice_attempts(created_at);

-- Learning Paths table
CREATE TABLE IF NOT EXISTS learning_paths (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL UNIQUE REFERENCES resumes(id) ON DELETE CASCADE,
    items JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_learning_paths_id ON learning_paths(id);
CREATE INDEX IF NOT EXISTS ix_learning_paths_resume_id ON learning_paths(resume_id);

-- Chat Messages table (gap tutor Q&A)
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    skill_gap_id INTEGER NOT NULL REFERENCES skill_gaps(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'user',
    content TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_chat_messages_id ON chat_messages(id);
CREATE INDEX IF NOT EXISTS ix_chat_messages_skill_gap_id ON chat_messages(skill_gap_id);
CREATE INDEX IF NOT EXISTS ix_chat_messages_created_at ON chat_messages(created_at);
