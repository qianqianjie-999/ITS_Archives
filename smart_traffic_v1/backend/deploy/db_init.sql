-- ==============================================
-- 智能交通档案系统 - 数据库初始化脚本
-- 适用环境: Rocky Linux 9.6 + MariaDB
-- ==============================================

-- 1. 创建数据库用户
-- 注意: 请将 'your_password' 替换为实际密码
CREATE USER IF NOT EXISTS 'smart_traffic'@'localhost' IDENTIFIED BY 'your_password';

-- 2. 创建数据库
CREATE DATABASE IF NOT EXISTS smart_traffic 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- 3. 授予用户权限
GRANT ALL PRIVILEGES ON smart_traffic.* TO 'smart_traffic'@'localhost';
FLUSH PRIVILEGES;

-- 4. 使用数据库
USE smart_traffic;

-- 5. 创建表结构
-- 用户表
CREATE TABLE IF NOT EXISTS user (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(100),
  role ENUM('admin', 'editor', 'viewer') NOT NULL DEFAULT 'viewer',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 项目表
CREATE TABLE IF NOT EXISTS project (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  acceptance_date DATE,
  warranty_period VARCHAR(50),
  warranty_expire_date DATE,
  construction_unit VARCHAR(100),
  construction_company VARCHAR(100),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 路口表
CREATE TABLE IF NOT EXISTS intersection (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  type VARCHAR(50),
  traffic_light_warranty_status VARCHAR(20),
  traffic_light_warranty_expire DATE,
  electronic_police_warranty_status VARCHAR(20),
  electronic_police_warranty_expire DATE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 信号灯表
CREATE TABLE IF NOT EXISTS traffic_light (
  id INT AUTO_INCREMENT PRIMARY KEY,
  intersection_id INT NOT NULL,
  project_id INT,
  project_name VARCHAR(100),
  acceptance_date DATE,
  warranty_period VARCHAR(50),
  warranty_expire_date DATE,
  warranty_status VARCHAR(20),
  construction_unit VARCHAR(100),
  construction_company VARCHAR(100),
  signal_type VARCHAR(50),
  signal_count INT DEFAULT 0,
  left_arrow_count INT DEFAULT 0,
  straight_arrow_count INT DEFAULT 0,
  right_arrow_count INT DEFAULT 0,
  full_screen_count INT DEFAULT 0,
  non_motor_count INT DEFAULT 0,
  pedestrian_count INT DEFAULT 0,
  radar_count INT DEFAULT 0,
  guide_screen_count INT DEFAULT 0,
  power_source TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (intersection_id) REFERENCES intersection(id) ON DELETE CASCADE,
  FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 电子警察表
CREATE TABLE IF NOT EXISTS electronic_police (
  id INT AUTO_INCREMENT PRIMARY KEY,
  intersection_id INT NOT NULL,
  project_id INT,
  project_name VARCHAR(100),
  acceptance_date DATE,
  warranty_period VARCHAR(50),
  warranty_expire_date DATE,
  warranty_status VARCHAR(20),
  construction_unit VARCHAR(100),
  construction_company VARCHAR(100),
  capture_type VARCHAR(50),
  terminal_server_count INT DEFAULT 0,
  forward_capture_count INT DEFAULT 0,
  reverse_capture_count INT DEFAULT 0,
  led_light_count INT DEFAULT 0,
  strobe_light_count INT DEFAULT 0,
  ptz_count INT DEFAULT 0,
  signal_detector_count INT DEFAULT 0,
  network_source TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (intersection_id) REFERENCES intersection(id) ON DELETE CASCADE,
  FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 违停抓拍点位表
CREATE TABLE IF NOT EXISTS parking_enforcement_point (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  area VARCHAR(100),
  type VARCHAR(50),
  status VARCHAR(20),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 违停抓拍设备表
CREATE TABLE IF NOT EXISTS parking_enforcement (
  id INT AUTO_INCREMENT PRIMARY KEY,
  point_id INT NOT NULL,
  project_id INT,
  project_name VARCHAR(100),
  acceptance_date DATE,
  warranty_period VARCHAR(50),
  warranty_expire_date DATE,
  warranty_status VARCHAR(20),
  construction_unit VARCHAR(100),
  construction_company VARCHAR(100),
  camera_count INT DEFAULT 0,
  parking_sign_count INT DEFAULT 0,
  monitor_sign_count INT DEFAULT 0,
  power_source TEXT,
  network_source TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (point_id) REFERENCES parking_enforcement_point(id) ON DELETE CASCADE,
  FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 卡口点位表
CREATE TABLE IF NOT EXISTS checkpoint_point (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  area VARCHAR(100),
  type VARCHAR(50),
  status VARCHAR(20),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 卡口设备表
CREATE TABLE IF NOT EXISTS checkpoint (
  id INT AUTO_INCREMENT PRIMARY KEY,
  point_id INT NOT NULL,
  project_id INT,
  project_name VARCHAR(100),
  acceptance_date DATE,
  warranty_period VARCHAR(50),
  warranty_expire_date DATE,
  warranty_status VARCHAR(20),
  construction_unit VARCHAR(100),
  construction_company VARCHAR(100),
  checkpoint_type VARCHAR(50),
  camera_count INT DEFAULT 0,
  strobe_light_count INT DEFAULT 0,
  radar_count INT DEFAULT 0,
  sign_count INT DEFAULT 0,
  power_source TEXT,
  network_source TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (point_id) REFERENCES checkpoint_point(id) ON DELETE CASCADE,
  FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 后端设备表
CREATE TABLE IF NOT EXISTS backend_device (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  type VARCHAR(50),
  project_id INT,
  project_name VARCHAR(100),
  acceptance_date DATE,
  warranty_period VARCHAR(50),
  warranty_expire_date DATE,
  warranty_status VARCHAR(20),
  construction_unit VARCHAR(100),
  construction_company VARCHAR(100),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 质保延期记录表
CREATE TABLE IF NOT EXISTS warranty_extension (
  id INT AUTO_INCREMENT PRIMARY KEY,
  facility_type VARCHAR(50) NOT NULL,
  facility_id INT NOT NULL,
  project_id INT,
  project_name VARCHAR(100),
  warranty_expire_date DATE,
  extension_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 附件表
CREATE TABLE IF NOT EXISTS attachment (
  id INT AUTO_INCREMENT PRIMARY KEY,
  facility_type VARCHAR(50) NOT NULL,
  facility_id INT NOT NULL,
  original_filename VARCHAR(255) NOT NULL,
  stored_filename VARCHAR(255) NOT NULL UNIQUE,
  file_size INT NOT NULL,
  upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 维修记录表
CREATE TABLE IF NOT EXISTS maintenance_record (
  id INT AUTO_INCREMENT PRIMARY KEY,
  facility_type VARCHAR(50) NOT NULL,
  facility_id INT NOT NULL,
  fault_level VARCHAR(20) NOT NULL,
  fault_description TEXT NOT NULL,
  solution TEXT,
  record_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  recorder_id INT NOT NULL,
  FOREIGN KEY (recorder_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 创建初始用户（密码: admin123）
-- 密码使用 werkzeug pbkdf2:sha256 加密
INSERT IGNORE INTO user (username, password_hash, display_name, role) VALUES (
  'admin',
  'pbkdf2:sha256:1000000$kwX24slZb3xs2kAx$08991631f88e9c3dd32ba1549ff4e562002f3354686633e8d4b5def0b5bf5dee',
  '系统管理员',
  'admin'
);

INSERT IGNORE INTO user (username, password_hash, display_name, role) VALUES (
  'editor',
  'pbkdf2:sha256:1000000$kwX24slZb3xs2kAx$08991631f88e9c3dd32ba1549ff4e562002f3354686633e8d4b5def0b5bf5dee',
  '编辑用户',
  'editor'
);

INSERT IGNORE INTO user (username, password_hash, display_name, role) VALUES (
  'viewer',
  'pbkdf2:sha256:1000000$kwX24slZb3xs2kAx$08991631f88e9c3dd32ba1549ff4e562002f3354686633e8d4b5def0b5bf5dee',
  '查看用户',
  'viewer'
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_traffic_light_intersection_id ON traffic_light(intersection_id);
CREATE INDEX IF NOT EXISTS idx_electronic_police_intersection_id ON electronic_police(intersection_id);
CREATE INDEX IF NOT EXISTS idx_parking_enforcement_point_id ON parking_enforcement(point_id);
CREATE INDEX IF NOT EXISTS idx_checkpoint_point_id ON checkpoint(point_id);
CREATE INDEX IF NOT EXISTS idx_warranty_extension_facility ON warranty_extension(facility_type, facility_id);
CREATE INDEX IF NOT EXISTS idx_attachment_facility ON attachment(facility_type, facility_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_record_facility ON maintenance_record(facility_type, facility_id);

-- ==============================================
-- 脚本执行完成
-- ==============================================