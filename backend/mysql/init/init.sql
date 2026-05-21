-- 初始化数据库脚本
-- 创建知识库文档表
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(64) PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建文档切片表
CREATE TABLE IF NOT EXISTS document_slices (
    id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    chunk_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_document_slices_document_id ON document_slices(document_id);
CREATE INDEX idx_documents_file_name ON documents(file_name);

-- 测试设计模块表结构

-- 需求表
CREATE TABLE IF NOT EXISTS requirements (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    source VARCHAR(50) DEFAULT 'standardization',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_requirements_user_id (user_id),
    INDEX idx_requirements_status (status)
);

-- 拆分需求表
CREATE TABLE IF NOT EXISTS split_requirements (
    id VARCHAR(64) PRIMARY KEY,
    requirement_id VARCHAR(64) NOT NULL,
    text TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    INDEX idx_split_requirements_requirement_id (requirement_id)
);

-- 测试点表
CREATE TABLE IF NOT EXISTS test_points (
    id VARCHAR(64) PRIMARY KEY,
    split_requirement_id VARCHAR(64) NOT NULL,
    text TEXT NOT NULL,
    description TEXT,
    source VARCHAR(10) DEFAULT 'AI',
    marked BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (split_requirement_id) REFERENCES split_requirements(id) ON DELETE CASCADE,
    INDEX idx_test_points_split_requirement_id (split_requirement_id)
);

-- 测试用例表
CREATE TABLE IF NOT EXISTS test_cases (
    id VARCHAR(64) PRIMARY KEY,
    test_point_id VARCHAR(64) NOT NULL,
    text VARCHAR(255) NOT NULL,
    case_property VARCHAR(10) DEFAULT '正例',
    pre_condition TEXT,
    steps JSON,
    source VARCHAR(10) DEFAULT 'AI',
    marked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (test_point_id) REFERENCES test_points(id) ON DELETE CASCADE,
    INDEX idx_test_cases_test_point_id (test_point_id)
);

-- AI会话表
CREATE TABLE IF NOT EXISTS ai_sessions (
    id VARCHAR(64) PRIMARY KEY,
    requirement_id VARCHAR(64) NOT NULL,
    node_id VARCHAR(64) NOT NULL,
    node_type VARCHAR(20) NOT NULL,
    marked_node_ids JSON,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ai_sessions_requirement_id (requirement_id)
);

-- AI消息表
CREATE TABLE IF NOT EXISTS ai_messages (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ai_sessions(id) ON DELETE CASCADE,
    INDEX idx_ai_messages_session_id (session_id)
);

-- 任务表
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(64) PRIMARY KEY,
    requirement_id VARCHAR(64) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    progress INT DEFAULT 0,
    progress_text VARCHAR(255) DEFAULT '',
    use_knowledge_base BOOLEAN DEFAULT FALSE,
    result JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tasks_requirement_id (requirement_id),
    INDEX idx_tasks_status (status)
);
