-- 初始化数据库脚本
-- 创建知识库文档表
CREATE TABLE `documents` (
  `id` varchar(64) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_path` varchar(512) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_documents_file_name` (`file_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

-- 创建文档切片表

CREATE TABLE `document_slices` (
  `id` varchar(64) NOT NULL,
  `document_id` varchar(64) NOT NULL,
  `content` text NOT NULL,
  `chunk_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_document_slices_document_id` (`document_id`),
  CONSTRAINT `document_slices_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
CREATE INDEX idx_document_slices_document_id ON document_slices(document_id);
CREATE INDEX idx_documents_file_name ON documents(file_name);

-- 测试设计模块表结构

-- 需求表
CREATE TABLE `requirements` (
  `id` varchar(64) NOT NULL,
  `user_id` varchar(64) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text,
  `input_mode` varchar(10) NOT NULL DEFAULT 'text',
  `raw_content` text,
  `file_id` varchar(64) DEFAULT NULL,
  `template_id` varchar(20) DEFAULT 'user-story',
  `standardized_content` text,
  `explore_data` json DEFAULT NULL,
  `quality_score` int DEFAULT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `source` varchar(50) DEFAULT 'standardization',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_requirements_user_id` (`user_id`),
  KEY `idx_requirements_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

-- 拆分需求表
CREATE TABLE `split_requirements` (
  `id` varchar(64) NOT NULL,
  `requirement_id` varchar(64) NOT NULL,
  `text` text NOT NULL,
  `content` text,
  `order_index` int NOT NULL DEFAULT '0',
  `status` varchar(20) DEFAULT 'pending',
  `sort_order` int DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_split_requirements_requirement_id` (`requirement_id`),
  CONSTRAINT `split_requirements_ibfk_1` FOREIGN KEY (`requirement_id`) REFERENCES `requirements` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

-- 测试点表
CREATE TABLE `test_points` (
  `id` varchar(64) NOT NULL,
  `split_requirement_id` varchar(64) NOT NULL,
  `text` text NOT NULL,
  `description` text,
  `source` varchar(10) DEFAULT 'AI',
  `marked` tinyint(1) DEFAULT '0',
  `status` varchar(20) DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_test_points_split_requirement_id` (`split_requirement_id`),
  CONSTRAINT `test_points_ibfk_1` FOREIGN KEY (`split_requirement_id`) REFERENCES `split_requirements` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

-- 测试用例表
CREATE TABLE `test_cases` (
  `id` varchar(64) NOT NULL,
  `test_point_id` varchar(64) NOT NULL,
  `text` varchar(255) NOT NULL,
  `case_property` varchar(10) DEFAULT '正例',
  `pre_condition` text,
  `steps` json DEFAULT NULL,
  `source` varchar(10) DEFAULT 'AI',
  `marked` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_test_cases_test_point_id` (`test_point_id`),
  CONSTRAINT `test_cases_ibfk_1` FOREIGN KEY (`test_point_id`) REFERENCES `test_points` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

-- AI会话表
CREATE TABLE `ai_sessions` (
  `id` varchar(64) NOT NULL,
  `requirement_id` varchar(64) NOT NULL,
  `node_id` varchar(64) NOT NULL,
  `node_type` varchar(20) NOT NULL,
  `marked_node_ids` json DEFAULT NULL,
  `status` varchar(20) DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_ai_sessions_requirement_id` (`requirement_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

-- AI消息表
CREATE TABLE `ai_messages` (
  `id` varchar(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `role` varchar(20) NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_ai_messages_session_id` (`session_id`),
  CONSTRAINT `ai_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `ai_sessions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

-- 任务表
CREATE TABLE `tasks` (
  `id` varchar(64) NOT NULL,
  `requirement_id` varchar(64) NOT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `progress` int DEFAULT '0',
  `progress_text` varchar(255) DEFAULT '',
  `use_knowledge_base` tinyint(1) DEFAULT '0',
  `result` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_tasks_requirement_id` (`requirement_id`),
  KEY `idx_tasks_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `adjust_messages` (
  `id` varchar(64) NOT NULL,
  `requirement_id` varchar(64) NOT NULL,
  `role` varchar(10) NOT NULL,
  `content` text NOT NULL,
  `message_type` varchar(20) DEFAULT NULL,
  `proposal_content` text,
  `change_summary` text,
  `confirmed` tinyint(1) DEFAULT NULL,
  `rejected` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_adjust_messages_requirement_id` (`requirement_id`),
  CONSTRAINT `adjust_messages_ibfk_1` FOREIGN KEY (`requirement_id`) REFERENCES `requirements` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `doc_versions` (
  `id` varchar(64) NOT NULL,
  `requirement_id` varchar(64) NOT NULL,
  `version_number` int NOT NULL,
  `content` text NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_doc_versions_requirement_id` (`requirement_id`),
  CONSTRAINT `doc_versions_ibfk_1` FOREIGN KEY (`requirement_id`) REFERENCES `requirements` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `explore_messages` (
  `id` varchar(64) NOT NULL,
  `requirement_id` varchar(64) NOT NULL,
  `role` varchar(10) NOT NULL,
  `content` text NOT NULL,
  `dimension_key` varchar(50) DEFAULT NULL,
  `dimension_label` varchar(50) DEFAULT NULL,
  `quick_replies` json DEFAULT NULL,
  `replied` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_explore_messages_requirement_id` (`requirement_id`),
  CONSTRAINT `explore_messages_ibfk_1` FOREIGN KEY (`requirement_id`) REFERENCES `requirements` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `uploaded_files` (
  `id` varchar(64) NOT NULL,
  `user_id` varchar(64) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_size` int NOT NULL,
  `file_type` varchar(100) DEFAULT NULL,
  `purpose` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_uploaded_files_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci