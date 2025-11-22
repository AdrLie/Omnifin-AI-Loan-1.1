# Omnifin Database Schema Design

## Database Architecture

Omnifin uses a dual-database architecture:
1. **Primary Database (PostgreSQL)**: User management, authentication, orders, analytics
2. **Knowledge Bank (PostgreSQL)**: AI training data, prompts, group-specific knowledge

## Primary Database Schema

### 1. Users & Authentication

#### users_user
```sql
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    role VARCHAR(20) DEFAULT 'simple', -- simple, super, admin, superadmin
    group_id INTEGER REFERENCES groups_group(id),
    created_by_id INTEGER REFERENCES users_user(id),
    profile_image VARCHAR(500),
    metadata JSONB DEFAULT '{}'
);
```

#### groups_group
```sql
CREATE TABLE groups_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users_user(id),
    is_active BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}'
);
```

#### auth_userpermissions
```sql
CREATE TABLE auth_userpermissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id) ON DELETE CASCADE,
    permission VARCHAR(100) NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by_id INTEGER REFERENCES users_user(id),
    UNIQUE(user_id, permission)
);
```

### 2. User Activity & Logs

#### analytics_useractivity
```sql
CREATE TABLE analytics_useractivity (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);
```

#### analytics_session
```sql
CREATE TABLE analytics_session (
    id SERIAL PRIMARY KEY,
    session_key VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users_user(id),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 3. Orders & Conversations

#### orders_order
```sql
CREATE TABLE orders_order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id) NOT NULL,
    order_type VARCHAR(20) NOT NULL, -- loan, insurance
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, cancelled
    priority VARCHAR(10) DEFAULT 'medium', -- low, medium, high, urgent
    conversation_id INTEGER REFERENCES orders_conversation(id),
    assigned_to_id INTEGER REFERENCES users_user(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);
```

#### orders_conversation
```sql
CREATE TABLE orders_conversation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id) NOT NULL,
    conversation_type VARCHAR(10) NOT NULL, -- chat, voice
    status VARCHAR(20) DEFAULT 'active', -- active, ended, transferred
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration INTEGER, -- in seconds
    metadata JSONB DEFAULT '{}'
);
```

#### orders_message
```sql
CREATE TABLE orders_message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES orders_conversation(id) NOT NULL,
    sender_type VARCHAR(10) NOT NULL, -- user, ai, agent
    sender_id INTEGER,
    message_type VARCHAR(10) DEFAULT 'text', -- text, image, audio, file
    content TEXT NOT NULL,
    file_url VARCHAR(500),
    file_size INTEGER,
    file_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);
```

### 4. Analytics & Reporting

#### analytics_metric
```sql
CREATE TABLE analytics_metric (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    value NUMERIC NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    period VARCHAR(20) DEFAULT 'daily', -- hourly, daily, weekly, monthly
    metadata JSONB DEFAULT '{}'
);
```

#### analytics_userengagement
```sql
CREATE TABLE analytics_userengagement (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id),
    session_duration INTEGER, -- in seconds
    page_views INTEGER DEFAULT 0,
    conversations_count INTEGER DEFAULT 0,
    orders_created INTEGER DEFAULT 0,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. API Configuration

#### core_apiconfiguration
```sql
CREATE TABLE core_apiconfiguration (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    api_type VARCHAR(50) NOT NULL, -- llm_text, llm_voice, crm, erp
    provider VARCHAR(50) NOT NULL, -- openai, anthropic, elevenlabs, etc.
    endpoint_url VARCHAR(500),
    api_key_encrypted TEXT,
    configuration JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_by_id INTEGER REFERENCES users_user(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    group_id INTEGER REFERENCES groups_group(id)
);
```

#### core_systemsetting
```sql
CREATE TABLE core_systemsetting (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Knowledge Bank Schema

### 1. Knowledge Management

#### knowledge_knowledgeentry
```sql
CREATE TABLE knowledge_knowledgeentry (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    tags TEXT[],
    group_id INTEGER REFERENCES groups_group(id),
    created_by_id INTEGER REFERENCES users_user(id),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);
```

#### knowledge_knowledgeversion
```sql
CREATE TABLE knowledge_knowledgeversion (
    id SERIAL PRIMARY KEY,
    knowledge_entry_id INTEGER REFERENCES knowledge_knowledgeentry(id),
    version INTEGER NOT NULL,
    title VARCHAR(200),
    content TEXT,
    change_summary TEXT,
    created_by_id INTEGER REFERENCES users_user(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Prompt Management

#### prompts_prompt
```sql
CREATE TABLE prompts_prompt (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    prompt_type VARCHAR(20) NOT NULL, -- system, user, assistant
    content TEXT NOT NULL,
    variables TEXT[],
    group_id INTEGER REFERENCES groups_group(id),
    created_by_id INTEGER REFERENCES users_user(id),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### prompts_promptversion
```sql
CREATE TABLE prompts_promptversion (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER REFERENCES prompts_prompt(id),
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,
    created_by_id INTEGER REFERENCES users_user(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. AI Training Data

#### knowledge_trainingdata
```sql
CREATE TABLE knowledge_trainingdata (
    id SERIAL PRIMARY KEY,
    data_type VARCHAR(50) NOT NULL, -- conversation, faq, document
    input_text TEXT NOT NULL,
    expected_output TEXT,
    intent VARCHAR(100),
    entities JSONB DEFAULT '{}',
    confidence_score NUMERIC,
    group_id INTEGER REFERENCES groups_group(id),
    is_used_for_training BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP,
    validated_by_id INTEGER REFERENCES users_user(id)
);
```

## Indexes

### Performance Indexes
```sql
-- User indexespython3 backend/manage.py migrate --database=knowledge
CREATE INDEX idx_users_user_email ON users_user(email);
CREATE INDEX idx_users_user_group ON users_user(group_id);
CREATE INDEX idx_users_user_role ON users_user(role);

-- Activity indexes
CREATE INDEX idx_analytics_activity_user ON analytics_useractivity(user_id);
CREATE INDEX idx_analytics_activity_created ON analytics_useractivity(created_at);

-- Order indexes
CREATE INDEX idx_orders_user ON orders_order(user_id);
CREATE INDEX idx_orders_status ON orders_order(status);
CREATE INDEX idx_orders_created ON orders_order(created_at);

-- Message indexes
CREATE INDEX idx_messages_conversation ON orders_message(conversation_id);
CREATE INDEX idx_messages_created ON orders_message(created_at);

-- Knowledge indexes
CREATE INDEX idx_knowledge_group ON knowledge_knowledgeentry(group_id);
CREATE INDEX idx_knowledge_category ON knowledge_knowledgeentry(category);
CREATE INDEX idx_knowledge_created ON knowledge_knowledgeentry(created_at);

-- Prompt indexes
CREATE INDEX idx_prompts_group ON prompts_prompt(group_id);
CREATE INDEX idx_prompts_category ON prompts_prompt(category);
```

## Database Views

### Analytics Views
```sql
-- User activity summary
CREATE VIEW analytics_user_activity_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.role,
    COUNT(a.id) as total_activities,
    MAX(a.created_at) as last_activity,
    COUNT(DISTINCT DATE(a.created_at)) as active_days
FROM users_user u
LEFT JOIN analytics_useractivity a ON u.id = a.user_id
GROUP BY u.id, u.username, u.role;

-- Order statistics
CREATE VIEW analytics_order_statistics AS
SELECT 
    DATE(created_at) as date,
    order_type,
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/3600) as avg_completion_hours
FROM orders_order
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at), order_type, status;
```

## Database Triggers

### Automatic Timestamps
```sql
-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users_user 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders_order 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Version Control Triggers
```sql
-- Knowledge entry version control
CREATE OR REPLACE FUNCTION create_knowledge_version()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO knowledge_knowledgeversion (
            knowledge_entry_id, version, title, content, 
            change_summary, created_by_id, created_at
        ) VALUES (
            OLD.id, OLD.version, OLD.title, OLD.content,
            'Automatic version on update', OLD.created_by_id, OLD.updated_at
        );
        NEW.version = OLD.version + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER knowledge_version_control 
    BEFORE UPDATE ON knowledge_knowledgeentry
    FOR EACH ROW EXECUTE FUNCTION create_knowledge_version();
```

## Database Setup Scripts

### Create Databases
```bash
# Create databases
createdb omnifin_primary
createdb omnifin_knowledge

# Create users
CREATE USER omnifin_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE omnifin_primary TO omnifin_user;
GRANT ALL PRIVILEGES ON DATABASE omnifin_knowledge TO omnifin_user;
```

### Migration Strategy
1. Use Django migrations for schema management
2. Version control for all database changes
3. Backup strategy before migrations
4. Rollback procedures documented
5. Staging environment testing required